from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
from sqlalchemy import inspect


import dotenv
dotenv.load_dotenv()

host = os.environ.get("DB_HOST", "")
port = os.environ.get("DB_PORT", "")
user = os.environ.get("DB_USER", "")
password = os.environ.get("DB_PASSWORD", "")
database = os.environ.get("DB_DATABASE", "")

if os.environ.get("testing", "") == "1":
    db_uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(db_uri)
    with engine.execution_options(isolation_level="AUTOCOMMIT").connect() as con:
        if con.execute(text("select * from pg_database where datname='postgres_test'")).all():
            con.execute(text("drop database postgres_test"))
        con.execute(text("create database postgres_test"))

    database = f"{database}_test"

db_uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
connect_args = {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 5,
    "keepalives_count": 5,
}
engine = create_engine(db_uri, pool_pre_ping=True, connect_args=connect_args)

conn = engine.connect()

Session = sessionmaker(bind=engine)
# session = Session()

Base = declarative_base()
metadata = Base.metadata

def truncate_db():
    inspector = inspect(engine)
    con = engine.connect()
    trans = con.begin()
    for table_name in inspector.get_table_names(schema="public"):
        con.execute(text(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL;'))
        con.execute(text(f'DELETE FROM "{table_name}";'))
        con.execute(text(f'ALTER TABLE "{table_name}" ENABLE TRIGGER ALL;'))
    trans.commit()

from sqlalchemy.ext.asyncio import create_async_engine
from google.cloud.alloydb.connector import IPTypes
from langchain_google_alloydb_pg import AlloyDBEngine
import asyncio
from threading import Thread
from typing import Optional, Union

db_user = user
db_password = password
db_host = host
db_port = port
db_database = database

async def monkey__create(
    cls,
    project_id: str,
    region: str,
    cluster: str,
    instance: str,
    database: str,
    ip_type: Union[str, IPTypes],
    user: Optional[str] = None,
    password: Optional[str] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    thread: Optional[Thread] = None,
):
    engine = create_async_engine(
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    )
    return AlloyDBEngine(engine, loop, thread)

AlloyDBEngine._create = monkey__create
alloy_db_engine = AlloyDBEngine.from_instance(
    project_id="",
    region="",
    cluster="",
    instance="",
    database="",
)
CHAT_MESSAGE_TABLE_NAME = "chat_messages"
alloy_db_engine.init_chat_history_table(table_name=CHAT_MESSAGE_TABLE_NAME)