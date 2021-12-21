import asyncio
import logging
import signal
import sys
import typing

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

Base = declarative_base()


class Count(Base):
    __tablename__ = "cnt"
    __table_args__ = {"sqlite_autoincrement": True}

    number = Column(Integer, primary_key=True)
    memo = Column(UnicodeText)

    def __repr__(self):
        memo_repr = None if self.memo is None else f"'{self.memo}'"
        return f"<Count(number={self.number}, memo={memo_repr})>"


async def initialize_database() -> typing.Callable[[], None]:
    engine = create_async_engine("sqlite+aiosqlite:///counter.db", echo=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def cleanup():
        try:
            await engine.dispose()
        except Exception:
            logger.exception("Ignoring exception during disposing engine.")

    return cleanup


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    cleanup = loop.run_until_complete(initialize_database())

    class GracefulExit(SystemExit):
        pass

    def raise_graceful_exit():
        raise GracefulExit

    for sig in {signal.SIGINT, signal.SIGTERM}:
        loop.add_signal_handler(sig, raise_graceful_exit)
    try:
        loop.run_forever()
    except GracefulExit:
        logger.info("Exiting counter gracefully...")
    finally:
        loop.run_until_complete(cleanup())
