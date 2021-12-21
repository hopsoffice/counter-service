import asyncio
import functools
import json
import logging
import signal
import sys
import typing

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

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


async def initialize_database() -> typing.Tuple[
    typing.Callable[[], AsyncSession], typing.Callable[[], None]
]:
    engine = create_async_engine("sqlite+aiosqlite:///counter.db", echo=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def cleanup():
        try:
            await engine.dispose()
        except Exception:
            logger.exception("Ignoring exception during disposing engine.")

    return (
        sessionmaker(engine, expire_on_commit=False, class_=AsyncSession),
        cleanup,
    )


async def count_number(
    make_session: typing.Callable[[], AsyncSession], request: Request
) -> JSONResponse:
    try:
        request_body = await request.json()
    except json.decoder.JSONDecodeError:
        request_body = {}
    new_count = Count(memo=request_body.get("memo"))
    try:
        async with make_session() as session:
            async with session.begin():
                session.add(new_count)
                session.commit()
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})
    else:
        return JSONResponse(
            {
                "success": True,
                "data": {"number": new_count.number, "memo": new_count.memo},
            }
        )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    make_session, cleanup = loop.run_until_complete(initialize_database())
    logger.info("Database connection initialized.")
    app = Starlette(
        routes=[
            Route(
                "/count/",
                functools.partial(count_number, make_session),
                methods=["POST"],
            ),
        ]
    )
    logger.info("App initialized.")

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
