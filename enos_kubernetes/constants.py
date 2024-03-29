import os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

ANSIBLE_DIR = os.path.join(ROOT_PATH, "ansible")

CONF = os.path.join(os.getcwd(), "conf.yaml")

KUBESPRAY_VENV = os.path.join(os.getcwd(), "current", "kubespray-venv")
KUBESPRAY_PATH = "kubespray"

KUBESPRAY_URL = "https://github.com/kubernetes-sigs/kubespray.git"
KUBESPRAY_VERSION = "release-2.18"

# Enforce this defaut parameters if they are not given as variable in the
# configuration
DEFAULT_K_VARS = {
    "kubelet_max_pods": 100,
    "helm_enabled": True,
    "etcd_deployment_type": "docker",
    "dashboard_enabled": True,
    # since 2.9.0
    "dashboard_skip_login": True,
    # Since 2.18.0
    "container_manager": "docker",
    "docker_registry_mirrors": ["http://docker-cache.grid5000.fr"],
    "docker_insecure_registries": ["docker-cache.grid5000.fr"],
    # fix a transient bug (unreferenced for now)
    "enable_nodelocaldns": False,
}

BUILD_CONF_PATH = os.path.join(ROOT_PATH, "build_conf.yml")
DEFAULT_BUILD_CLUSTER = "parasilo"
