import json


class ConfigProcessor:

    def __init__(self, json_path: str):
        self.configs = self.__class__._get_project_configs(json_path)

    def get_configs(self):
        return self.configs

    @staticmethod
    def _get_project_configs(json_path: str) -> str:
        print("Config json path:", json_path)
        return json.load(open(json_path))
