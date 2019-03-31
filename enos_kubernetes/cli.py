import click
import logging
import os
import yaml

import enos_kubernetes.tasks as t
from enos_kubernetes.constants import (CONF, BUILD_CONF_PATH,
                                       DEFAULT_BUILD_CLUSTER)

logging.basicConfig(level=logging.DEBUG)


@click.group()
def cli():
    pass


def load_config(file_path):
    """
    Read configuration from a file in YAML format.
    :param file_path: Path of the configuration file.
    :return:
    """
    with open(file_path) as f:
        configuration = yaml.safe_load(f)
    return configuration


def load_build_conf(provider, cluster=DEFAULT_BUILD_CLUSTER, working_dir=None):
    conf = load_config(BUILD_CONF_PATH)
    # yeah, that smells
    provider_conf = conf[provider]
    if provider == "g5k" or provider == "vmong5k":
        provider_conf["resources"]["machines"][0]["cluster"] = cluster
    if provider == "vmong5k":
        if working_dir is None:
            # force the working_dir
            working_dir = os.path.join(os.getcwd(), "working_dir")
            provider_conf["working_dir"] = working_dir
    return conf



@cli.command(help="Claim resources on Grid'5000 (frontend).")
@click.option("--force",
              is_flag=True,
              help="force redeployment")
@click.option("--conf",
              default=CONF,
              help="alternative configuration file")
@click.option("--env",
              help="alternative environment directory")
def g5k(force, conf, env):
    config = load_config(conf)
    t.g5k(config, force, env=env)


@cli.command(help="Claim resources on vagrant (localhost).")
@click.option("--force",
              is_flag=True,
              help="force redeployment")
@click.option("--conf",
              default=CONF,
              help="alternative configuration file")
@click.option("--env",
              help="alternative environment directory")
def vagrant(force, conf, env):
    config = load_config(conf)
    t.vagrant(config, force, env=env)


@cli.command(help="Generate the Ansible inventory [after g5k or vagrant].")
@click.option("--env",
              help="alternative environment directory")
def inventory(env):
    t.inventory(env=env)


@cli.command(help="Configure available resources [after deploy, inventory or\
             destroy].")
@click.option("--env",
              help="alternative environment directory")
def prepare(env):
    t.prepare(env=env)


@cli.command(help="Post install the deployement")
@click.option("--env",
              help="alternative environment directory")
def post_install(env):
    t.post_install(env=env)
    t.hints(env=env)


@cli.command(help="Give some hints on the deployment")
@click.option("--env",
              help="alternative environment directory")
def hints(env):
    t.hints(env=env)


@cli.command(help="Backup the deployed environment")
@click.option("--env",
              help="alternative environment directory")
def backup(env):
    t.backup(env=env)


@cli.command(help="Destroy the deployed environment")
@click.option("--env",
              help="alternative environment directory")
def destroy(env):
    t.destroy(env=env)


@cli.command(help="Resets Kubernetes (see kspray doc)")
@click.option("--env",
              help="alternative environment directory")
def reset(env):
    t.reset(env=env)


@cli.command(help="Claim resources from a PROVIDER and configure them.")
@click.argument("provider")
@click.option("--force",
              is_flag=True,
              help="force redeployment")
@click.option("--conf",
              default=CONF,
              help="alternative configuration file")
@click.option("--env",
              help="alternative environment directory")
def deploy(provider, force, conf, env):
    config = load_config(conf)
    t.PROVIDERS[provider](config, force, env=env)
    t.inventory(env=env)
    t.prepare(env=env)
    t.post_install(env=env)
    t.hints(env=env)


@cli.command(help="Preconfigure a machine with all the dependency. only vmong5k for now")
@click.argument("provider")
@click.option("--cluster",
              default=DEFAULT_BUILD_CLUSTER,
              help="cluster to use for building the base image")
def build(provider, cluster):
    force = False
    t.PROVIDERS[provider](load_build_conf(provider, cluster=cluster), force)
    t.inventory()
    t.prepare()
    t.reset()
