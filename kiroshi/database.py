"""Module containing the database models for Kiroshi.

It defines the following models:
- FrontDoorRanges
- FrontDoorIPs

Each model represents a table in the database and is defined using SQLAlchemy.
"""
from datetime import datetime

from sqlalchemy import ARRAY, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_base, mapped_column

from kiroshi.settings import settings

engine = create_engine(settings.database_dsn, echo=False)
Base: DeclarativeBase = declarative_base()


class FrontDoorRanges(Base):
    """Model representing the front door ranges table in the database."""

    __tablename__ = "frontdoor_ranges"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    ranges: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    last_updated: Mapped[datetime | None]


class FrontDoorIPs(Base):
    """Model representing the front door IPs table in the database."""

    __tablename__ = "frontdoor_ips"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    domain: Mapped[str | None]
    ips: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    last_updated: Mapped[datetime | None]
