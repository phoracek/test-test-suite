FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && \
    apt install -y curl && \
    curl -L -o /usr/bin/virtctl https://github.com/kubevirt/kubevirt/releases/download/v1.5.0/virtctl-v1.5.0-linux-amd64 && \
    chmod +x /usr/bin/virtctl && \
    apt remove curl -y

# Copy the project files
COPY . .

# Default command to run tests
ENTRYPOINT ["pytest", "-v", "--gherkin-terminal-reporter"]
