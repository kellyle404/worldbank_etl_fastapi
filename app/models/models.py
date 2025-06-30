from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from app.core.config import settings

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    indicators_meta = relationship('IndicatorMeta', back_populates='topic')

class IndicatorMeta(Base):
    __tablename__ = 'indicator_meta'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    source_note = Column(String, nullable=True)
    topic = relationship('Topic', back_populates='indicators_meta')
    values = relationship('IndicatorValue', back_populates='indicator_meta')

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    iso3 = Column(String(3), unique=True, nullable=False)
    name = Column(String, nullable=False)
    region = Column(String, nullable=True)
    indicator_values = relationship('IndicatorValue', back_populates='country')

class IndicatorValue(Base):
    __tablename__ = 'indicator_values'
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey('indicator_meta.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    date = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    indicator_meta = relationship('IndicatorMeta', back_populates='values')
    country = relationship('Country', back_populates='indicator_values')
    __table_args__ = (UniqueConstraint('indicator_id', 'country_id', 'date', name='uix_indicator_country_date'),)