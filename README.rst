Enos-kubernetes
===============

|Build Status| |License| |Pypi|

Deploys Kubernetes on various providers. Deployments are for
evaluation/experimental purpose (not production).

Behind the scenes this project uses:

* Kubespray (https://github.com/kubernetes-sigs/kubespray): It uses decent
  defaults values but this should be reasonnable customizable (through roles
  and vars in the configuration file)

* EnOSlib (https://gitlab.inria.fr/discovery/enoslib) for the framework part.

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



.. |Build Status| image:: https://gitlab.inria.fr/msimonin/enos-Kubernetes/badges/master/pipeline.svg
   :target: https://gitlab.inria.fr/msimonin/enos-kubernetes/pipelines

.. |License| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. |Pypi| image:: https://badge.fury.io/py/enos-kubernetes.svg
   :target: https://badge.fury.io/py/enos-kubernetes
