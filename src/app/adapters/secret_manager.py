import boto3
import json
from botocore.exceptions import ClientError


class SecretsManager:

    instance = None

    def __init__(self):
        if SecretsManager.instance is None:
            session = boto3.session.Session()
            SecretsManager.instance = session.client(
                service_name='secretsmanager', region_name="us-east-2")

    def get_secret_client(self):
        if SecretsManager.instance is None:
            SecretsManager()
        return SecretsManager.instance


    def get_secret(self, secret_id):
        try:
            secret = self.get_secret_client().get_secret_value(
                SecretId=secret_id
            )
        except ClientError as e:
            raise e
        else:
            if 'SecretString' in secret:
                return json.loads(secret['SecretString'])
            else:
                return {}