import json, os


class ConfigProcessor:

    def __init__(self, config_dir_path: str):
        self.configs = self.__class__._get_project_configs(config_dir_path)

    def get_configs(self):
        return self.configs

    @staticmethod
    def _get_project_configs(config_dir_path: str) -> str:
        # 1. Get config type
        cfg_type = os.getenv("CFG_TYPE")
        if cfg_type is None:
            raise RuntimeError("You have to set CFG_TYPE environment variable")
        print("Using config type:", cfg_type)

        # 2. Here it is supposed that config files are contained in the directory
        # which path corresponds to the following pattern:
        # <the project dir path> + "/config/" + <development/production>.json
        json_path = os.path.join(config_dir_path, "config", cfg_type + ".json")
        print("Config json path:", json_path)

        return json.load(open(json_path))
