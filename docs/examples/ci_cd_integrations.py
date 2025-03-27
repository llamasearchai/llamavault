#!/usr/bin/env python3
"""
LlamaVault Integrations with CI/CD Systems

This example demonstrates how to integrate LlamaVault with various CI/CD platforms:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Azure DevOps

These patterns can help you securely pass credentials to your CI/CD pipelines.
"""

import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from llamavault import Vault


class CIIntegrationBase:
    """Base class for CI/CD integrations."""
    
    def __init__(self, vault_path: Optional[str] = None, password_env: str = "VAULT_PASSWORD"):
        """
        Initialize the CI integration.
        
        Args:
            vault_path: Path to the vault directory (default: ~/.llamavault)
            password_env: Name of the environment variable containing the vault password
        """
        self.vault_path = vault_path
        self.password_env = password_env
        
        # Get password from environment variable
        password = os.environ.get(password_env)
        if not password:
            raise ValueError(
                f"Vault password not found in environment variable {password_env}. "
                "Make sure it's set as a secret in your CI environment."
            )
            
        # Initialize vault
        self.vault = Vault(vault_dir=vault_path, password=password)
        
    def export_env_file(self, path: str = ".env", uppercase: bool = True) -> None:
        """
        Export credentials to a .env file.
        
        Args:
            path: Path to the output file
            uppercase: Whether to convert variable names to uppercase
        """
        self.vault.export_env_file(path, uppercase=uppercase)
        print(f"Exported credentials to {path}")
        
    def get_credential(self, name: str) -> str:
        """
        Get a credential by name.
        
        Args:
            name: Name of the credential
            
        Returns:
            The credential value
        """
        return self.vault.get_credential(name)
        
    def set_environment_variables(self, credentials: Optional[List[str]] = None, 
                                prefix: str = "", uppercase: bool = True) -> None:
        """
        Set environment variables for specified credentials.
        
        Args:
            credentials: List of credential names to export (default: all)
            prefix: Prefix to add to variable names
            uppercase: Whether to convert variable names to uppercase
        """
        if credentials is None:
            # Use all credentials
            credentials = self.vault.list_credentials()
            
        for name in credentials:
            env_name = name.replace("-", "_").replace(" ", "_")
            if prefix:
                env_name = f"{prefix}_{env_name}"
            if uppercase:
                env_name = env_name.upper()
                
            os.environ[env_name] = self.vault.get_credential(name)
            print(f"Set environment variable: {env_name}")


class GitHubActionsIntegration(CIIntegrationBase):
    """Integration for GitHub Actions."""
    
    def set_github_outputs(self, credentials: List[str]) -> None:
        """
        Set GitHub Actions outputs for use in subsequent steps.
        
        Args:
            credentials: List of credential names to set as outputs
        """
        output_file = os.environ.get("GITHUB_OUTPUT")
        if not output_file:
            print("GITHUB_OUTPUT environment variable not found. Not running in GitHub Actions?")
            return
            
        with open(output_file, "a") as f:
            for name in credentials:
                value = self.vault.get_credential(name)
                f.write(f"{name}={value}\n")
                print(f"Set GitHub output: {name}")
                
    def set_github_env(self, credentials: List[str], uppercase: bool = True) -> None:
        """
        Set GitHub Actions environment variables for subsequent steps.
        
        Args:
            credentials: List of credential names to set
            uppercase: Whether to convert variable names to uppercase
        """
        env_file = os.environ.get("GITHUB_ENV")
        if not env_file:
            print("GITHUB_ENV environment variable not found. Not running in GitHub Actions?")
            return
            
        with open(env_file, "a") as f:
            for name in credentials:
                env_name = name.replace("-", "_").replace(" ", "_")
                if uppercase:
                    env_name = env_name.upper()
                    
                value = self.vault.get_credential(name)
                f.write(f"{env_name}={value}\n")
                print(f"Set GitHub environment variable: {env_name}")
                
    def create_github_secrets(self, repo: str, credentials: List[str], 
                            token_name: str = "github_token") -> None:
        """
        Create GitHub repository secrets using the GitHub CLI.
        
        Args:
            repo: Repository name in format owner/repo
            credentials: List of credential names to set as secrets
            token_name: Name of the credential containing the GitHub token
        """
        github_token = self.vault.get_credential(token_name)
        os.environ["GITHUB_TOKEN"] = github_token
        
        for name in credentials:
            value = self.vault.get_credential(name)
            secret_name = name.replace("-", "_").replace(" ", "_").upper()
            
            # Use GitHub CLI to set secret
            result = subprocess.run(
                ["gh", "secret", "set", secret_name, "--repo", repo], 
                input=value.encode(), 
                capture_output=True
            )
            
            if result.returncode == 0:
                print(f"Set GitHub secret: {secret_name}")
            else:
                print(f"Failed to set GitHub secret {secret_name}: {result.stderr.decode()}")


