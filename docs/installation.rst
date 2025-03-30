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

    git clone https://github.com/holgern/nectarengine.git
    cd nectarengine
    python setup.py build
    
    python setup.py install --user

Run tests after install::

    pytest
