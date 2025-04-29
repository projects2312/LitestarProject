import os

from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler
)

from db.schema import Base

DB_USERNAME = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_ENGINE = os.getenv("DB_ENGINE")
DB_PORT = os.getenv("DB_PORT")


connection_string = f"{DB_ENGINE}+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

db_config = SQLAlchemyAsyncConfig(
    connection_string=connection_string,
    metadata=Base.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler
)

# db_config = SQLAlchemyAsyncConfig(
#     connection_string="sqlite+aiosqlite:///db.sqlite",
#     metadata=Base.metadata,
#     create_all=True,
#     before_send_handler=autocommit_before_send_handler
# )
