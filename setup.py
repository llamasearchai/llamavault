#!/usr/bin/env python3
"""
LlamaVault package setup
"""

from setuptools import setup, find_packages
import os
from typing import List

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Define version
VERSION = "0.1.0"

# Define dependencies
REQUIRED = [
    "cryptography>=37.0.0",
    "argparse>=1.4.0",
    "pathlib>=1.0.1",
]

# Optional dependencies
EXTRAS = {
    "ai": [
        "torch>=1.12.0",
        "huggingface_hub>=0.10.0",
        "transformers>=4.20.0",
        "langchain>=0.0.139",
    ],
    "web": [
        "flask>=2.0.0",
        "flask-restful>=0.3.9",
        "flask-cors>=3.0.10",
    ],
    "cloud": [
        "boto3>=1.24.0",
        "google-cloud-storage>=2.4.0",
        "azure-storage-blob>=12.13.0",
    ],
    "all": [],  # Will be populated below
}

# Populate 'all' with all extras
for key, value in EXTRAS.items():
    if key != "all":
        EXTRAS["all"].extend(value)

setup(
    name="llamavault",
    version=VERSION,
    description="Enterprise-grade credential management system with AI-powered configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LlamaSearch AI",
    author_email="info@llamasearch.ai",
    url="https://github.com/llamasearch/llamavault",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "llamavault=llamavault.cli:main",
        ],
    },
    keywords=[
        "api-keys",
        "credentials",
        "security",
        "vault",
        "configuration",
        "llm",
        "ai",
        "machine-learning",
    ],
    project_urls={
        "Documentation": "https://docs.llamavault.ai",
        "Source": "https://github.com/llamasearch/llamavault",
        "Bug Reports": "https://github.com/llamasearch/llamavault/issues",
    },
) 