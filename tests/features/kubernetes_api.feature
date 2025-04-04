Feature: Kubernetes API Connectivity

  Scenario: Verify connection to the Kubernetes API
    Given a Kubernetes cluster is accessible
    When I list the nodes in the cluster
    Then I should see at least one node
