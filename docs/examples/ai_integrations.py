#!/usr/bin/env python3
"""
LlamaVault Integrations with AI Libraries and Frameworks

This example demonstrates how to integrate LlamaVault with popular AI libraries and frameworks.
It includes examples for:
- OpenAI
- Anthropic
- Hugging Face Transformers
- LangChain
- Llama Index
"""

import os
import getpass
from typing import Optional, Dict, Any

from llamavault import Vault, CredentialNotFoundError


class LlamaVaultIntegration:
    """Base class for integrating LlamaVault with AI libraries."""
    
    def __init__(self, vault_dir: Optional[str] = None, password: Optional[str] = None):
        """Initialize with a vault or create a new connection."""
        # Get password if not provided
        if password is None:
            password = getpass.getpass("Vault password: ")
            
        # Open the vault
        self.vault = Vault(vault_dir=vault_dir, password=password)
        
    def get_credential(self, name: str, required: bool = True) -> Optional[str]:
        """Get a credential from the vault, with option to make it required."""
        try:
            return self.vault.get_credential(name)
        except CredentialNotFoundError:
            if required:
                raise CredentialNotFoundError(f"Required credential '{name}' not found in vault")
            return None
            
    def setup_environment(self, credential_map: Dict[str, str]):
        """
        Set up environment variables based on a mapping.
        
        Args:
            credential_map: Dict mapping credential names to environment variable names
        """
        for cred_name, env_var in credential_map.items():
            try:
                os.environ[env_var] = self.vault.get_credential(cred_name)
            except CredentialNotFoundError:
                print(f"Warning: Credential '{cred_name}' not found for env var '{env_var}'")
                

class OpenAIIntegration(LlamaVaultIntegration):
    """Integration with OpenAI's API."""
    
    def setup(self, 
              api_key_name: str = "openai_api_key", 
              org_id_name: Optional[str] = "openai_org_id") -> Any:
        """
        Set up OpenAI client using credentials from vault.
        
        Returns:
            Configured OpenAI client
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
            
        # Get API key from vault
        openai.api_key = self.get_credential(api_key_name)
        
        # Get organization ID if provided
        if org_id_name:
            org_id = self.get_credential(org_id_name, required=False)
            if org_id:
                openai.organization = org_id
                
        return openai
        
    def create_client(self, 
                      api_key_name: str = "openai_api_key", 
                      org_id_name: Optional[str] = "openai_org_id") -> Any:
        """
        Create OpenAI client using the v1 client interface.
        
        Returns:
            OpenAI client instance
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai>=1.0.0"
            )
            
        # Get API key from vault
        api_key = self.get_credential(api_key_name)
        
        # Get organization ID if provided
        kwargs = {}
        if org_id_name:
            org_id = self.get_credential(org_id_name, required=False)
            if org_id:
                kwargs["organization"] = org_id
                
        # Create client
        return OpenAI(api_key=api_key, **kwargs)
        
    def example_usage(self):
        """Example of using OpenAI with LlamaVault."""
        # Using the global singleton (deprecated but still common)
        openai = self.setup()
        
        completion = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Hello, I'm using LlamaVault to securely store my API keys.",
            max_tokens=50
        )
        print("OpenAI Response (global):", completion.choices[0].text.strip())
        
        # Using the client interface (recommended)
        client = self.create_client()
        
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "How can I store API keys securely?"}
            ]
        )
        print("OpenAI Response (client):", chat_completion.choices[0].message.content.strip())


