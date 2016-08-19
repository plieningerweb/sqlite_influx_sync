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


client = DBClient(Config.config['influx'])

def get_latest_measurement(measurement, tags):
    """return time of latest measurement

    Returns:
        time (int): time of last measuremnt if found, otherwise -1
    """
    if not tags:
        raise Exception('tag required to disctinctly select a measurement')

    tags_formatted = ['"{key}" = \'{value}\''.format(key=key, value=tags[key]) \
                      for key in tags]

    query = ('SELECT * FROM "{measurement}" '
             'WHERE {tags} ORDER BY time DESC LIMIT 1'.format(
                measurement=measurement,
                tags=' and '.join(tags_formatted)
             ))

    results = client.query(query)

    try:
        # assume only one result because of limit 1
        for r in results:
            time = r[0]['time'][0:19]
            time_parsed = dateutil.parser.parse(time)
            return time_parsed
    except Exception:
        raise

    return -1
