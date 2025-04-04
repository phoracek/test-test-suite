from pytest_bdd import given, when, then

@given("I have a configured test environment")
def configured_environment():
    pass

@when("I run the test")
def run_test():
    pass

@then("I should see it pass")
def test_pass():
    assert True
