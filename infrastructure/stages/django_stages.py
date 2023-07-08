from aws_cdk import (
    Stage,
    Environment
)
from constructs import Construct

from djangoapi_stack import DjangoApiStack
from enums import EnvironmentType


class DjangoApiStage(Stage):

    def __init__(
        self, scope: Construct,
        id: str,
        environment: EnvironmentType,
        env: Environment,
        props: dict = {}
    ):
        """
        :param environment: Stage environment of the app.
        """
        super().__init__(scope, id, env=env)
        DjangoApiStack(
            scope=self,
            construct_id=id,
            environment=environment,
            env=env
        )

