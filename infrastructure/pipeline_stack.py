import aws_cdk as cdk
from aws_cdk import (
    Tags,
    Environment,
    pipelines,
    aws_codebuild as codebuild
)
from constructs import Construct

from configuration.configuration_loader import ConfigurationLoader as Conf
from enums import EnvironmentType
from stages.django_stages import DjangoApiStage

SANDBOX_NAMESPACE = "sandbox"
PIPELINE_NAMESPACE = "pipeline"
PRODUCTION_NAMESPACE = "prod"

PROJECT_NAME = "djangoapp"

# Accounts
PIPELINE_ACCOUNT = "195480428059" # pipeline
SANDBOX_ACCOUNT = "057864228752" # sandbox
PRODUCTION_ACCOUNT = "009939884268" # Production

# Regions
PIPELINE_REGION = "us-east-2"
SANDBOX_REGION = "us-east-2"
PRODUCTION_REGION = "us-east-2"

# The aws connection ARN
CONECTION_ARN = "arn:aws:codestar-connections:us-east-2:195480428059:connection/cc3a11d6-6878-479b-947e-c27f5757d803"
REPOSITORY_NAME = "ale180192/aws-cdk-django"
REPOSITORY_BRANCH_NAME = "main"


class PipelineStack(cdk.Stack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        connection_source = pipelines.CodePipelineSource.connection(
            repo_string=REPOSITORY_NAME,
            branch=REPOSITORY_BRANCH_NAME,
            connection_arn=CONECTION_ARN
        )

        pipeline = pipelines.CodePipeline(
            scope=self,
            id=id,
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=connection_source,
                install_commands=["npm install -g aws-cdk"],
                commands=[
                    "ls", "cd infrastructure",
                    "python -m pip install -r requirements.txt",
                    "pwd", "ls", "cdk synth"
                ],
                primary_output_directory="infrastructure/cdk.out",
            ),
            pipeline_name=id,
            cross_account_keys=True,

        )
        # sandbox stage
        env_sandbox = Environment(
            account=SANDBOX_ACCOUNT, region=SANDBOX_REGION
        )
        sandbox_stage_name = Conf.build_naming_convention(
            name="buildStage",
            env=EnvironmentType.DEVELOPMENT.value
        )
        sandbox_stage = DjangoApiStage(
            scope=self,
            id=sandbox_stage_name,
            environment=EnvironmentType.DEVELOPMENT.value,
            env=env_sandbox
        )
        pipeline.add_stage(sandbox_stage)

        # Production Stage
        env_production = Environment(
            account=PRODUCTION_ACCOUNT, region=PRODUCTION_REGION
        )
        production_stage_name = Conf.build_naming_convention(
            name="buildStage",
            env=EnvironmentType.PRODUCTION.value
        )
        production_stage = DjangoApiStage(
            scope=self,
            id=production_stage_name,
            environment=EnvironmentType.PRODUCTION.value,
            env=env_production
        )
        manually_step_name = Conf.build_naming_convention(
            "manualApproveStep", env=EnvironmentType.DEVELOPMENT.value
        )
        pipeline.add_stage(
            production_stage,
            pre=[pipelines.ManualApprovalStep(id=manually_step_name)]
        )


