Feature: VirtualMachine management

  Scenario: Create and start a VM in OpenShift
    When I create a new VirtualMachine
    And I start the VirtualMachine
    Then the VirtualMachine should be running
    And it should be possible to connect using console

  Scenario: Verify connectivity between two VMs
    Given Two VirtualMachines connected to the Pod network
    Then there must be connectivity between the two