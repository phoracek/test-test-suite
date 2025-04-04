from pytest_bdd import given, when, then, scenarios
from kubernetes import client, config
import uuid
import pytest
import time

scenarios('../features/openshift_api.feature')

@given('an OpenShift cluster is accessible')
def openshift_cluster_accessible():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    # Verify the cluster is accessible by listing namespaces
    v1.list_namespace()

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

    # Register a finalizer to ensure cleanup
    def cleanup_project():
        project_api.delete_cluster_custom_object(
            group="project.openshift.io",
            version="v1",
            plural="projects",
            name=project_name
        )
    request.addfinalizer(cleanup_project)

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