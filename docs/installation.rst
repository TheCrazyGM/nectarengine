Installation
============
The minimal working python version is 3.5.x


Install nectar with pip:

.. code:: bash

    pip install -U nectarengine

Sometimes this does not work. Please try::

    pip3 install -U nectarengine

or::

    python -m pip install nectarengine

Manual installation
-------------------
    
You can install nectar from this repository if you want the latest
but possibly non-compiling version::

    git clone https://github.com/thecrazygm/nectarengine.git
    cd nectarengine
    uv sync   

    uv sync --dev

Run tests after install::

    make test
