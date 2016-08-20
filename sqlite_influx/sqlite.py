import json
import logging
import datetime
import dateutil.parser

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlite_influx import Config, influx

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
engine = create_engine(Config.config['engine'], echo=False)
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
        logger.info("Stored measurement {} ({})".format(measurement,
            time.isoformat()))
    except:
        session.rollback()
        logger.exception("Could not store measurement {} ({})".format(measurement,
            time.isoformat()))
        raise
    finally:
        # close session?
        pass

def store_dicts(measurements):
    """store dicts of measurements with time now"""
    time = datetime.datetime.utcnow()
    for m in measurements:
        store(m, Config.config['tags'],
            time, measurements[m])

def archive(older_than_days):
    """archive all history which is older than x days

    Returns:
        archved_items (int): Count of archived rows

    ::warning:: archive in this case means delete
    """
    try:
        conn = engine.connect()

        # use datetime time instead of built in sqlite stuff
        # because timezone etc. handling is different
        min_time = datetime.datetime.utcnow() - \
            datetime.timedelta(days=older_than_days)
        where = ("WHERE "
                 "unix_timestamp <= {min_time}".format(
                 min_time=min_time.strftime("%s")))

        count = conn.execute("select count(*) as count from history " + where)
        affected_rows = count.first()[0]

        sql = ("DELETE FROM history " + where)
        conn.execute(sql)

        logger.info("Archived {} rows older than {} days".format(
            affected_rows,
            older_than_days))

        return affected_rows
    except Exception:
        logger.exception("Could not archive data {} days back".format(
            older_than_days))
        raise

def history_to_dict(row):
    return dict(
        measurement=row.measurement,
        # conver to isoformat, so we have common precision in infludb
        time=dateutil.parser.parse(row.time).isoformat(),
        tags=json.loads(row.tags),
        fields=json.loads(row.fields)
    )

def sync_to_influx():
    """sync all new items from sqlite to influxdb

    Returns:
        count (int): of syncted items or -1 if failed
    """
    logger.info("start sync to influx")

    try:
        # get latest influx point
        last = influx.get_latest_measurement(Config.config['tags'])
        logger.info("sync to influx since {}".format(last))

        # load all local points since then
        query = session.query(History)
        if isinstance(last, datetime.datetime):
            query = query.filter(History.unix_timestamp > int(last.strftime('%s')))

        rows = query.all()

        # build query
        data = [history_to_dict(row) for row in rows]

        # store to influx
        influx.client.writeData(data)

        logger.info("synced {} measurements to influx".format(len(data)))

        return len(data)
    except Exception as e:
        logger.exception("sync to influx failed")

    return -1
