from pytest_bdd import given, when, then, scenarios
from kubernetes import config
import uuid
import pytest
from ocp_resources.pod import Pod
from ocp_resources.virtual_machine import VirtualMachine
from ocp_resources.project_request import ProjectRequest
import logging
import pexpect
from timeout_sampler import TimeoutSampler

LOGGER = logging.getLogger(__name__)

scenarios('../features/pod_connectivity.feature')
scenarios('../features/virtual_machine.feature')

config.load_kube_config()

@pytest.fixture(scope="module")
def project():
    project_name = f"phoracek-test-project-{uuid.uuid4()}"
    project_request = ProjectRequest(name=project_name)
    project_request.create()
    return project_name

@when('I create a new project')
def create_project(project):
    pass

@pytest.fixture
def pod(project):
    pod_name = f"pod-{uuid.uuid4()}"
    return Pod(
        name=pod_name,
        namespace=project,
        containers=[
            {
                "name": "test-container",
                "image": "quay.io/phoracek/iptoolbox:latest",
                "command": ["/bin/sh", "-c", "sleep infinity"],
            }
        ],
    )

@when('I create a pod in the project')
def create_pod(pod):
    pod.create()

@then('the pod should be running')
def verify_pod_running(pod):
    pod.wait_for_status(status="Running", timeout=30)

@pytest.fixture
def virtual_machine(project):
    vm_name = f"vm-{uuid.uuid4()}"
    vm = VirtualMachine(
        name=vm_name,
        namespace=project,
        body={
            "spec": {
                "runStrategy": "Halted",
                "template": {
                    "metadata": {"labels": {"kubevirt.io/domain": vm_name}},
                    "spec": {
                        "domain": {
                            "devices": {"disks": [{"name": "disk0", "disk": {"bus": "virtio"}}]},
                            "resources": {"requests": {"memory": "64Mi"}}
                        },
                        "volumes": [{"name": "disk0", "containerDisk": {"image": "kubevirt/cirros-container-disk-demo"}}]
                    }
                }
            }
        }
    )
    return vm

@when('I create a new VirtualMachine')
def create_virtual_machine(virtual_machine):
    virtual_machine.create()

@when('I start the VirtualMachine')
def start_virtual_machine(virtual_machine):
    virtual_machine.start()

@then('the VirtualMachine should be running')
def verify_virtual_machine_running(virtual_machine):
    virtual_machine.vmi.wait_until_running(timeout=180)

@then('it should be possible to connect using console')
def verify_virtual_machine_console(virtual_machine):
    with Console(vm=virtual_machine) as vmc:
        vmc.sendline('hostname')
        vmc.expect('cirros')

@given('Two VirtualMachines connected to the Pod network', target_fixture="vms")
def given_vms(project):
    body = {
        "spec": {
            "runStrategy": "Always",
            "template": {
                "spec": {
                    "domain": {
                        "devices": {
                            "disks": [{"name": "disk0", "disk": {"bus": "virtio"}}],
                            "interfaces": [{"name": "default", "masquerade": {}}],
                        },
                        "resources": {"requests": {"memory": "64Mi"}},
                    },
                    "networks": [{"name": "default", "pod": {}}],
                    "volumes": [{"name": "disk0", "containerDisk": {"image": "kubevirt/cirros-container-disk-demo"}}]
                }
            }
        }
    }
    vm_a = VirtualMachine(
        name=f"vm-a-{uuid.uuid4()}",
        namespace=project,
        body=body,
    )
    vm_b = VirtualMachine(
        name=f"vm-b-{uuid.uuid4()}",
        namespace=project,
        body=body,
    )
    vm_a.create()
    vm_b.create()
    vm_a.vmi.wait_until_running(timeout=180)
    vm_b.vmi.wait_until_running(timeout=180)
    return vm_a, vm_b

@then('there must be connectivity between the two')
def verify_no_packet_loss(vms):
    vm_a, vm_b = vms

    vm_a_ip = vm_a.vmi.interfaces[0].ipAddress
    vm_b_ip = vm_b.vmi.interfaces[0].ipAddress

    with Console(vm=vm_a) as vm_a_console:
        vm_a_console.sendline(f"ping -c 10 {vm_b_ip}")
        vm_a_console.expect("0% packet loss")

class Console(object):
    def __init__(self, vm):
        self.vm = vm
        self.username = "cirros"
        self.password = "gocubsgo"
        self.timeout = 60
        self.child = None
        self.login_prompt = "login:"
        self.prompt = [r"\$"]
        self.cmd = self._generate_cmd()
        self.base_dir = "/tmp"

    def connect(self):
        LOGGER.info(f"Connect to {self.vm.name} console")
        self.console_eof_sampler(func=pexpect.spawn, command=self.cmd, timeout=self.timeout)

        self._connect()

        return self.child

    def _connect(self):
        self.child.send("\n\n")
        if self.username:
            self.child.expect(self.login_prompt, timeout=5*60)
            LOGGER.info(f"{self.vm.name}: Using username {self.username}")
            self.child.sendline(self.username)
            if self.password:
                self.child.expect("Password:")
                LOGGER.info(f"{self.vm.name}: Using password {self.password}")
                self.child.sendline(self.password)

        self.child.expect(self.prompt, timeout=150)
        LOGGER.info(f"{self.vm.name}: Got prompt {self.prompt}")

    def disconnect(self):
        if self.child.terminated:
            self.console_eof_sampler(func=pexpect.spawn, command=self.cmd, timeout=self.timeout)

        self.child.send("\n\n")
        self.child.expect(self.prompt)
        if self.username:
            self.child.send("exit")
            self.child.send("\n\n")
            self.child.expect("login:")
        self.child.close()

    def console_eof_sampler(self, func, command, timeout):
        sampler = TimeoutSampler(
            wait_timeout=5*60,
            sleep=5,
            func=func,
            exceptions_dict={pexpect.exceptions.EOF: []},
            command=command,
            timeout=timeout,
            encoding="utf-8",
        )
        for sample in sampler:
            if sample:
                self.child = sample
                self.child.logfile = open(f"{self.base_dir}/{self.vm.name}.pexpect.log", "a")
                break

    def _generate_cmd(self):
        virtctl_str = "virtctl"
        cmd = f"{virtctl_str} console {self.vm.name}"
        if self.vm.namespace:
            cmd += f" -n {self.vm.namespace}"
        return cmd

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()