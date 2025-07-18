import os

from aiokafka.admin import NewTopic
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.brokers.kafka import start_admin_client, start_kafka_producer
from app.configs.logging import logger
from app.database.db import engine
from app.database.models import Base
from app.routers import auth, events
from app.services.keycloak import verify_permission, verify_token

load_dotenv()  # Environmental variables

ORIGINS = os.getenv("ORIGINS")

print(f"{ORIGINS=}")

# FastAPI app creation
app = FastAPI(docs_url="/api/v1/docs", openapi_url="/api/v1/openapi")

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

app.include_router(
    events.router,
    prefix="/api/v1/events",
    tags=["events"],
    dependencies=[Depends(verify_token)],
)

# Configure CORS
origins = ORIGINS.split(sep=",")
print(f"{origins=}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def root() -> Response:
    """
    API Healthcheck

    :returns Response: Response with sucessful status code
    """
    return Response(status_code=status.HTTP_200_OK)

@app.get("/admin")  # Requires the admin role
def call_admin(user = Depends(verify_permission(required_roles=["admin"]))):
    """
    Admin role obtaining

    :param list required_roles: Role admin for calling
    :returns string: Messager for admin user
    """
    return f"Hello, admin {user}"

# Database creation
@app.on_event("startup")
async def startup():
    """
    Starting database creation

    """
    async with engine.begin() as connector:
        await connector.run_sync(Base.metadata.create_all)
    logger.info("Database creation was finished")
    app.state.producer = await start_kafka_producer()

@app.post("/send")
async def send_message(message: str):
    """
    Sending message to a Kafka topic.

    This asynchronous function takes a message as input, encodes it in UTF-8,
    and sends it to the specified Kafka topic using the producer.

    :param str message: The message to be sent to the Kafka topic.
    :return dict: A JSON response indicating the status of the message sending.
    """
    await app.state.producer.send_and_wait('my_topic', message.encode('utf-8'))
    return {"message": "Message sent to Kafka"}

@app.post("/create_topic")
async def create_topic(topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
    """Create a new Kafka topic.

    This endpoint allows you to create a new Kafka topic by providing the topic name,
    number of partitions, and replication factor.

    :param str topic_name: The name of the topic to create.
    :param int num_partitions: The number of partitions for the topic (default is 1).
    :param int replication_factor: The replication factor for the topic (default is 1).
    :return dict: A message indicating the success of the topic creation.
    :raises HTTPException: If the topic name is not provided or if there is an error.
    """
    if not topic_name:
        raise HTTPException(status_code=400, detail="Topic name should be provided")

    try:
        async with start_admin_client() as admin_client:
            await admin_client.create_topics(
                [
                    NewTopic(
                        name=topic_name,
                        num_partitions=num_partitions,
                        replication_factor=replication_factor,
                    )
                ]
            )
        return {"message": f"Topic '{topic_name}' created successfully."}
    except Exception as excp:
        raise HTTPException(status_code=500, detail=str(excp)) from excp


if __name__ == "__main__":
    import asyncio

    import uvicorn

    asyncio.run(uvicorn.run(app, host="0.0.0.0", port=8001))
