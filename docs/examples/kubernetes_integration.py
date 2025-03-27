#!/usr/bin/env python3
"""
Kubernetes Integration Example for LlamaVault
=============================================

This example demonstrates how to use LlamaVault with Kubernetes to:
1. Create Kubernetes Secrets from LlamaVault credentials
2. Generate Kubernetes manifests for different credential types
3. Deploy applications with credentials from LlamaVault
4. Rotate credentials in Kubernetes environments
5. Use LlamaVault in Kubernetes operators and controllers

Requirements:
- kubectl command-line tool
- kubernetes Python package (pip install kubernetes)
- LlamaVault (pip install llamavault)
"""

import os
import base64
import yaml
import tempfile
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from kubernetes import client, config
from llamavault import Vault


class KubernetesVaultIntegration:
    """
    Class for integrating LlamaVault with Kubernetes configurations.
    """

    def __init__(self, vault_password: str, vault_dir: Optional[str] = None, namespace: str = "default"):
        """
        Initialize the Kubernetes integration with LlamaVault.
        
        Args:
            vault_password: Password to unlock the vault
            vault_dir: Optional directory where the vault is stored
            namespace: Kubernetes namespace to use
        """
        self.vault = Vault(password=vault_password, vault_dir=vault_dir)
        self.namespace = namespace
        
        # Try to load kube config from default location
        try:
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.in_cluster = False
        except:
            # Fallback to in-cluster config if running in a pod
            try:
                config.load_incluster_config()
                self.v1 = client.CoreV1Api()
                self.in_cluster = True
            except:
                print("Warning: Could not configure Kubernetes client. "
                      "Commands that require direct API access will not work.")
                self.v1 = None
                self.in_cluster = False

    def create_secret_manifest(self, secret_name: str, credential_names: List[str], 
                              type: str = "Opaque") -> Dict[str, Any]:
        """
        Create a Kubernetes Secret manifest using credentials from the vault.
        
        Args:
            secret_name: Name of the Kubernetes Secret
            credential_names: List of credential names to include in the secret
            type: Kubernetes Secret type (Opaque, kubernetes.io/tls, etc.)
            
        Returns:
            Dictionary containing the Kubernetes Secret manifest
        """
        data = {}
        for cred_name in credential_names:
            cred_value = self.vault.get_credential(cred_name)
            # Base64 encode the credential value for Kubernetes secrets
            data[cred_name] = base64.b64encode(cred_value.encode()).decode()
            
        secret_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": secret_name,
                "namespace": self.namespace,
                "labels": {
                    "managed-by": "llamavault",
                    "created-at": datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                }
            },
            "type": type,
            "data": data
        }
        
        return secret_manifest
    
    def create_tls_secret_manifest(self, secret_name: str, cert_cred_name: str, 
                                  key_cred_name: str) -> Dict[str, Any]:
        """
        Create a TLS Secret manifest from certificate and key credentials.
        
        Args:
            secret_name: Name of the Kubernetes Secret
            cert_cred_name: Name of the certificate credential in the vault
            key_cred_name: Name of the private key credential in the vault
            
        Returns:
            Dictionary containing the Kubernetes TLS Secret manifest
        """
        cert_value = self.vault.get_credential(cert_cred_name)
        key_value = self.vault.get_credential(key_cred_name)
        
        tls_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": secret_name,
                "namespace": self.namespace,
                "labels": {
                    "managed-by": "llamavault",
                    "created-at": datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                }
            },
            "type": "kubernetes.io/tls",
            "data": {
                "tls.crt": base64.b64encode(cert_value.encode()).decode(),
                "tls.key": base64.b64encode(key_value.encode()).decode()
            }
        }
        
        return tls_secret
    
    def create_configmap_manifest(self, name: str, credential_names: List[str]) -> Dict[str, Any]:
        """
        Create a ConfigMap manifest using non-sensitive credentials from the vault.
        
        Args:
            name: Name of the ConfigMap
            credential_names: List of credential names to include
            
        Returns:
            Dictionary containing the Kubernetes ConfigMap manifest
        """
        data = {}
        for cred_name in credential_names:
            data[cred_name] = self.vault.get_credential(cred_name)
            
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "managed-by": "llamavault",
                    "created-at": datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                }
            },
            "data": data
        }
        
        return configmap
    
    def apply_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Apply a Kubernetes manifest using kubectl.
        
        Args:
            manifest: Kubernetes manifest as a dictionary
            
        Returns:
            True if successful, False otherwise
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp:
            yaml.dump(manifest, temp)
            temp_path = temp.name
            
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", temp_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Applied manifest: {result.stdout}")
            os.unlink(temp_path)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error applying manifest: {e.stderr}")
            os.unlink(temp_path)
            return False
    
    def create_secret(self, secret_name: str, credential_names: List[str], 
                     type: str = "Opaque") -> bool:
        """
        Create a Kubernetes Secret using the Kubernetes API.
        
        Args:
            secret_name: Name of the Kubernetes Secret
            credential_names: List of credential names to include in the secret
            type: Kubernetes Secret type
            
        Returns:
            True if successful, False otherwise
        """
        if not self.v1:
            print("Kubernetes client not configured. Cannot create secret directly.")
            return False
            
        data = {}
        for cred_name in credential_names:
            cred_value = self.vault.get_credential(cred_name)
            # For the API, we need bytes, not base64 strings
            data[cred_name] = cred_value.encode()
            
        try:
            self.v1.create_namespaced_secret(
                namespace=self.namespace,
                body=client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    metadata=client.V1ObjectMeta(
                        name=secret_name,
                        namespace=self.namespace,
                        labels={
                            "managed-by": "llamavault",
                            "created-at": datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        }
                    ),
                    type=type,
                    data=data
                )
            )
            print(f"Created secret {secret_name} in namespace {self.namespace}")
            return True
        except Exception as e:
            print(f"Error creating secret: {str(e)}")
            return False
    
    def update_secret(self, secret_name: str, credential_names: List[str]) -> bool:
        """
        Update an existing Kubernetes Secret with new values from the vault.
        
        Args:
            secret_name: Name of the Kubernetes Secret
            credential_names: List of credential names to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.v1:
            print("Kubernetes client not configured. Cannot update secret directly.")
            return False
            
        try:
            # Get the current secret
            secret = self.v1.read_namespaced_secret(
                name=secret_name,
                namespace=self.namespace
            )
            
            # Update the data
            if not secret.data:
                secret.data = {}
                
            for cred_name in credential_names:
                cred_value = self.vault.get_credential(cred_name)
                secret.data[cred_name] = cred_value.encode()
            
            # Update the secret
            self.v1.replace_namespaced_secret(
                name=secret_name,
                namespace=self.namespace,
                body=secret
            )
            
            print(f"Updated secret {secret_name} in namespace {self.namespace}")
            return True
        except Exception as e:
            print(f"Error updating secret: {str(e)}")
            return False
    
    def generate_deployment_with_secrets(self, 
                                        name: str,
                                        image: str,
                                        secret_name: str,
                                        env_from_secrets: Optional[List[str]] = None,
                                        volume_mounts: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a Kubernetes Deployment manifest that references secrets.
        
        Args:
            name: Name of the deployment
            image: Container image to use
            secret_name: Name of the secret to use
            env_from_secrets: List of secrets to mount as environment variables
            volume_mounts: Dictionary mapping mount paths to volume names
            
        Returns:
            Dictionary containing the Kubernetes Deployment manifest
        """
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": name,
                    "managed-by": "llamavault"
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "env": []
                            }
                        ]
                    }
                }
            }
        }
        
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        
        # Add environment variables from secrets
        if env_from_secrets:
            container["envFrom"] = []
            for secret in env_from_secrets:
                container["envFrom"].append({
                    "secretRef": {
                        "name": secret
                    }
                })
        
        # Add volume mounts if specified
        if volume_mounts:
            container["volumeMounts"] = []
            volumes = []
            
            for mount_path, volume_name in volume_mounts.items():
                container["volumeMounts"].append({
                    "name": volume_name,
                    "mountPath": mount_path,
                    "readOnly": True
                })
                
                volumes.append({
                    "name": volume_name,
                    "secret": {
                        "secretName": secret_name
                    }
                })
            
            deployment["spec"]["template"]["spec"]["volumes"] = volumes
        
        return deployment
    
    def rotate_credentials_and_update_secrets(self, 
                                            credential_names: List[str], 
                                            secret_name: str,
                                            rotation_function) -> bool:
        """
        Rotate credentials in the vault and update Kubernetes secrets.
        
        Args:
            credential_names: List of credential names to rotate
            secret_name: Name of the Kubernetes Secret to update
            rotation_function: Function that returns a new value for each credential
            
        Returns:
            True if all operations were successful, False otherwise
        """
        success = True
        
        for cred_name in credential_names:
            # Get the current credential
            cred = self.vault.get_credential_object(cred_name)
            
            # Generate new value
            new_value = rotation_function(cred_name, cred.value)
            
            # Update in the vault
            self.vault.update_credential(
                cred_name, 
                new_value, 
                metadata={
                    **(cred.metadata or {}),
                    "rotated_at": datetime.now().isoformat(),
                    "previous_rotation": cred.updated_at.isoformat() if cred.updated_at else None
                }
            )
            
            print(f"Rotated credential {cred_name} in vault")
        
        # Update the Kubernetes secret
        if not self.update_secret(secret_name, credential_names):
            success = False
        
        return success


