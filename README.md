# :beers: GuangyuPeng's Shell Script Repo

1. [Overview](#Overview)
2. [Modules](#Modules)

    * [Initialization](#Initialization)
    * [System Management](#SystemManagement)
	* [Products Construction](#ProductsConstruction)

## <a name='Overview'></a>Overview

This repository contains useful shell scripts that automatically configure
a new linux system, install some common developmental tools, manage various
functions in system, install and configure some high-quality products, etc.

Note: scripts in this repository have been tested on **Ubuntu 22.04** system.

## <a name='Modules'></a>Modules

### <a name='Initialization'></a>Initialization

This module helps to do some necessary work of configuration and installation
after installing a new linux, including:

* Set some basic info: timezone, umask.
* Configure software mirror source.
* Install necessary tools.
* Configure common developmental tools.
* Configure sshd to only allow key authentication and restart it.

Just run `./run_init` to initialize a new system.

### <a name='SystemManagement'></a>System Management

This module includes scripts to manage various aspects of the system, such as
user management, network management, etc.

* User management: create users, delete users, etc.
* TODO

### <a name='ProductsConstruction'></a>Products Construction

TODO