# test_database.py
from unittest.mock import AsyncMock, patch

import pytest  # pylint: disable=E0401
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db


@pytest.mark.anyio
async def test_get_db():
    """
    Testing session availability.

    This test verifies that the database session is correctly created and managed
    using the asynchronous context manager. It ensures that the session is available
    for use and that the appropriate enter and exit methods are called.

    Steps performed in this test:

    1. A mock of the `AsyncSession` is created to simulate database interactions.
    2. The `AsyncSessionLocal` is patched to return the mock session.
    3. The `get_db` generator function is called to obtain a session.
    4. Assertions are made to check that the session is the mock session and that
       the session's enter method is called once while the exit method is not called.
    5. The generator is closed, and it is asserted that the exit method is called once.
    """
    # Creation AsyncSession mock
    mock_session = AsyncMock(spec=AsyncSession)

    # Patching AsyncSessionLocal for mock
    with patch(
        "app.database.db.ASYNC_SESSION_LOCAL", return_value=mock_session
    ) as mock_database:
        mock_database.config = "mocked_config"
        async_generator = get_db()
        session = await anext(async_generator)  # Generator session obtaining

        # Session responses mock-object
        assert isinstance(session, AsyncMock)
        assert isinstance(mock_session, AsyncMock)

        # Session was created
        mock_session.__aenter__.assert_called_once()
        mock_session.__aexit__.assert_not_called()  # Exit was not called

        # Generator closing
        await async_generator.aclose()
        mock_session.__aexit__.assert_called_once()
