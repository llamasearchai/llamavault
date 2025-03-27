# LlamaVault: Secure Credential Management

[![PyPI Version](https://img.shields.io/pypi/v/llamavault.svg)](https://pypi.org/project/llamavault/)
[![Build Status](https://github.com/llamasearch/llamavault/actions/workflows/ci.yml/badge.svg)](https://github.com/llamasearch/llamavault/actions/workflows/ci.yml)
[![Docker Image](https://img.shields.io/docker/pulls/llamasearch/llamavault.svg)](https://hub.docker.com/r/llamasearch/llamavault)
[![Documentation Status](https://readthedocs.org/projects/llamavault/badge/?version=latest)](https://llamavault.readthedocs.io/en/latest/?badge=latest)
[![Code Coverage](https://codecov.io/gh/llamasearch/llamavault/branch/main/graph/badge.svg)](https://codecov.io/gh/llamasearch/llamavault)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/llamavault.svg)](https://pypi.org/project/llamavault/)

LlamaVault is a secure credential management system designed specifically for AI and LLM applications. It provides encrypted storage for API keys, access tokens, and other sensitive credentials with both CLI and web interfaces.

![LlamaVault Dashboard](./docs/images/llamavault-dashboard.png)

## ✨ Features

- **🔐 Secure Storage**: AES-256 encryption for all credentials
- **🔑 Key Management**: Easy management of API keys for OpenAI, HuggingFace, Anthropic, and more
- **🔄 Environment Integration**: Seamlessly inject credentials into your environment
- **🌐 Web Interface**: Optional web UI for team credential management
- **🧩 Plugin System**: Extend functionality with custom credential providers
- **🔍 Audit Logging**: Track credential usage and access attempts
- **🔒 Access Control**: Role-based permissions for team environments
- **📊 Usage Analytics**: Track API key usage and costs
- **🖥️ CLI**: Feature-rich command-line interface with colorful output

## 🚀 Installation

### From PyPI

```bash
# Basic installation
pip install llamavault

# With web interface
pip install llamavault[web]

# Development installation
pip install llamavault[dev]
```

### Using Docker

```bash
docker pull llamasearch/llamavault:latest
docker run -p 5000:5000 -v ~/.llamavault:/data llamasearch/llamavault
```

### From Source

```bash
git clone https://github.com/llamasearch/llamavault.git
cd llamavault
pip install -e ".[dev,web]"
```

## 🔧 Quick Start

### CLI Usage

```bash
# Initialize the vault
llamavault init

# Add a new API key
llamavault add openai SK-xxxxxxxxxxxxxxxxxxxx

# List all stored credentials
llamavault list

# Export credentials to .env file
llamavault export .env

# Start the web interface
llamavault web
```

### Python API

```python
from llamavault import Vault

# Create or load a vault
vault = Vault()

# Add credentials
vault.add_credential("openai", "sk-xxxxxxxxxxxx")
vault.add_credential("anthropic", "sk-ant-xxxxxxxxxxxx")

# Retrieve credentials
openai_key = vault.get_credential("openai")

# Use in your application
import openai
openai.api_key = vault.get_credential("openai")
```

### Web Interface

The web interface provides a user-friendly dashboard for managing credentials:

1. Start the web server: `llamavault web`
2. Open http://localhost:5000 in your browser
3. Log in with your credentials
4. Manage your API keys and tokens through the UI

![LlamaVault Web UI](./docs/images/llamavault-web.png)

## 📊 Security Architecture

LlamaVault uses a multi-layered security approach:

1. **Encryption**: AES-256 for all stored credentials
2. **Key Derivation**: PBKDF2 with high iteration count
3. **Authentication**: Argon2 password hashing
4. **Session Security**: CSRF protection, secure cookies
5. **Network Security**: HTTPS for all connections
6. **Data Isolation**: Credential separation by project

## 🔌 Integrations

LlamaVault seamlessly integrates with:

- **AI Frameworks**: OpenAI, Hugging Face, Anthropic, etc.
- **Development Tools**: VS Code, PyCharm, Jupyter
- **CI/CD Systems**: GitHub Actions, GitLab CI, Jenkins
- **Docker**: Container environment variable injection
- **Cloud Platforms**: AWS, Azure, GCP credential management

## 📖 Documentation

Visit our [Documentation Site](https://llamavault.readthedocs.io/) for:

- Complete API reference
- Advanced usage guides
- Tutorial videos
- Best practices for credential management
- Security recommendations

## 🙌 Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](./CONTRIBUTING.md) for details on:

- Code of Conduct
- Development setup
- Testing procedures
- Pull request process

## 📄 License

LlamaVault is released under the MIT License. See the [LICENSE](./LICENSE) file for details. 