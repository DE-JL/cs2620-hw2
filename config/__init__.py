import yaml
import importlib.resources

config_path = importlib.resources.files(__package__) / "config.yaml"

with config_path.open() as f:
    config = yaml.safe_load(f)

HOST = config["socket"]["host"]
PORT = config["socket"]["port"]
PROTOCOL_TYPE = config["protocol_type"]
DEBUG = config["debug"]

__all__ = [
    "HOST",
    "PORT",
    "PROTOCOL_TYPE",
    "DEBUG",
]
