"""example layer of how to use sqlite_influx
in an app"""

import yaml
import logging
from sqlite_influx import Config

# setup logging
logging.basicConfig(level=logging.INFO)

# setup config first, before we import the other stuff
with open('config.yaml', 'r') as stream:
    config_yaml = yaml.load(stream)
Config.config.update(config_yaml)

# now import helpers, which initialize database
# based on config data
from sqlite_influx import sqlite

# get measurements, e.g. from a sensor reading
measurements = {
    'test1': {
        'field1': 'data1',
        'field2': 'data2'
    },
    'test2': {
        'field3': 'data3'
    }
}

# store measurements
sqlite.store_dicts(measurements)

sqlite.sync_to_influx()
sqlite.archive(Config.config['archive_older_than_days'])
