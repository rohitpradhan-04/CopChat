from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlmodel import Session

from config.core import environmentVariables

consts = environmentVariables()
database_url = consts.database_url
connect_args = {"check_same_thread": False} if database_url and database_url.startswith("sqlite") else {}
engin = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def getDbSession():
    with Session(engin) as session:
        yield session


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
