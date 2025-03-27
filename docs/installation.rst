Installation
============

LlamaVault can be installed in several ways, depending on your needs and preferences.

Installing from PyPI
-------------------

The easiest way to install LlamaVault is using pip:

.. code-block:: bash

    # Basic installation
    pip install llamavault

For the web interface, install with the optional web dependencies:

.. code-block:: bash

    # With web interface
    pip install llamavault[web]

For development, install with the development dependencies:

.. code-block:: bash

    # Development installation
    pip install llamavault[dev]

    # Development with web interface
    pip install llamavault[dev,web]

Using Docker
-----------

LlamaVault is available as a Docker image, which includes the web interface:

.. code-block:: bash

    # Pull the Docker image
    docker pull llamasearch/llamavault:latest

    # Run the container
    docker run -p 5000:5000 -v ~/.llamavault:/data llamasearch/llamavault

This will mount your local ``~/.llamavault`` directory to the container's ``/data`` directory, 
allowing the vault data to persist between container restarts.

Installing from Source
--------------------

To install LlamaVault from source:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/llamasearch/llamavault.git
    cd llamavault

    # Install in development mode
    pip install -e .

    # With web interface
    pip install -e ".[web]"

    # With all development dependencies
    pip install -e ".[dev,web]"

Using make targets:

.. code-block:: bash

    # Install basic dependencies
    make install

    # Install development dependencies
    make dev

    # Install web interface dependencies
    make web

System Requirements
-----------------

LlamaVault requires Python 3.8 or later.

For the web interface, we recommend a modern web browser:

- Chrome/Chromium (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

Operating systems supported:

- Linux
- macOS
- Windows

Verification
-----------

After installation, verify that LlamaVault is correctly installed by running:

.. code-block:: bash

    llamavault --version

This should display the version of LlamaVault installed on your system.

Next Steps
---------

After installation, we recommend:

1. Following the :doc:`quickstart` guide to set up your first vault
2. Learning the :doc:`cli_usage` for everyday use
3. Or exploring the :doc:`web_interface` if you installed with web support 