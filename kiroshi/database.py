from sqlalchemy import ARRAY, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

from kiroshi.settings import settings

engine = create_engine(settings.database_dsn, echo=False)
base = declarative_base()


class FrontDoorRanges(base):
    __tablename__ = "frontdoor_ranges"

    id = Column(Integer, primary_key=True)
    ranges = Column(ARRAY(String))
    last_updated = Column(DateTime)


class FrontDoorIPs(base):
    __tablename__ = "frontdoor_ips"

    id = Column(Integer, primary_key=True)
    domain = Column(String)
    ips = Column(ARRAY(String))
    last_updated = Column(DateTime)
