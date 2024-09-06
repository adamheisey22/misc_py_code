Sphinx Documentation Structure
==============================

Sphinx organizes the documentation into the following sections:

Package Overview
----------------
The documentation starts with a general overview of the main package structure. In this project, the top-level package is `src`. Inside the `src` package, you will find the following main packages:

- **electricity**: Contains modules related to electricity modeling and calculations.
- **hydrogen**: Contains modules for hydrogen energy production, storage, and consumption.
- **residential**: Contains models and utilities related to residential energy use.
- **integrator**: Integrates components from various energy sources (electricity, hydrogen, etc.) into a cohesive system.

Submodules and Subpackages
--------------------------
Each package may contain additional submodules and subpackages, which are organized in the documentation as follows:

- **Package**: Each package (e.g., electricity, hydrogen) is documented with a high-level description of its purpose and contents.
- **Submodules**: The individual Python modules within each package are listed and documented. For example, the `electricity` package may contain submodules like `generation.py`, `transmission.py`, and `distribution.py`. Each of these modules will have its own section.
- **Subpackages**: If a package contains nested subpackages, these are also documented. For instance, if `residential` has a subpackage `appliances`, it will have its own subsection with corresponding submodules.

Each module's docstrings are captured to provide detailed information about functions, classes, methods, and attributes.

Example Structure
-----------------
For the `src` package, Sphinx might organize the contents as follows:

.. code-block:: text

    src/
    │
    ├── electricity/
    │   ├── generation.py
    │   ├── transmission.py
    │   └── distribution.py
    │
    ├── hydrogen/
    │   ├── production.py
    │   └── storage.py
    │
    ├── residential/
    │   ├── appliances/
    │   │   ├── fridge.py
    │   │   └── washer.py
    │   └── hvac.py
    │
    └── integrator/
        ├── main.py
        └── utils.py

In the HTML and Markdown outputs, each package and subpackage is represented with links to the respective modules, making it easy to navigate between different sections of the documentation.
