Feature: API Connectivity

  Scenario: Verify connection to the OpenShift API
    Given an OpenShift cluster is accessible
    When I query the OpenShift API for its version
    Then I should receive a valid response
