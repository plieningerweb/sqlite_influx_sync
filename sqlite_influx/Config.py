config = {
    'engine': 'sqlite:///:memory:',
    'archive_older_than_days': 30,
    'influx': {
        'host': 'localhost',
        'user': 'no-need',
        'password': 'no-need',
        'dbname': 'pv-nodes',
        'port': 8086
    },
    'measurement': 'test-me',
    'tags': {
        'host': 'testhost.de',
        'region': 'europe'
    }
}
