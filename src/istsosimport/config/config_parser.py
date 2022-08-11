import os
import toml

from collections import ChainMap
from pathlib import Path

from marshmallow import EXCLUDE

from marshmallow.exceptions import ValidationError

from istsosimport.env import DEFAULT_CONFIG_FILE
from istsosimport.config.config_schema import Config


def load_and_validate_toml(toml_file, config_schema):
    """
    Fonction qui charge un fichier toml
     et le valide avec un Schema marshmallow
    """
    toml_config = load_toml(toml_file)
    configs_py = config_schema().load(toml_config, unknown=EXCLUDE)

    return configs_py


def load_toml(toml_file):
    """
    Fonction qui charge un fichier toml
    """
    if not Path(toml_file).is_file():
        raise Exception("Missing file {}".format(toml_file))
    return toml.load(str(toml_file))


config_path = os.environ.get("GEONATURE_CONFIG_FILE", DEFAULT_CONFIG_FILE)
config = load_and_validate_toml(config_path, Config)
