Welcome to enos-kubernetes' documentation!
==========================================

.. hint ::

    The source code is available at
    https://gitlab.inria.fr/msimonin/enos-kubernetes


Command line overview
---------------------

.. code-block :: bash

    Usage: ek [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      backup        Backup the deployed environment
      build         Preconfigure a machine with all the...
      deploy        Claim resources from a PROVIDER and configure...
      destroy       Destroy the deployed environment
      g5k           Claim resources on Grid'5000 (frontend).
      hints         Give some hints on the deployment
      inventory     Generate the Ansible inventory [after g5k or...
      post_install  Post install the deployement
      prepare       Configure available resources [after deploy,...
      reset         Resets Kubernetes (see kspray doc)
      vagrant       Claim resources on vagrant (localhost).


Usage overview
--------------

Install the project::

    pip install enos-kubernetes

Get a sample configuration file at::

    wget https://gitlab.inria.fr/msimonin/enos-kubernetes/blob/master/conf.yaml

Deploy on g5k::

    ek deploy g5k


Deploy on g5k using virtual machines::

    ek deploy vmong5k


Build a base image on g5k::

    ek build g5k

Build a base image on vmong5k with an alternative cluster::

    ek build vmong5k --cluster=chetemi
