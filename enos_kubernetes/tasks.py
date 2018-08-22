from enoslib.api import generate_inventory, run_ansible
from enoslib.task import enostask
from enoslib.infra.enos_g5k.provider import G5k
from enoslib.infra.enos_vagrant.provider import Enos_vagrant
import logging
import os
from subprocess import check_call
import yaml

from enos_kubernetes.constants import (ANSIBLE_DIR,
                                       KUBESPRAY_VENV,
                                       KUBESPRAY_PATH)

logger = logging.getLogger(__name__)

def check_call_in_venv(venv_dir, cmd):
    """Calls command in a specific virtualenv."""

    def check_venv(venv_path):

        if not os.path.exists(venv_path):
            check_call("virtualenv %s" % venv_path, shell=True)
            check_call_in_venv(venv_dir, "pip install --upgrade pip")

    logger.info("[%s] %s" % (venv_dir, cmd))
    cmd_in_venv = []
    cmd_in_venv.append(". %s/bin/activate " % venv_dir)
    cmd_in_venv.append('&&')
    cmd_in_venv.append(cmd)
    check_venv(venv_dir)

    return check_call(' '.join(cmd_in_venv), shell=True)


def in_kubespray(cmd):
    return check_call_in_venv(KUBESPRAY_VENV, cmd)


@enostask(new=True)
def g5k(config, force, env=None, **kwargs):
    provider = G5k(config["g5k"])
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks


@enostask(new=True)
def vagrant(config, force, env=None, **kwargs):
    provider = Enos_vagrant(config["vagrant"])
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks


@enostask()
def inventory(**kwargs):
    env = kwargs["env"]
    roles = env["roles"]
    networks = env["networks"]
    env["inventory"] = os.path.join(env["resultdir"], "hosts")
    generate_inventory(roles, networks, env["inventory"], check_networks=True)


@enostask()
def prepare(**kwargs):
    env = kwargs["env"]

    # common tasks
    extra_vars = {
        "enos_action": "deploy"
    }
    run_ansible([os.path.join(ANSIBLE_DIR, "site.yml")],
                env["inventory"], extra_vars=extra_vars)


    kspray_path = os.path.join(env['resultdir'], KUBESPRAY_PATH)

    logger.info("Remove previous Kubespray installation")
    check_call("rm -rf %s" % kspray_path, shell=True)

    logger.info("Cloning Kubespray repository...")
    check_call("git clone --depth 1 --branch v2.6.0 --single-branch --quiet %s %s" %
                ("https://github.com/kubernetes-incubator/kubespray",
                kspray_path),
                shell=True)
    in_kubespray("cd %s && pip install -r requirements.txt" % kspray_path)
    kspray_inventory_path = os.path.join(kspray_path, "inventory", "mycluster", "hosts.ini")
    in_kubespray("cd %s && cp -rfp inventory/sample inventory/mycluster" % kspray_path)
    in_kubespray("cd %s && cp %s %s" % (kspray_path, env["inventory"], kspray_inventory_path))


    # Dumping overriden vars
    extra_vars_file = os.path.join(env["resultdir"], "extra_vars.yaml")
    with open(extra_vars_file, "w") as f:
        f.write(yaml.dump(env["config"].get("vars", {})))


    in_kubespray("cd %s && ansible-playbook -i inventory/mycluster/hosts.ini cluster.yml -e %s" % (kspray_path, extra_vars_file))


@enostask()
def backup(**kwargs):
    env = kwargs["env"]
    extra_vars = {
        "enos_action": "backup"
    }
    run_ansible([os.path.join(ANSIBLE_DIR, "site.yml")],
                env["inventory"], extra_vars=extra_vars)


@enostask()
def destroy(**kwargs):
    env = kwargs["env"]
    extra_vars = {
        "enos_action": "destroy"
    }
    run_ansible([os.path.join(ANSIBLE_DIR, "site.yml")],
                env["inventory"], extra_vars=extra_vars)


PROVIDERS = {
    "g5k": g5k,
    "vagrant": vagrant,
    #    "static": static
    #    "chameleon": chameleon
}