class AnthropicIntegration(LlamaVaultIntegration):
    """Integration with Anthropic's API."""
    
    def setup(self, api_key_name: str = "anthropic_api_key") -> Any:
        """
        Set up Anthropic client using credentials from vault.
        
        Returns:
            Configured Anthropic client
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
            
        # Get API key from vault
        api_key = self.get_credential(api_key_name)
        
        # Create and return the client
        return anthropic.Anthropic(api_key=api_key)
        
    def example_usage(self):
        """Example of using Anthropic with LlamaVault."""
        client = self.setup()
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": "What are best practices for credential management in AI applications?"
                }
            ]
        )
        print("Anthropic Response:", message.content[0].text.strip())


class HuggingFaceIntegration(LlamaVaultIntegration):
    """Integration with Hugging Face's API and libraries."""
    
    def setup_api(self, api_key_name: str = "huggingface_api_key") -> None:
        """Set up Hugging Face API with credentials from vault."""
        # Get the API key from vault
        api_key = self.get_credential(api_key_name)
        
        # Set environment variable for HF
        os.environ["HUGGINGFACE_TOKEN"] = api_key
        os.environ["HF_API_TOKEN"] = api_key  # Alternative name used by some libraries
        
    def setup_inference_api(self, api_key_name: str = "huggingface_api_key") -> Any:
        """
        Set up Hugging Face Inference API client.
        
        Returns:
            Hugging Face Inference API client
        """
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "Hugging Face Hub package not installed. Install with: pip install huggingface_hub"
            )
            
        # Get API key from vault
        api_key = self.get_credential(api_key_name)
        
        # Create and return client
        return InferenceClient(token=api_key)
        
    def example_usage(self):
        """Example of using Hugging Face with LlamaVault."""
        # Set up environment variables for transformers
        self.setup_api()
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Now we can access private models because the token is set
            print("Accessing private Hugging Face model...")
            
            # This is a lightweight public model for demonstration
            tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
            print("Successfully loaded tokenizer")
            
            # Inference API example
            client = self.setup_inference_api()
            
            response = client.text_generation(
                prompt="What is LlamaVault?",
                model="gpt2"  # Using a public model for demo
            )
            print("Hugging Face Response:", response)
            
        except ImportError:
            print("Transformers package not installed. Install with: pip install transformers")


class LangChainIntegration(LlamaVaultIntegration):
    """Integration with LangChain framework."""
    
    def setup(self) -> None:
        """Set up environment variables for LangChain."""
        # Define mappings from credential names to environment variables
        env_mapping = {
            "openai_api_key": "OPENAI_API_KEY",
            "anthropic_api_key": "ANTHROPIC_API_KEY",
            "huggingface_api_key": "HUGGINGFACE_API_TOKEN",
            "google_api_key": "GOOGLE_API_KEY",
            "cohere_api_key": "COHERE_API_KEY",
            "serpapi_api_key": "SERPAPI_API_KEY"
        }
        
        # Set up environment variables
        self.setup_environment(env_mapping)
        
    def create_llm(self, provider: str = "openai") -> Any:
        """
        Create an LLM from LangChain using credentials from vault.
        
        Args:
            provider: The LLM provider to use
            
        Returns:
            LangChain LLM instance
        """
        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    api_key=self.get_credential("openai_api_key")
                )
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model_name="claude-3-sonnet-20240229",
                    anthropic_api_key=self.get_credential("anthropic_api_key")
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except ImportError:
            raise ImportError(
                f"LangChain packages not installed. Install with: pip install langchain-{provider}"
            )
            
    def example_usage(self):
        """Example of using LangChain with LlamaVault."""
        # Set up environment variables
        self.setup()
        
        try:
            from langchain.schema import HumanMessage, SystemMessage
            from langchain.prompts import ChatPromptTemplate
            
            # Create LLM
            llm = self.create_llm("openai")
            
            # Simple example
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="What's LlamaVault?")
            ]
            
            response = llm.invoke(messages)
            print("LangChain Response:", response.content)
            
            # Example with prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a credential security assistant."),
                ("human", "What's the best way to store {credential_type}?")
            ])
            
            chain = prompt | llm
            response = chain.invoke({"credential_type": "API keys"})
            print("LangChain Chain Response:", response.content)
            
        except ImportError:
            print("LangChain packages not installed. Install with: pip install langchain langchain-openai")


