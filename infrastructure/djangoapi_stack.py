import os
import json
from typing import Tuple

from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as gateway,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secrets,
    RemovalPolicy,
    CfnOutput,
    Duration,
)
from constructs import Construct
from configuration.configuration_loader import ConfigurationLoader as Conf
from enums import EnvironmentType

dirname = os.path.dirname(__file__)
sql_port = 5442
db_username = "postgres"
db_name = "django"

class DjangoApiStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment: EnvironmentType,
        **kwargs
    ) -> None:
        """
        :param environment: This is the stage of this project and should be a EnvironmentType value
        """
        super().__init__(scope, construct_id, **kwargs)
        vpc_name = Conf.build_naming_convention(
            env=environment,
            name="vpc"
        )

        private_subnet_name = Conf.build_naming_convention(
            env=environment,
            name="PrivateSubnet"
        )
        public_subnet_name = Conf.build_naming_convention(
            env=environment,
            name="publicSubnet"
        )
        vpc = ec2.Vpc(
            self,
            id=vpc_name,
            cidr="10.50.0.0/16",
            nat_gateways=1,
            max_azs=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=private_subnet_name,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name=public_subnet_name,
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # SG
        lambda_sg_name = Conf.build_naming_convention(
            env=environment,
            name="lambda sg"
        )
        rds_sg_name = Conf.build_naming_convention(
            env=environment,
            name="rds sg"
        )

        lambda_sg = ec2.SecurityGroup(
            self,
            id=lambda_sg_name,
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Lambda sg"
        )
        rds_sg = ec2.SecurityGroup(
            self,
            id=rds_sg_name,
            vpc=vpc,
            allow_all_outbound=True,
            description=f"rds sg"
        )

        rds_sg.add_ingress_rule(
            # peer=ec2.Peer.ipv4("xxx.xxx.xxx.xxx/32"),
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(sql_port),
            description="all access"
        )

        rds_sg.add_ingress_rule(
            peer=lambda_sg,
            connection=ec2.Port.tcp(sql_port),
            description=f"{lambda_sg_name} Allow port "
        )

        # secrets
        secrets_template = json.dumps({
            "username": db_username
        })
        db_credentials_secret_name = "CredentialsSecret"
        db_credentials_secret = secrets.Secret(
            self,
            id=db_credentials_secret_name,
            secret_name=db_credentials_secret_name,
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template=secrets_template,
                exclude_punctuation=True,
                include_space=False,
                generate_string_key="password"
            )
        )

        # rds
        rds_instance_name = Conf.build_naming_convention(
            env=environment,
            name="DjangoPostgres"
        )
        rds_instance = rds.DatabaseInstance(
            self,
            id=rds_instance_name,
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15),
            credentials=rds.Credentials.from_secret(db_credentials_secret),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            database_name=db_name,
            port=sql_port,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            security_groups=[rds_sg],
            publicly_accessible=True,
            multi_az=False,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
        )


        # lambda
        lambda_django = _lambda.DockerImageFunction(
            scope=self,
            id="apilambda",
            code=_lambda.DockerImageCode.from_image_asset(
                os.path.join(dirname, "../src"),
                file="./Dockerfile"
            ),
            memory_size=128,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_sg],
            timeout=Duration.seconds(60),
            environment={
                "RDS_DB_NAME": db_name,
                "AWS_SECRET_ID": db_credentials_secret_name
            }
        )

        db_credentials_secret.grant_read(lambda_django)
        
        # API gateway
        api_gateway_name = Conf.build_naming_convention(
            env=environment,
            name="DjangoGw"
        )
        api = gateway.LambdaRestApi(
            scope=self,
            id=api_gateway_name,
            rest_api_name=api_gateway_name,
            api_key_source_type=gateway.ApiKeySourceType.HEADER,
            default_cors_preflight_options={
                "allow_origins": gateway.Cors.ALL_ORIGINS,
                "allow_methods": gateway.Cors.ALL_METHODS
            },
            proxy=True,
            handler=lambda_django
        )

        api_id_name = Conf.build_naming_convention(
            env=environment,
            name="DjangoApiIdGw"
        )
        CfnOutput(
            self,
            id=api_id_name,
            export_name=api_id_name,
            value=api.rest_api_id
        )
        CfnOutput(
            scope=self,
            id="dbEndpoint",
            value= rds_instance.instance_endpoint.hostname,
            description="db host")

        
        
        
        
