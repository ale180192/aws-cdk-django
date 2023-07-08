import enum

class ResourceType(enum.Enum):
    SQS = "sqs"
    SNS =  "sns"

class AuthorizerType(enum.Enum):
    GCP = "gcp"


class EnvironmentType(enum.Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    PIPELINE = "pipeline"