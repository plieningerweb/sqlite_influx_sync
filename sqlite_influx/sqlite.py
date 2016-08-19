import json
import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sqlite_influx.Config as Config

logger = logging.getLogger(__name__)
Base = declarative_base()

class History(Base):
    __tablename__ = 'history'
    __table_args__ = {'sqlite_autoincrement': True}
    #tell SQLAlchemy the name of column and its attributes:
    id = Column(Integer, primary_key=True, nullable=False)
    measurement = Column(String)
    time = Column(String)
    tags = Column(String)
    fields = Column(String)
    unix_timestamp = Column(Integer)

#Create the database
engine = create_engine(Config.config['engine'], echo=True)
Base.metadata.create_all(engine)

#Create the session
session_factory = sessionmaker()
session_factory.configure(bind=engine)
session = session_factory()

def store(measurement, tags, time, fields):
    record = History(measurement = measurement,
        time=time.isoformat(),
        tags=json.dumps(tags),
        fields=json.dumps(fields),
        unix_timestamp=int(time.strftime("%s"))
        )

    try:
        session.add(record)
        session.commit()
        logger.info("Stored {} ({})".format(measurement, time.isoformat()))
    except:
        session.rollback()
        logger.error("Could not store {} ({})".format(measurement,
            time.isoformat()))
        raise
    finally:
        # close session?
        pass

def archive(older_than_days):
    """archive all history which is older than x days

    Returns:
        archved_items (int): Count of archived rows

    ::warning:: archive in this case means delete
    """
    try:
        conn = engine.connect()

        where = ("WHERE "
                 "unix_timestamp <= strftime('%s','now','-{days} days')".format(
                 days=older_than_days))

        count = conn.execute("select count(*) as count from history " + where)
        affected_rows = count.first()[0]

        sql = ("DELETE FROM history " + where)
        conn.execute(sql)

        logger.info("Archived {} rows older than {} days".format(
            affected_rows,
            older_than_days))

        return affected_rows
    except Exception:
        logger.error("Could not archive data {} days back".format(
            older_than_days))
        raise




def sync_influx():
    pass
    # get latest influx point
    # load all local points since then
    # store in influx
