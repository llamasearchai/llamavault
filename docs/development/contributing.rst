Contributing to LlamaVault
======================

Thank you for your interest in contributing to LlamaVault! This guide will help you get started with contributing to the project.

Development Setup
--------------

1. **Fork the Repository**

   Start by forking the LlamaVault repository on GitHub.

2. **Clone Your Fork**

   .. code-block:: bash

      git clone https://github.com/YOUR-USERNAME/llamavault.git
      cd llamavault

3. **Set Up Development Environment**

   Create a virtual environment and install development dependencies:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -e ".[dev,test,docs]"

4. **Install Pre-commit Hooks**

   We use pre-commit hooks to ensure code quality:

   .. code-block:: bash

      pre-commit install

5. **Create a Feature Branch**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Development Workflow
-----------------

1. **Make Your Changes**

   Implement your feature or bug fix.

2. **Write Tests**

   Add tests for your changes to ensure functionality and prevent regressions.

3. **Run Tests Locally**

   .. code-block:: bash

      pytest

4. **Update Documentation**

   Update relevant documentation to reflect your changes.

5. **Commit Your Changes**

   Follow the commit message guidelines below.

6. **Push Your Changes**

   .. code-block:: bash

      git push origin feature/your-feature-name

7. **Create a Pull Request**

   Open a pull request on GitHub with a clear description of your changes.

Commit Message Guidelines
---------------------

We follow the Conventional Commits specification for commit messages:

.. code-block:: text

    <type>(<scope>): <subject>

    <body>

    <footer>

Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

Example:

.. code-block:: text

    feat(cli): add ability to export credentials by tag

    This change adds a new --tag option to the export command
    allowing users to export only credentials with a specific tag.

    Closes #123

Code Style
--------

We use the following code style guidelines:

- **Python**: Follow PEP 8 and use the Black formatter
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include type hints for all functions and methods
- **Imports**: Sort imports using isort

Testing Guidelines
--------------

- Write unit tests for all new code
- Strive for high test coverage, especially for security-critical code
- Use pytest fixtures for common test setup
- Mock external dependencies and services
- Include both positive and negative test cases

Documentation Guidelines
--------------------

- Update documentation for all new features and changes
- Use clear, concise language
- Include examples for all APIs
- Follow reStructuredText formatting guidelines

Security Considerations
--------------------

Security is a top priority for LlamaVault. When contributing:

- Be mindful of potential security implications of your changes
- Avoid introducing new dependencies without careful consideration
- Never commit sensitive data, even in tests
- Report security issues privately (see below)

Reporting Security Issues
---------------------

If you discover a security issue, please **do not** open a public issue. Instead, send an email to security@llamasearch.ai with details about the issue.

Development Tools
--------------

- **Code Formatting**: Black
- **Import Sorting**: isort
- **Linting**: flake8, pylint
- **Type Checking**: mypy
- **Test Runner**: pytest
- **Documentation**: Sphinx
- **CI/CD**: GitHub Actions

Release Process
------------

1. **Version Bump**

   Update version in `src/llamavault/__init__.py`.

2. **Update Changelog**

   Document all significant changes in `CHANGELOG.md`.

3. **Create a Release PR**

   Submit a pull request with version bump and changelog updates.

4. **Tag Release**

   Once merged, tag the release:

   .. code-block:: bash

      git tag -a v0.x.y -m "Version 0.x.y"
      git push origin v0.x.y

5. **CI/CD**

   Our CI/CD pipeline will automatically build and publish the package to PyPI and create a GitHub release.

Getting Help
----------

If you have questions about contributing, you can:

- Open a discussion on GitHub
- Join our community Discord server
- Email dev@llamasearch.ai

Thank you for contributing to LlamaVault!

Community Guidelines
-----------------

- Be respectful and inclusive in all communications
- Provide constructive feedback
- Help others learn and grow
- Focus on what is best for the community
- Show empathy towards other community members 