class LlamaIndexIntegration(LlamaVaultIntegration):
    """Integration with LlamaIndex framework."""
    
    def setup(self) -> None:
        """Set up environment variables for LlamaIndex."""
        # Define mappings from credential names to environment variables
        env_mapping = {
            "openai_api_key": "OPENAI_API_KEY",
            "anthropic_api_key": "ANTHROPIC_API_KEY",
            "pinecone_api_key": "PINECONE_API_KEY",
            "weaviate_api_key": "WEAVIATE_API_KEY"
        }
        
        # Set up environment variables
        self.setup_environment(env_mapping)
        
    def create_llm(self, provider: str = "openai") -> Any:
        """
        Create an LLM for LlamaIndex using credentials from vault.
        
        Args:
            provider: The LLM provider to use
            
        Returns:
            LlamaIndex LLM instance
        """
        try:
            if provider == "openai":
                from llama_index.llms import OpenAI
                return OpenAI(
                    model="gpt-3.5-turbo",
                    api_key=self.get_credential("openai_api_key")
                )
            elif provider == "anthropic":
                from llama_index.llms import Anthropic
                return Anthropic(
                    model="claude-3-sonnet-20240229",
                    api_key=self.get_credential("anthropic_api_key")
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except ImportError:
            raise ImportError(
                "LlamaIndex packages not installed. Install with: pip install llama-index"
            )
            
    def example_usage(self):
        """Example of using LlamaIndex with LlamaVault."""
        # Set up environment variables
        self.setup()
        
        try:
            from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
            
            # Create LLM
            llm = self.create_llm("openai")
            
            # Create a simple document
            documents = [
                Document(text="LlamaVault is a secure credential management system for AI applications.")
            ]
            
            # Create an index
            index = VectorStoreIndex.from_documents(documents, llm=llm)
            
            # Create query engine
            query_engine = index.as_query_engine()
            
            # Query the index
            response = query_engine.query("What is LlamaVault?")
            print("LlamaIndex Response:", response.response)
            
        except ImportError:
            print("LlamaIndex packages not installed. Install with: pip install llama-index")


def demo():
    """Run demonstration of all integrations."""
    print("=" * 50)
    print("LlamaVault AI Integrations Demo")
    print("=" * 50)
    
    # Get vault password
    password = getpass.getpass("Enter vault password (will be used for all demos): ")
    
    # Set up vault with necessary credentials
    vault = Vault(password=password)
    if not (Path.home() / ".llamavault" / "config.json").exists():
        print("Initializing new vault...")
        vault.init()
    
    # Add example credentials if they don't exist
    example_credentials = {
        "openai_api_key": "sk-example12345",
        "anthropic_api_key": "sk-ant-example12345",
        "huggingface_api_key": "hf_example12345",
        "pinecone_api_key": "example12345",
        "cohere_api_key": "example12345",
        "google_api_key": "example12345",
        "serpapi_api_key": "example12345"
    }
    
    for name, value in example_credentials.items():
        try:
            vault.get_credential(name)
            print(f"Using existing credential: {name}")
        except CredentialNotFoundError:
            vault.add_credential(
                name, 
                value,
                metadata={
                    "is_demo": True,
                    "note": "This is a placeholder value for demonstration purposes only."
                }
            )
            print(f"Added example credential: {name}")
    
    # Run demos for each integration
    try:
        print("\n--- OpenAI Integration ---")
        openai_integration = OpenAIIntegration(password=password)
        openai_integration.example_usage()
    except Exception as e:
        print(f"OpenAI demo error: {e}")
    
    try:
        print("\n--- Anthropic Integration ---")
        anthropic_integration = AnthropicIntegration(password=password)
        anthropic_integration.example_usage()
    except Exception as e:
        print(f"Anthropic demo error: {e}")
    
    try:
        print("\n--- Hugging Face Integration ---")
        hf_integration = HuggingFaceIntegration(password=password)
        hf_integration.example_usage()
    except Exception as e:
        print(f"Hugging Face demo error: {e}")
    
    try:
        print("\n--- LangChain Integration ---")
        langchain_integration = LangChainIntegration(password=password)
        langchain_integration.example_usage()
    except Exception as e:
        print(f"LangChain demo error: {e}")
    
    try:
        print("\n--- LlamaIndex Integration ---")
        llamaindex_integration = LlamaIndexIntegration(password=password)
        llamaindex_integration.example_usage()
    except Exception as e:
        print(f"LlamaIndex demo error: {e}")
    
    print("\nDemo complete!")
    print("Note: This demo used placeholder API keys. In a real application, you would")
    print("store your actual API keys securely in the vault.")


if __name__ == "__main__":
    from pathlib import Path
    demo() 