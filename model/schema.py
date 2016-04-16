# coding: utf-8
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

Base = declarative_base()
metadata = Base.metadata


class Location(Base):
    """
    Table to store all official forecast locations
    """
    __tablename__ = 'tbl_forecast_locations'

    id = Column(Integer, primary_key=True)
    location = Column(Geography(geometry_type='POINT', srid=4326, spatial_index=True))
    name = Column(String(128))


class Forecast(Base):
    """
    Table to store metadata from a forecast grid
    """
    __tablename__ = 'tbl_forecasts'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    creation_date = Column(DateTime)
    forecast_date = Column(DateTime)


class ForecastValue(Base):
    """
    Forecast grid split into location / values
    """
    __tablename__ = 'tbl_forecast_values'

    id = Column(Integer, primary_key=True)
    id_forecast = Column(Integer, ForeignKey('tbl_forecasts.id'), nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326, spatial_index=True))
    value = Column(DECIMAL(10,4))

    forecast = relationship(Forecast)


class RainfallObservation(Base):
    """
    Stores rainfall observation data
    """
    __tablename__ = 'tbl_rainfall_observations'

    time = Column(DateTime, index=True)
    location = Column(Geography(geometry_type='POINT', srid=4326, spatial_index=True))
    value = Column(DECIMAL(10,4))
    source = Column(String(128))
