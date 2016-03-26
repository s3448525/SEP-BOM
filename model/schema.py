# coding: utf-8
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geography

Base = declarative_base()
metadata = Base.metadata


class Location(Base):
    __tablename__ = 'tbl_locations'

    id = Column(Integer, primary_key=True)
    geom = Column(Geography(geometry_type='POINT', srid=4326, spatial_index=True))
    name = Column(String(128))
