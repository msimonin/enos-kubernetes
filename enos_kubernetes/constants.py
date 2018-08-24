
import os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

ANSIBLE_DIR = os.path.join(ROOT_PATH, "ansible")

CONF = os.path.join(os.getcwd(), "conf.yaml")

KUBESPRAY_VENV = os.path.join(os.getcwd(), "current", "kubespray-venv")
KUBESPRAY_PATH = "kubespray"

# Enforce this defaut parameters if they are not given as variable in the
# configuration
DEFAULT_K_VARS = {
    "kubelet_max_pods": 100,
    "helm_enabled": True
}
