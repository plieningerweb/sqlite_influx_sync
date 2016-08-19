import logging
import dateutil.parser

from influxdb import InfluxDBClient

from sqlite_influx import Config

logger = logging.getLogger(__name__)

class DBClient:
    client = False

    def __init__(self,config):
        self.client = InfluxDBClient(config['host'], config['port'], \
                    config['user'], config['password'], config['dbname'])

        logger.info("connected to influx database '{}'".format(config['dbname']))

    def writeData(self,data):
        logger.info("write points to influx: {0}".format(data))
        self.client.write_points(data)

    def query(self, query):
        logger.debug("run query: {}".format(query))
        return self.client.query(query)

    def create_database(self, db):
        self.client.create_database(db)

    def drop_database(self, db):
        self.client.drop_database(db)

client = DBClient(Config.config['influx'])

def get_latest_measurement(tags):
    """return time of latest measurement

    Returns:
        time (int or datetime.datetime): time of last
        measuremnt if found, otherwise -1
    """
    if not tags:
        raise Exception('tag required to disctinctly select a measurement')

    tags_formatted = ['"{key}" = \'{value}\''.format(key=key, value=tags[key]) \
                      for key in tags]

    # see http://docs.influxdata.com/influxdb/v0.12/troubleshooting/frequently_encountered_issues/#querying-after-now
    # to get results of future points
    # add where clause with time in future
    query = ('SELECT * FROM /.*/ '
             'WHERE {tags} and time < now() + 2w '
             'ORDER BY time DESC LIMIT 1'.format(
                tags=' and '.join(tags_formatted)
             ))

    results = client.query(query)

    try:
        logger.debug("last measurement found {} results".format(len(results)))
        # assume only one result because of limit 1
        for r in results:
            print(r)
            # use only seconds, remove microseconds
            # as influx stores 2016-08-26T23:05:22.000360 as
            # 26T23:05:22.000359936, which is not the same
            # and tests will fail
            # therefore only use second precision
            time = r[0]['time'][0:16]
            time_parsed = dateutil.parser.parse(time)

            logger.debug("last measurement from {}".format(time_parsed))
            return time_parsed
    except Exception:
        raise

    return -1
