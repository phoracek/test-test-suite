Feature: Pod connectivity

  Scenario: Create a project and a pod in OpenShift
    Given an OpenShift cluster is accessible
    When I create a new project
    And I create a pod in the project
    Then the pod should be running
