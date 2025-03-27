#!/usr/bin/env python3
"""
LlamaVault Docker Integration Examples

This script demonstrates how to use LlamaVault with Docker:
- Creating a Docker image with LlamaVault
- Passing credentials to Docker containers
- Using Docker Compose with LlamaVault
- Environment variable management in containerized applications
"""

import os
import tempfile
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

from llamavault import Vault


def create_dockerfile():
    """Create a sample Dockerfile that uses LlamaVault."""
    dockerfile_content = """FROM python:3.10-slim

# Install LlamaVault
RUN pip install llamavault

# Create a non-root user
RUN useradd -m appuser
USER appuser
WORKDIR /home/appuser

# Copy the vault (if provided)
COPY --chown=appuser:appuser .llamavault /home/appuser/.llamavault

# Copy application code
COPY --chown=appuser:appuser app.py .

# Run with credentials from vault
CMD ["python", "app.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("Created Dockerfile")
    
    app_content = """#!/usr/bin/env python3
import os
import sys
import getpass
from llamavault import Vault, CredentialNotFoundError

def main():
    # Check if vault password is provided as environment variable
    password = os.environ.get("VAULT_PASSWORD")
    if not password:
        print("No vault password provided. Please set VAULT_PASSWORD environment variable.")
        sys.exit(1)
    
    # Open the vault
    try:
        vault = Vault(password=password)
        
        # Get required credentials
        try:
            api_key = vault.get_credential("api_key")
            db_url = vault.get_credential("database_url")
            
            # Print masked credentials (for demo purposes only)
            print(f"API Key: {api_key[:3]}...{api_key[-3:] if len(api_key) > 6 else ''}")
            print(f"Database URL: {db_url[:10]}...{db_url[-5:] if len(db_url) > 15 else ''}")
            
            # In a real app, you would use these credentials
            # E.g., connect to database, initialize API client, etc.
            print("Application running with credentials from vault")
            
        except CredentialNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error opening vault: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open("app.py", "w") as f:
        f.write(app_content)
    print("Created app.py")


def create_docker_compose():
    """Create a sample docker-compose.yml file."""
    compose_content = """version: '3'

services:
  app:
    build: .
    environment:
      - VAULT_PASSWORD=${VAULT_PASSWORD}
    volumes:
      # Mount the vault directory (optional approach)
      - ${HOME}/.llamavault:/home/appuser/.llamavault
  
  # Alternative approach: export credentials to environment variables
  app-env:
    build: .
    env_file:
      - .env
    # No vault mount needed as we're using env vars
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    print("Created docker-compose.yml")


def setup_vault_and_credentials(password: str):
    """Set up a vault with sample credentials for Docker demo."""
    vault = Vault(password=password)
    
    # Initialize if needed
    vault_dir = Path.home() / ".llamavault"
    if not (vault_dir / "config.json").exists():
        vault.init()
        print("Initialized new vault")
    
    # Add sample credentials if they don't exist
    try:
        vault.get_credential("api_key")
    except Exception:
        vault.add_credential(
            "api_key", 
            "sk-example12345abcde",
            metadata={"service": "ExampleAPI", "environment": "docker-demo"}
        )
        print("Added api_key credential")
    
    try:
        vault.get_credential("database_url")
    except Exception:
        vault.add_credential(
            "database_url", 
            "postgresql://user:pass@localhost/db",
            metadata={"service": "PostgreSQL", "environment": "docker-demo"}
        )
        print("Added database_url credential")
    
    return vault


def export_env_for_docker(vault: Vault):
    """Export credentials to .env file for Docker."""
    # Export credentials to .env file
    vault.export_env_file(".env")
    print("Exported credentials to .env file")


def build_and_run_docker_image():
    """Build and run the Docker image."""
    print("\nBuilding Docker image...")
    result = subprocess.run(["docker", "build", "-t", "llamavault-demo", "."], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error building Docker image: {result.stderr}")
        return
    
    print("Docker image built successfully")
    
    print("\nRunning container with mounted vault...")
    result = subprocess.run(
        ["docker", "run", "-e", f"VAULT_PASSWORD={os.environ.get('VAULT_PASSWORD')}", 
         "-v", f"{Path.home()}/.llamavault:/home/appuser/.llamavault", 
         "llamavault-demo"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error running Docker container: {result.stderr}")
    else:
        print("Container output:")
        print(result.stdout)


def run_with_docker_compose():
    """Run the application using Docker Compose."""
    print("\nStarting services with Docker Compose...")
    result = subprocess.run(["docker-compose", "up", "--build"], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running Docker Compose: {result.stderr}")
    else:
        print("Docker Compose output:")
        print(result.stdout)


def cleanup():
    """Clean up files created for the demo."""
    for file in ["Dockerfile", "app.py", "docker-compose.yml", ".env"]:
        if os.path.exists(file):
            os.remove(file)
    print("\nCleaned up demo files")


def manual_build_instructions():
    """Print instructions for manually building and running the Docker container."""
    print("\n=== Manual Docker Build and Run Instructions ===")
    print("""
To build the Docker image:
  docker build -t llamavault-demo .

To run with mounted vault:
  docker run -e VAULT_PASSWORD=your-password \
    -v ~/.llamavault:/home/appuser/.llamavault \
    llamavault-demo

To run with environment variables:
  # First export credentials to .env
  llamavault export .env --password=your-password
  
  # Then run the container with env file
  docker run --env-file .env llamavault-demo

Using Docker Compose:
  # Set vault password in environment
  export VAULT_PASSWORD=your-password
  
  # Run with compose
  docker-compose up
""")


def main():
    """Main function demonstrating Docker integration with LlamaVault."""
    parser = argparse.ArgumentParser(description="LlamaVault Docker Integration Demo")
    parser.add_argument("--password", required=True, help="Password for the vault")
    parser.add_argument("--run", action="store_true", help="Run Docker commands (requires Docker)")
    args = parser.parse_args()
    
    # Set password in environment for Docker
    os.environ["VAULT_PASSWORD"] = args.password
    
    print("=== LlamaVault Docker Integration Demo ===\n")
    
    # Create a temporary directory for the demo
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Setup sample files
        create_dockerfile()
        create_docker_compose()
        
        # Setup vault and credentials
        vault = setup_vault_and_credentials(args.password)
        
        # Export credentials to .env file
        export_env_for_docker(vault)
        
        # If we're set to run Docker commands
        if args.run:
            try:
                build_and_run_docker_image()
                run_with_docker_compose()
            except Exception as e:
                print(f"Error running Docker commands: {e}")
                print("Docker or Docker Compose might not be installed or running.")
        else:
            manual_build_instructions()
        
        # Cleanup
        cleanup()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main() 