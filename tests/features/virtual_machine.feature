Feature: VirtualMachine management

  Scenario: Create and start a VirtualMachine in OpenShift
    Given an OpenShift cluster is accessible
    When I create a new VirtualMachine
    And I start the VirtualMachine
    Then the VirtualMachine should be running
