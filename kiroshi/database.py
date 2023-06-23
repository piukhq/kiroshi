"""Module containing the database models for Kiroshi.

It defines the following models:
- FrontDoorRanges
- FrontDoorIPs

Each model represents a table in the database and is defined using SQLAlchemy.
"""
from sqlalchemy import ARRAY, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

from kiroshi.settings import settings

engine = create_engine(settings.database_dsn, echo=False)
base = declarative_base()


class FrontDoorRanges(base):
    """Model representing the front door ranges table in the database."""

    __tablename__ = "frontdoor_ranges"

    id = Column(Integer, primary_key=True)  # noqa: A003
    ranges = Column(ARRAY(String))
    last_updated = Column(DateTime)


class FrontDoorIPs(base):
    """Model representing the front door IPs table in the database."""

    __tablename__ = "frontdoor_ips"

    id = Column(Integer, primary_key=True)  # noqa: A003
    domain = Column(String)
    ips = Column(ARRAY(String))
    last_updated = Column(DateTime)
