import os
import json

from mangum import Mangum
from django.core.asgi import get_asgi_application

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
        if isinstance(event["body"], str):
            event["body"] = json.loads(event["body"])
        else:
            event["body"] = json.loads(event["body"].decode())

    app = Mangum(application, lifespan="off")
    return app(event, context)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(application, host="0.0.0.0", port=8000)
# This handler is the lambda entrypoint for the not local environment
# for the local environment the entrypoint is the normal python manage.py runserver
