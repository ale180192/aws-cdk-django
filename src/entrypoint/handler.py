import os
import json
import sys

from mangum import Mangum
from django.core.asgi import get_asgi_application
# os.environ.setdefault("ENVIRONMENT", "local")
# root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(root_path)


from app.utils import logger as _logger
from app.config import boostrap

logger = _logger.get_logger()

settings = boostrap()

print("AWS_PROFILE uvicorn", settings.AWS_SECRET_ID)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapi.settings")



application = get_asgi_application()

def main(event, context):
    logger.info(event)
    logger.info(context)
    if event["httpMethod"] == "POST" and event["headers"].get("Content-Type") == "application/json":
        logger.info("body type")
        logger.info(event["body"])
        logger.info(type(event["body"]))

    app = Mangum(application, lifespan="off")
    return app(event, context)

# if __name__ == "__main__":
#     import uvicorn
#     os.environ.setdefault("ENVIRONMENT", "local")
#     print("path", root_path)
#     uvicorn.run(application, host="0.0.0.0", port=8000, env_file="../.env")
# This handler is the lambda entrypoint for the not local environment
# for the local environment the entrypoint is the normal python manage.py runserver
