from pytest_bdd import given, when, then, scenarios
from kubernetes import client, config

scenarios('../features/kubernetes_api.feature')

@given('a Kubernetes cluster is accessible')
def kubernetes_cluster_accessible():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    # Verify the cluster is accessible by listing namespaces
    v1.list_namespace()

@when('I list the nodes in the cluster')
def list_nodes():
    v1 = client.CoreV1Api()
    global nodes
    nodes = v1.list_node()

@then('I should see at least one node')
def verify_at_least_one_node():
    assert len(nodes.items) > 0, "No nodes found in the cluster"
