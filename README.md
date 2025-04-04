# Test Suite

This project contains a test suite using `pytest-bdd` for behavior-driven development (BDD).

## Project Structure

- `tests/features/`: Contains `.feature` files defining test scenarios.
- `tests/steps/`: Contains step definitions for the scenarios.
- `tests/conftest.py`: Configuration and fixtures for pytest.

## Running the Test Suite

### Using Podman

1. Build the container image:
   ```bash
   podman build -t test-suite .
   ```

2. Run the test suite with a kubeconfig:
   ```bash
   podman run --rm -it -v ~/.kube/config:/root/.kube/config:z -e KUBECONFIG=/root/.kube/config test-suite
   ```

   Add `-k <test_name>` to select a subset of tests.

## Requirements

- Podman
