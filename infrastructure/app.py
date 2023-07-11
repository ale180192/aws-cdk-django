#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import (
    Tags,
    Environment,
)

from configuration.configuration_loader import ConfigurationLoader as Conf
from enums import EnvironmentType
import pipeline_stack

app = cdk.App()
props = {}

name_pipeline = Conf.build_naming_convention(
    name="pipelinestack",
    env=EnvironmentType.PIPELINE.value
)

env_pipeline = Environment(
    account=pipeline_stack.PIPELINE_ACCOUNT,
    region=pipeline_stack.PIPELINE_REGION
)
pipeline_stack.PipelineStack(
    scope=app,
    id=name_pipeline,
    env=env_pipeline
)
app.synth()