def main():
    parser = argparse.ArgumentParser(description="LlamaVault Kubernetes Integration")
    parser.add_argument("--vault-password", help="Vault password")
    parser.add_argument("--vault-dir", help="Vault directory")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--action", required=True, 
                      choices=["create-secret", "update-secret", "generate-manifests", "apply-manifests"],
                      help="Action to perform")
    parser.add_argument("--secret-name", help="Name of the Kubernetes Secret")
    parser.add_argument("--credentials", help="Comma-separated list of credential names")
    parser.add_argument("--output-dir", help="Directory to output generated manifests")
    
    args = parser.parse_args()
    
    if not args.vault_password:
        import getpass
        vault_password = getpass.getpass("Vault password: ")
    else:
        vault_password = args.vault_password
    
    k8s_vault = KubernetesVaultIntegration(
        vault_password=vault_password,
        vault_dir=args.vault_dir,
        namespace=args.namespace
    )
    
    if args.action in ["create-secret", "update-secret", "generate-manifests"] and not args.credentials:
        parser.error("--credentials is required for this action")
    
    credential_names = args.credentials.split(",") if args.credentials else []
    
    if args.action == "create-secret":
        if not args.secret_name:
            parser.error("--secret-name is required for this action")
        k8s_vault.create_secret(args.secret_name, credential_names)
    
    elif args.action == "update-secret":
        if not args.secret_name:
            parser.error("--secret-name is required for this action")
        k8s_vault.update_secret(args.secret_name, credential_names)
    
    elif args.action == "generate-manifests":
        if not args.output_dir:
            parser.error("--output-dir is required for this action")
        if not args.secret_name:
            parser.error("--secret-name is required for this action")
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate secret manifest
        secret_manifest = k8s_vault.create_secret_manifest(args.secret_name, credential_names)
        with open(output_dir / f"{args.secret_name}-secret.yaml", "w") as f:
            yaml.dump(secret_manifest, f)
        
        # Generate deployment manifest
        deployment_manifest = k8s_vault.generate_deployment_with_secrets(
            name=f"{args.secret_name}-app",
            image="your-app-image:latest",
            secret_name=args.secret_name,
            env_from_secrets=[args.secret_name]
        )
        with open(output_dir / f"{args.secret_name}-deployment.yaml", "w") as f:
            yaml.dump(deployment_manifest, f)
            
        print(f"Generated manifests in {output_dir}")
    
    elif args.action == "apply-manifests":
        if not args.output_dir:
            parser.error("--output-dir is required for this action")
        
        output_dir = Path(args.output_dir)
        for yaml_file in output_dir.glob("*.yaml"):
            with open(yaml_file, "r") as f:
                manifest = yaml.safe_load(f)
                k8s_vault.apply_manifest(manifest)
                

