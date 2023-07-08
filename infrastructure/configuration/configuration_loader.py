from dynaconf import LazySettings

from enums import EnvironmentType


settings = LazySettings(
    ROOT_PATH_FOR_DYNACONF="./configuration/",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True
)

class ConfigurationLoader:

    @staticmethod
    def get_setting(setting_key: str, env: str):
        return settings.from_env(env)[setting_key]


    @staticmethod
    def build_naming_convention(
        name: str,
        env: EnvironmentType,
        is_dynamodb_table_name: bool = False
    ):
        """
        This resources type has the stack id prefix so we dont need to
        adds the namespace and project name because the stack already has the prefix:
        excluded_resource_types = ["s3", "dynamodb", "lambda", "stepfunctions"]
        TODO: adds the rules
        """
        namespace = settings.from_env(env)["NAMESPACE"]
        project_name = settings.from_env(env)["PROJECT_NAME"]
        if not is_dynamodb_table_name:
            return f"{namespace}-{project_name}-{name}"
        
        return f"{namespace}_{project_name}_{name}"

