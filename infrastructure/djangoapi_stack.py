import os
import json

from aws_cdk import (
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secrets,
    RemovalPolicy,
    CfnOutput,
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as acm,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ssm as ssm,
    aws_iam as iam
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
        self.s3_private_link = ec2.GatewayVpcEndpoint(
            self,
            "S3GWEndpoint",
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        self.ecr_api_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "ECRapiEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            open=True,
            private_dns_enabled=True
        )
        self.ecr_dkr_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "ECRdkrEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            open=True,
            private_dns_enabled=True
        )
        self.cloudwatch_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "CloudWatchEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            open=True,
            private_dns_enabled=True
        )
        self.secrets_manager_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "SecretsManagerEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            open=True,
            private_dns_enabled=True
        )
        # ecs cluster
        ecs_cluster = ecs.Cluster(self, f"ECSCluster", vpc=vpc)


        # SG
        ec2_sg_name = Conf.build_naming_convention(
            env=environment,
            name="lambda sg"
        )
        rds_sg_name = Conf.build_naming_convention(
            env=environment,
            name="rds sg"
        )

        lambda_sg = ec2.SecurityGroup(
            self,
            id=ec2_sg_name,
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
            description=f"{ec2_sg_name} Allow port "
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
        env_vars = environment={
            "RDS_HOST": rds_instance.instance_endpoint.hostname,
            "RDS_DB_NAME": db_name,
            "AWS_SECRET_ID": db_credentials_secret_name
        }
        secrets_values = {}

        ##########  elb   ####################
        task_cpu = 256
        task_memory_mib = 1024
        task_desired_count = 2
        task_min_scaling_capacity = 2
        task_max_scaling_capacity = 4
        # Prepare parameters
        self.container_name = f"django_app"
        # Retrieve the arn of the TLS certificate from SSM Parameter Store
        # self.certificate_arn = "todo: poner"
        # # Instantiate the certificate which will be required by the load balancer later
        # domain_certificate = acm.Certificate.from_certificate_arn(
        #     self, "DomainCertificate",
        #     certificate_arn=self.certificate_arn
        # )
        # policy to read the secrets
        secret_access_policy = iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=[db_credentials_secret.secret_arn]
        )

        # Añade la política de acceso al rol de ejecución de la tarea
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        task_role.add_to_policy(secret_access_policy)


        # Create the load balancer, ECS service and fargate task for teh Django App
        self.alb_fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"MyDjangoApp",
            protocol=elbv2.ApplicationProtocol.HTTP,
            redirect_http=False,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            cluster=ecs_cluster,  # Required
            task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            cpu=task_cpu,  # Default is 256
            memory_limit_mib=task_memory_mib,  # Default is 512
            desired_count=task_desired_count,  # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(
                    directory="../src",
                    file="./Dockerfile",
                    # target="prod"
                ),
                container_name=self.container_name,
                container_port=8000,
                environment=env_vars,
                secrets=secrets_values,
                task_role=task_role
            ),
            public_load_balancer=True
        )
        # Set the health checks settings
        self.alb_fargate_service.target_group.configure_health_check(
            path="/healthcheck",
            healthy_threshold_count=3,
            unhealthy_threshold_count=2
        )
        # Autoscaling based on CPU utilization
        scalable_target = self.alb_fargate_service.service.auto_scale_task_count(
            min_capacity=task_min_scaling_capacity,
            max_capacity=task_max_scaling_capacity
        )
        scalable_target.scale_on_cpu_utilization(
            f"CpuScaling",
            target_utilization_percent=75,
        )
        # Save useful values in in SSM
        self.ecs_cluster_name_param = ssm.StringParameter(
            self,
            "EcsClusterNameParam",
            parameter_name=f"/{scope.stage_name}/EcsClusterNameParam",
            string_value=ecs_cluster.cluster_name
        )
        self.task_def_arn_param = ssm.StringParameter(
            self,
            "TaskDefArnParam",
            parameter_name=f"/{scope.stage_name}/TaskDefArnParam",
            string_value=self.alb_fargate_service.task_definition.task_definition_arn
        )
        self.task_def_family_param = ssm.StringParameter(
            self,
            "TaskDefFamilyParam",
            parameter_name=f"/{scope.stage_name}/TaskDefFamilyParam",
            string_value=f"family:{self.alb_fargate_service.task_definition.family}"
        )
        self.exec_role_arn_param = ssm.StringParameter(
            self,
            "TaskExecRoleArnParam",
            parameter_name=f"/{scope.stage_name}/TaskExecRoleArnParam",
            string_value=self.alb_fargate_service.task_definition.execution_role.role_arn
        )
        self.task_role_arn_param = ssm.StringParameter(
            self,
            "TaskRoleArnParam",
            parameter_name=f"/{scope.stage_name}/TaskRoleArnParam",
            string_value=self.alb_fargate_service.task_definition.task_role.role_arn
        )
        CfnOutput(
            scope=self,
            id="dbEndpoint",
            value= rds_instance.instance_endpoint.hostname,
            description="db host")



        
        
        
        