class GitLabCIIntegration(CIIntegrationBase):
    """Integration for GitLab CI."""
    
    def create_gitlab_variables(self, project_id: str, credentials: List[str],
                              token_name: str = "gitlab_token", 
                              masked: bool = True, protected: bool = True) -> None:
        """
        Create GitLab CI/CD variables using the GitLab API.
        
        Args:
            project_id: GitLab project ID
            credentials: List of credential names to set as variables
            token_name: Name of the credential containing the GitLab token
            masked: Whether to mask the variables in job logs
            protected: Whether to protect the variables (only available in protected branches)
        """
        gitlab_token = self.vault.get_credential(token_name)
        
        import requests
        headers = {"PRIVATE-TOKEN": gitlab_token}
        
        for name in credentials:
            value = self.vault.get_credential(name)
            variable_key = name.replace("-", "_").replace(" ", "_").upper()
            
            # Create or update the variable using GitLab API
            url = f"https://gitlab.com/api/v4/projects/{project_id}/variables"
            data = {
                "key": variable_key,
                "value": value,
                "masked": masked,
                "protected": protected
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code in (200, 201):
                print(f"Set GitLab CI/CD variable: {variable_key}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Variable exists, update it
                response = requests.put(
                    f"{url}/{variable_key}", 
                    headers=headers, 
                    data=data
                )
                if response.status_code == 200:
                    print(f"Updated GitLab CI/CD variable: {variable_key}")
                else:
                    print(f"Failed to update GitLab CI/CD variable {variable_key}: {response.text}")
            else:
                print(f"Failed to set GitLab CI/CD variable {variable_key}: {response.text}")


class JenkinsIntegration(CIIntegrationBase):
    """Integration for Jenkins CI."""
    
    def create_jenkins_credentials(self, jenkins_url: str, credentials: List[str],
                                token_name: str = "jenkins_token", 
                                domain: str = "_", folder: Optional[str] = None) -> None:
        """
        Create Jenkins credentials using the Jenkins API.
        
        Args:
            jenkins_url: Jenkins server URL
            credentials: List of credential names to set
            token_name: Name of the credential containing the Jenkins API token
            domain: Jenkins credentials domain
            folder: Jenkins folder path (for folder-scoped credentials)
        """
        jenkins_token = self.vault.get_credential(token_name)
        jenkins_user = self.vault.get_credential("jenkins_user")
        
        import requests
        from requests.auth import HTTPBasicAuth
        
        auth = HTTPBasicAuth(jenkins_user, jenkins_token)
        
        # Get Jenkins CSRF token
        response = requests.get(f"{jenkins_url}/crumbIssuer/api/json", auth=auth)
        if response.status_code != 200:
            print(f"Failed to get Jenkins CSRF token: {response.text}")
            return
            
        crumb_data = response.json()
        headers = {crumb_data.get("crumbRequestField"): crumb_data.get("crumb")}
        
        # Set path for credentials API
        credentials_url = f"{jenkins_url}/credentials/store/system/domain/{domain}/createCredentials"
        if folder:
            credentials_url = f"{jenkins_url}/job/{folder}/credentials/store/folder/domain/{domain}/createCredentials"
        
        for name in credentials:
            value = self.vault.get_credential(name)
            credential_id = name.replace(" ", "_")
            
            # Create Jenkins credential
            xml_data = f"""
            <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
                <scope>GLOBAL</scope>
                <id>{credential_id}</id>
                <description>Added by LlamaVault</description>
                <username>{name}</username>
                <password>{value}</password>
            </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
            """
            
            response = requests.post(
                credentials_url,
                auth=auth,
                headers={**headers, "Content-Type": "application/xml"},
                data=xml_data
            )
            
            if response.status_code == 200:
                print(f"Created Jenkins credential: {credential_id}")
            else:
                print(f"Failed to create Jenkins credential {credential_id}: {response.text}")


class CircleCIIntegration(CIIntegrationBase):
    """Integration for CircleCI."""
    
    def create_circleci_env_vars(self, project_slug: str, credentials: List[str],
                             token_name: str = "circleci_token") -> None:
        """
        Create CircleCI environment variables using the CircleCI API.
        
        Args:
            project_slug: CircleCI project slug (e.g., github/org/repo)
            credentials: List of credential names to set as environment variables
            token_name: Name of the credential containing the CircleCI token
        """
        circleci_token = self.vault.get_credential(token_name)
        
        import requests
        headers = {"Circle-Token": circleci_token, "Content-Type": "application/json"}
        
        for name in credentials:
            value = self.vault.get_credential(name)
            env_name = name.replace("-", "_").replace(" ", "_").upper()
            
            # Create environment variable using CircleCI API
            url = f"https://circleci.com/api/v2/project/{project_slug}/envvar"
            data = {"name": env_name, "value": value}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                print(f"Set CircleCI environment variable: {env_name}")
            else:
                print(f"Failed to set CircleCI environment variable {env_name}: {response.text}")


class AzureDevOpsIntegration(CIIntegrationBase):
    """Integration for Azure DevOps."""
    
    def create_azure_variables(self, org: str, project: str, pipeline_id: str,
                            credentials: List[str], token_name: str = "azure_token",
                            secret: bool = True) -> None:
        """
        Create Azure DevOps pipeline variables using the Azure DevOps API.
        
        Args:
            org: Azure DevOps organization name
            project: Azure DevOps project name
            pipeline_id: Azure DevOps pipeline ID
            credentials: List of credential names to set as variables
            token_name: Name of the credential containing the Azure DevOps PAT
            secret: Whether to mark the variables as secret
        """
        azure_token = self.vault.get_credential(token_name)
        
        import requests
        from requests.auth import HTTPBasicAuth
        
        # Azure DevOps uses Basic auth with empty username and PAT as password
        auth = HTTPBasicAuth("", azure_token)
        headers = {"Content-Type": "application/json"}
        
        # First, get existing variables
        url = f"https://dev.azure.com/{org}/{project}/_apis/build/definitions/{pipeline_id}?api-version=6.0"
        response = requests.get(url, auth=auth)
        
        if response.status_code != 200:
            print(f"Failed to get Azure DevOps pipeline definition: {response.text}")
            return
            
        pipeline_def = response.json()
        variables = pipeline_def.get("variables", {})
        
        # Update variables
        for name in credentials:
            value = self.vault.get_credential(name)
            var_name = name.replace("-", "_").replace(" ", "_").upper()
            
            variables[var_name] = {
                "value": value,
                "isSecret": secret
            }
            
        pipeline_def["variables"] = variables
        
        # Update pipeline definition
        response = requests.put(url, auth=auth, headers=headers, json=pipeline_def)
        
        if response.status_code == 200:
            print(f"Set {len(credentials)} Azure DevOps pipeline variables")
        else:
            print(f"Failed to update Azure DevOps pipeline variables: {response.text}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LlamaVault CI/CD Integration Examples")
    parser.add_argument("--platform", required=True, 
                       choices=["github", "gitlab", "jenkins", "circleci", "azure"],
                       help="CI/CD platform to demonstrate")
    parser.add_argument("--vault-password", required=True,
                       help="Password for the vault")
    parser.add_argument("--credentials", required=True, nargs="+",
                       help="Names of credentials to use")
    return parser.parse_args()


def main():
    """Main function demonstrating CI/CD integrations."""
    args = parse_args()
    
    # Set vault password in environment variable
    os.environ["VAULT_PASSWORD"] = args.vault_password
    
    print(f"=== LlamaVault {args.platform.capitalize()} CI/CD Integration Demo ===\n")
    
    # Create appropriate integration based on platform
    if args.platform == "github":
        integration = GitHubActionsIntegration()
        
        # Export as environment variables
        integration.set_environment_variables(args.credentials)
        
        # If running in GitHub Actions, set outputs and env vars
        if "GITHUB_OUTPUT" in os.environ:
            integration.set_github_outputs(args.credentials)
            integration.set_github_env(args.credentials)
            
        # Example - Export to .env file for use in actions
        integration.export_env_file()
        
    elif args.platform == "gitlab":
        integration = GitLabCIIntegration()
        
        # Export as environment variables
        integration.set_environment_variables(args.credentials)
        
        # Example - Export to .env file for use in GitLab CI
        integration.export_env_file()
        
    elif args.platform == "jenkins":
        integration = JenkinsIntegration()
        
        # Export as environment variables
        integration.set_environment_variables(args.credentials)
        
        # Example - Export to .env file to be loaded in Jenkins
        integration.export_env_file()
        
    elif args.platform == "circleci":
        integration = CircleCIIntegration()
        
        # Export as environment variables
        integration.set_environment_variables(args.credentials)
        
        # Example - Export to .env file to be loaded in CircleCI
        integration.export_env_file()
        
    elif args.platform == "azure":
        integration = AzureDevOpsIntegration()
        
        # Export as environment variables
        integration.set_environment_variables(args.credentials)
        
        # Example - Export to .env file to be loaded in Azure DevOps
        integration.export_env_file()
        
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main() 