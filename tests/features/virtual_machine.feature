Feature: VirtualMachine management

  Scenario: Create and start a VirtualMachine in OpenShift
    When I create a new VirtualMachine
    And I start the VirtualMachine
    Then the VirtualMachine should be running
    And it should be possible to connect using console
