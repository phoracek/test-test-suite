from pytest_bdd import given, when, then, scenarios
from kubernetes import client, config
import uuid
import pytest
import time
from ocp_resources.pod import Pod
from ocp_resources.virtual_machine import VirtualMachine
from ocp_resources.project_request import ProjectRequest

scenarios('../features/pod_connectivity.feature')
scenarios('../features/virtual_machine.feature')

config.load_kube_config()

@pytest.fixture
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
    pod_name = "test-pod"
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
    vm_name = "test-vm"
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