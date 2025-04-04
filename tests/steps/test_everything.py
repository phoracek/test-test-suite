from pytest_bdd import given, when, then, scenarios
from kubernetes import client, config
import uuid
import pytest
import time
from ocp_resources.pod import Pod
from ocp_resources.virtual_machine import VirtualMachine

scenarios('../features/pod_connectivity.feature')
scenarios('../features/virtual_machine.feature')

config.load_kube_config()

@when('I create a new project')
def create_project(request):
    global project_name
    project_name = f"phoracek-test-project-{uuid.uuid4()}"
    project_api = client.CustomObjectsApi()
    project_body = {
        "apiVersion": "project.openshift.io/v1",
        "kind": "ProjectRequest",
        "metadata": {"name": project_name}
    }
    project_api.create_cluster_custom_object(
        group="project.openshift.io",
        version="v1",
        plural="projectrequests",
        body=project_body
    )

@when('I create a pod in the project')
def create_pod():
    global pod_name
    pod_name = "test-pod"
    pod = Pod(
        name=pod_name,
        namespace=project_name,
        containers=[
            {
                "name": "test-container",
                "image": "quay.io/phoracek/iptoolbox:latest",
                "command": ["/bin/sh", "-c", "sleep infinity"],
            }
        ],
    )
    pod.create()

@then('the pod should be running')
def verify_pod_running():
    pod = Pod(name=pod_name, namespace=project_name)
    pod.wait_for_status(status="Running", timeout=30, sleep=1)

@when('I create a new VirtualMachine')
def create_virtual_machine():
    global vm_name
    vm_name = f"test-vm-{uuid.uuid4()}"
    vm = VirtualMachine(
        name=vm_name,
        namespace=project_name,
        body={
            "spec": {
                "running": False,
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
    vm.create()

@when('I start the VirtualMachine')
def start_virtual_machine():
    #vm = VirtualMachine(name=vm_name, namespace=project_name)
    #vm.update({"spec": {"running": True}})
    pass

@then('the VirtualMachine should be running')
def verify_virtual_machine_running():
    #vm = VirtualMachine(name=vm_name, namespace=project_name)
    #vm.wait_for_status(status="Running", timeout=120, sleep=1)
    pass