if __name__ == "__main__":
    main()


# Example usage:
def example():
    """Example demonstrating how to use the KubernetesVaultIntegration class"""
    # Initialize vault with some example credentials
    vault = Vault(password="secure-password")
    
    # Add some sample credentials if they don't exist
    if "database_password" not in vault.list_credentials():
        vault.add_credential("database_password", "db-password-123")
    if "api_key" not in vault.list_credentials():
        vault.add_credential("api_key", "api-key-456")
    if "app_secret" not in vault.list_credentials():
        vault.add_credential("app_secret", "app-secret-789")
    
    # Initialize the Kubernetes integration
    k8s_vault = KubernetesVaultIntegration(
        vault_password="secure-password",
        namespace="llamavault-demo"
    )
    
    # Create a secret manifest
    secret_manifest = k8s_vault.create_secret_manifest(
        secret_name="app-credentials",
        credential_names=["database_password", "api_key", "app_secret"]
    )
    
    # Print the manifest
    print(yaml.dump(secret_manifest))
    
    # Create a deployment that uses the secret
    deployment = k8s_vault.generate_deployment_with_secrets(
        name="demo-app",
        image="demo-app:latest",
        secret_name="app-credentials",
        env_from_secrets=["app-credentials"]
    )
    
    # Print the deployment manifest
    print(yaml.dump(deployment))
    
    # Example of rotating credentials
    def rotation_function(cred_name, current_value):
        # In a real scenario, this would call an external service or generate a new credential
        return f"new-{current_value}-{datetime.now().strftime('%Y%m%d')}"
    
    # Rotate credentials and update Kubernetes secrets
    k8s_vault.rotate_credentials_and_update_secrets(
        credential_names=["database_password", "api_key"],
        secret_name="app-credentials",
        rotation_function=rotation_function
    )

# Uncomment to run the example
# example() 