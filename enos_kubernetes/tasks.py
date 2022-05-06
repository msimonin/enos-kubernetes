import logging
import os
from subprocess import check_call
import yaml

import enoslib as en

from enos_kubernetes.constants import (
    ANSIBLE_DIR,
    KUBESPRAY_URL,
    KUBESPRAY_VERSION,
    KUBESPRAY_VENV,
    KUBESPRAY_PATH,
    DEFAULT_K_VARS,
)

logger = logging.getLogger(__name__)

en.init_logging()


def check_call_in_venv(venv_dir, cmd):
    """Calls command in a specific virtualenv."""

    def check_venv(venv_path):

        if not os.path.exists(venv_path):
            check_call("virtualenv %s" % venv_path, shell=True)
            check_call_in_venv(venv_dir, "pip install --upgrade pip")

    logger.info("[%s] %s" % (venv_dir, cmd))
    cmd_in_venv = []
    cmd_in_venv.append(". %s/bin/activate " % venv_dir)
    cmd_in_venv.append("&&")
    cmd_in_venv.append(cmd)
    check_venv(venv_dir)

    return check_call(" ".join(cmd_in_venv), shell=True)


def in_kubespray(cmd):
    return check_call_in_venv(KUBESPRAY_VENV, cmd)


def update_k_vars(k_vars):
    """Update unspeified keys in k_vars with the defaults"""
    for k, v in DEFAULT_K_VARS.items():
        if k not in k_vars:
            k_vars[k] = v


@en.enostask(new=True)
def g5k(config, force, env=None, **kwargs):
    conf = en.G5kConf.from_dictionnary(config["g5k"])
    provider = en.G5k(conf)
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks
    env["context"] = "g5k"
    env["provider"] = provider


@en.enostask(new=True)
def vagrant(config, force, env=None, **kwargs):
    conf = en.VagrantConf.from_dictionnary(config["vagrant"])
    provider = en.Enos_vagrant(conf)
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks
    env["context"] = "vagrant"
    env["provider"] = provider


@en.enostask(new=True)
def vmong5k(config, force, env=None, **kwargs):
    conf = en.VMonG5kConf.from_dictionnary(config["vmong5k"])
    provider = en.VMonG5k(conf)
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks
    env["context"] = "vmong5k"
    env["provider"] = provider


@en.enostask(new=True)
def chameleon(config, force, env=None, **kwargs):
    from enoslib.infra.enos_chameleonbaremetal.provider import Chameleonbaremetal
    from enoslib.infra.enos_chameleonbaremetal.configuration import Configuration
    conf = Configuration.from_dictionnary(config["chameleon"])
    provider = Chameleonbaremetal(conf)
    roles, networks = provider.init(force_deploy=force)
    env["config"] = config
    env["roles"] = roles
    env["networks"] = networks
    env["context"] = "chameleon"
    env["provider"] = provider


@en.enostask()
def inventory(**kwargs):
    env = kwargs["env"]
    roles = env["roles"]
    networks = env["networks"]
    env["inventory"] = os.path.join(env["resultdir"], "hosts")
    en.generate_inventory(roles, networks, env["inventory"], check_networks=True)


@en.enostask()
def prepare(**kwargs):
    env = kwargs["env"]

    # common tasks
    extra_vars = {"enos_action": "deploy", "context": env["context"]}
    en.run_ansible(
        [os.path.join(ANSIBLE_DIR, "site.yml")], env["inventory"], extra_vars=extra_vars
    )

    kspray_path = os.path.join(env["resultdir"], KUBESPRAY_PATH)

    logger.info("Remove previous Kubespray installation")
    check_call("rm -rf %s" % kspray_path, shell=True)

    logger.info("Cloning Kubespray repository...")
    check_call(
        "git clone -b {ref} --depth 1 --single-branch --quiet {url} {dest}".format(
            ref=KUBESPRAY_VERSION, url=KUBESPRAY_URL, dest=kspray_path
        ),
        shell=True,
    )

    in_kubespray("cd %s && pip install -r requirements.txt" % kspray_path)
    kspray_inventory_path = os.path.join(
        kspray_path, "inventory", "mycluster", "hosts.ini"
    )

    in_kubespray("cd %s && cp -rfp inventory/sample inventory/mycluster" % kspray_path)
    in_kubespray(
        "cd %s && cp %s %s" % (kspray_path, env["inventory"], kspray_inventory_path)
    )

    k_vars = env["config"].get("vars", {})
    update_k_vars(k_vars)
    # Dumping overriden vars
    extra_vars_file = os.path.join(env["resultdir"], "extra_vars.yaml")
    with open(extra_vars_file, "w") as f:
        f.write(yaml.dump(env["config"].get("vars", {})))

    in_kubespray(
        "cd %s && ansible-playbook -i inventory/mycluster/hosts.ini"
        " "
        "cluster.yml -e @%s" % (kspray_path, extra_vars_file)
    )


@en.enostask()
def post_install(**kwargs):
    env = kwargs["env"]
    extra_vars = {"enos_action": "post-install"}
    # Adding the k vars
    extra_vars.update(env["config"].get("vars", {}))

    en.run_ansible(
        [os.path.join(ANSIBLE_DIR, "post_install.yml")],
        env["inventory"],
        extra_vars=extra_vars,
    )


@en.enostask()
def hints(**kwargs):
    env = kwargs["env"]
    master = env["roles"]["kube_control_plane"][0].address
    hints = []
    hints.append(
        "dashboard url : https://{}:6443/api/v1/namespaces/"
        "kube-system/services/https:kubernetes-dashboard:/"
        "proxy/#!/login".format(master)
    )

    hints.append(
        "start the proxy on {} : kubectl proxy --address='0.0.0.0'"
        "--accept-hosts='.*'".format(master)
    )

    hints.append(
        "dashboard url proxy : http://{}:8001/api/v1/namespaces/"
        "kube-system/services/https:kubernetes-dashboard:"
        "/proxy/#!/login".format(master)
    )

    hints.append(
        "Grafana dashboard: http://{}:8001/api/v1/namespaces/"
        "monitoring/services/kube-prometheus-stack-grafana:80"
        "/proxy/#!/login".format(master)
    )

    for hint in hints:
        print("{:->80}".format(""))
        print(hint)
    else:
        print("{:->80}".format(""))


@en.enostask()
def backup(**kwargs):
    env = kwargs["env"]
    extra_vars = {"enos_action": "backup"}
    en.run_ansible(
        [os.path.join(ANSIBLE_DIR, "site.yml")], env["inventory"], extra_vars=extra_vars
    )


@en.enostask()
def reset(**kwargs):
    env = kwargs["env"]
    kspray_path = os.path.join(env["resultdir"], KUBESPRAY_PATH)
    in_kubespray(
        "cd %s && ansible-playbook -i inventory/mycluster/hosts.ini"
        " "
        "reset.yml" % (kspray_path)
    )


@en.enostask()
def destroy(**kwargs):
    env = kwargs["env"]
    provider = env["provider"]
    provider.destroy()


PROVIDERS = {
    "g5k": g5k,
    "vagrant": vagrant,
    "vmong5k": vmong5k,
    "chameleon": chameleon
    #    "static": static
    #    "chameleon": chameleon
}
