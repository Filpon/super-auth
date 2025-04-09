from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.configs.logging import logger
from app.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=C0103


class ModelRepository(Generic[ModelType]):
    """
    Database model repository

    """

    def __init__(self, session: AsyncSession, model: ModelType):
        self.session = session
        self.model = model

    async def fetch_by_id(self, id: int) -> ModelType:  # pylint: disable=W0622
        """
        Fetching results by id

        :param int id: Identificator for filtering
        :return ModelType results: Filtered results
        """
        logger.info(f"Fetching record with {id=}")
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def fetch_by_filters(self, **filters) -> ModelType:
        """
        Fetching results by filters

        :param int id: Identificator for filtering
        :return ModelType results: Filtered results
        """
        query = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(
                    getattr(self.model, field).ilike(f"%{value}%")
                )  # Case-insensitive search
        result = await self.session.execute(query)
        return result.scalars().all()

    async def fetch_all(self) -> ModelType:
        """
        Fetching all results

        :return ModelType results: Fetched results
        """
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """
        Record creation

        :param ModelType obj: Object creation
        :return ModelType results: Fetched results
        """
        instance = self.model(**obj.dict())
        self.session.add(instance)
        await self.session.commit()
        return obj
