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
    'tags': {
        'host': 'testhost.de',
        'region': 'europe'
    }
}
