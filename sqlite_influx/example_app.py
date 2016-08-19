"""example layer of how to use sqlite_influx
in an app"""

from sqlite_influx import Config, sqlite


measurements = {
    'test1': {
        'field1': 'data1',
        'field2': 'data2'
    },
    'test2': {
        'field3': 'data3'
    }
}

sqlite.store_dicts(measurements)

sqlite.sync_to_influx()
sqlite.archive(Config.config['archive_older_than_days'])
