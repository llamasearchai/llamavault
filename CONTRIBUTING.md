# Contributing to LlamaVault

Thank you for your interest in contributing to LlamaVault! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

There are many ways to contribute to LlamaVault:

1. **Report bugs**: Submit bug reports on the issue tracker.
2. **Suggest features**: Submit feature requests on the issue tracker.
3. **Submit pull requests**: Contribute code, documentation, or other improvements.
4. **Review pull requests**: Help review and test pull requests from other contributors.
5. **Share and promote**: Help spread the word about LlamaVault!

## Development Setup

To set up your development environment:

1. Fork the repository and clone your fork:

```bash
git clone https://github.com/your-username/llamavault.git
cd llamavault
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:

```bash
pip install -e ".[all]"
```

4. Install development dependencies:

```bash
pip install pytest pytest-cov black flake8 mypy sphinx
```

## Development Workflow

1. **Create a branch**: Create a branch for your changes.

```bash
git checkout -b feature/your-feature-name
```

2. **Make changes**: Implement your changes, following the code style guidelines.

3. **Write tests**: Add or update tests to cover your changes.

4. **Run tests**: Ensure all tests pass.

```bash
pytest
```

5. **Format code**: Format your code using Black.

```bash
black llamavault
```

6. **Check style**: Check your code with flake8.

```bash
flake8 llamavault
```

7. **Check types**: Run type checking with mypy.

```bash
mypy llamavault
```

8. **Commit changes**: Commit your changes with a descriptive message.

```bash
git commit -m "Add feature XYZ"
```

9. **Push changes**: Push your changes to your fork.

```bash
git push origin feature/your-feature-name
```

10. **Submit a pull request**: Open a pull request against the main repository.

## Pull Request Guidelines

- Follow the pull request template when submitting a PR.
- Include tests for any new functionality.
- Update documentation as needed.
- Ensure all tests pass and the code is properly formatted.
- Keep PRs focused on a single topic.
- Be respectful and constructive in discussions.

## Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
- Use [Black](https://black.readthedocs.io/) for code formatting.
- Write docstrings for all modules, classes, and functions.
- Use type hints for function parameters and return values.

## Documentation

- Update relevant documentation when introducing changes.
- Use clear and concise language.
- Include code examples when appropriate.

## Testing

- Write unit tests for all new functionality.
- Ensure existing tests continue to pass.
- Aim for high test coverage, especially for security-critical components.

## Security Considerations

- Never commit sensitive data, API keys, or credentials.
- Report security vulnerabilities privately to the maintainers.
- Follow security best practices in your code.

## License

By contributing to LlamaVault, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 