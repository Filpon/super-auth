from typing import Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.brokers.kafka_producer import get_producer
from app.configs.logging_handler import configure_logging_handler
from app.database.db import get_db
from app.database.models import Event
from app.database.repository import ModelRepository, ModelType
from app.routers.auth import get_current_user
from app.schemas.events import EventCreateSchema, EventFetchSchema

logger = configure_logging_handler()

router = APIRouter()


@router.post("/create", response_model=EventCreateSchema)
async def create_event(
    event: EventCreateSchema,
    user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    producer: Any = Depends(get_producer),
) -> EventCreateSchema | Any:
    """
    Event creation for authenticated user

    :param EventCreateSchema event: Event for creation
    :param dict user: Current user instance
    :param AsyncSession db: Current database session
    """
    repository_events = ModelRepository(session=db, model=Event)
    event_finding_result = await repository_events.fetch_by_filters(name=event.name)
    if event_finding_result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event already exists in system",
        )
    event.client_info = user["azp"]
    event_creation_result = await repository_events.create(obj=event)  # type: ignore[arg-type]
    await producer.send_message(topic="events", message=f"{event.name} was created")
    logger.info("Event '%s' was created", event.name)
    return event_creation_result


@router.get("", response_model=list[EventFetchSchema])
@cache(expire=60)
async def fetch_events(
    user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ModelType]:
    """
    Events for current user fetching

    :param dict user: Current user instance
    :param AsyncSession db: Current database session
    """
    repository_events = ModelRepository(session=db, model=Event)
    fetch_events_result = await repository_events.fetch_by_filters(
        filters={"client_info": user["azp"]}
    )
    logger.info("Fetching result was successful")
    return fetch_events_result
