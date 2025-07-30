from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.configs.logging_handler import configure_logging_handler
from app.database.models import Base

logger = configure_logging_handler()

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=C0103


class ModelRepository(Generic[ModelType]):
    """
    Database model repository

    """

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def fetch_by_id(self, id: int) -> ModelType | None:  # pylint: disable=W0622
        """
        Fetching results by id

        :param int id: Identificator for filtering
        :return ModelType | None results: Filtered results
        """
        logger.info("Fetching record with id=%s", id)
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def fetch_by_filters(self, **filters: Any) -> Sequence[ModelType]:
        """
        Fetching results by filters

        :param int id: Identificator for filtering
        :return list[ModelType] results: Filtered results
        """
        query = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(
                    getattr(self.model, field).ilike(f"%{value}%")
                )  # Case-insensitive search
        result = await self.session.execute(query)
        return result.scalars().all()

    async def fetch_all(self) -> Sequence[ModelType]:
        """
        Fetching all results

        :return list[ModelType] results: Fetched results
        """
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj: ModelType) -> Any:
        """
        Record creation

        :param ModelType obj: Object creation
        :return ModelType results: Fetched results
        """
        instance = self.model(**obj.dict())
        self.session.add(instance)
        await self.session.commit()
        return instance
