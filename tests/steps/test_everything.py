from pytest_bdd import given, when, then, scenarios
from kubernetes import client, config
import uuid
import pytest
import time

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
    v1 = client.CoreV1Api()
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name="test-pod"),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="test-container",
                    image="quay.io/phoracek/iptoolbox:latest",
                    command=["/bin/sh", "-c", "sleep infinity"],
                )
            ]
        )
    )
    v1.create_namespaced_pod(namespace=project_name, body=pod)

@then('the pod should be running')
def verify_pod_running():
    v1 = client.CoreV1Api()
    for _ in range(30):  # Retry for up to 30 seconds
        pod = v1.read_namespaced_pod(name="test-pod", namespace=project_name)
        if pod.status.phase == "Running":
            break
        time.sleep(1)
    else:
        assert False, f"Pod is not running, current phase: {pod.status.phase}"

@when('I create a new VirtualMachine')
def create_virtual_machine():
    global vm_name
    vm_name = f"test-vm-{uuid.uuid4()}"
    vm_api = client.CustomObjectsApi()
    vm_body = {
        "apiVersion": "kubevirt.io/v1",
        "kind": "VirtualMachine",
        "metadata": {"name": vm_name},
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
    vm_api.create_namespaced_custom_object(
        group="kubevirt.io",
        version="v1",
        namespace=project_name,
        plural="virtualmachines",
        body=vm_body
    )

@when('I start the VirtualMachine')
def start_virtual_machine():
    vm_api = client.CustomObjectsApi()
    vm_api.patch_namespaced_custom_object(
        group="kubevirt.io",
        version="v1",
        namespace=project_name,
        plural="virtualmachines",
        name=vm_name,
        body={"spec": {"running": True}}
    )

@then('the VirtualMachine should be running')
def verify_virtual_machine_running():
    vm_api = client.CustomObjectsApi()
    for _ in range(120):
        vm = vm_api.get_namespaced_custom_object(
            group="kubevirt.io",
            version="v1",
            namespace=project_name,
            plural="virtualmachines",
            name=vm_name
        )
        if vm.get("status", {}).get("ready"):
            break
        time.sleep(1)
    else:
        assert False, f"VirtualMachine is not running, current phase: {vm.get('status', {}).get('phase')}"