# Turnip Test Suite

This project contains a test suite using `pytest-bdd` for behavior-driven development (BDD).

## Project Structure

- `tests/features/`: Contains `.feature` files defining test scenarios.
- `tests/steps/`: Contains step definitions for the scenarios.
- `tests/conftest.py`: Configuration and fixtures for pytest.

## Running the Test Suite

### Using Podman

1. Build the container image:
   ```bash
   podman build -t turnip-test-suite .
   ```

2. Run the test suite with a kubeconfig:
   ```bash
   podman run --rm -it -v /path/to/kubeconfig:/root/.kube/config:ro -e KUBECONFIG=/root/.kube/config turnip-test-suite
   ```

### Without Containers

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests with a kubeconfig:
   ```bash
   KUBECONFIG=/path/to/kubeconfig pytest tests
   ```

## Requirements

- Python 3.10 or higher
- `pytest` and `pytest-bdd`
- Podman (optional, for containerized execution)
