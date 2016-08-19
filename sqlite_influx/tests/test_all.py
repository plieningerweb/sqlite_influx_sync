import unittest as unittest
import datetime
import dateutil

import sqlite_influx.Config as Config
from sqlite_influx import sqlite, influx

class HighlevelTest(unittest.TestCase):
    measurement = 'test_measurement'
    example_data = {
        'channel1': 123.2,
        'channel2': 22.4
    }
    tags = Config.config['tags']
    time_future = datetime.datetime.utcnow() + \
        datetime.timedelta(days=7)
    # parse again so we always get same timestamp as from influxdb
    time_future = dateutil.parser.parse(time_future.isoformat()[0:16])

    def setUp(self):
        # setup database in influx
        # first clean then create
        influx.client.drop_database(Config.config['influx']['dbname'])
        influx.client.create_database(Config.config['influx']['dbname'])

    def store_item(self, time):
        sqlite.store(self.measurement, self.tags,
            time, self.example_data)

    def step1_store(self):
        time = datetime.datetime.utcnow()
        self.store_item(time)

    def step3_archive_none(self):
        archived = sqlite.archive(Config.config['archive_older_than_days'])
        self.assertEqual(archived, 0)

    def step4_archive_10(self):
        today = datetime.datetime.utcnow()
        days = [today - datetime.timedelta(days=d) for d in range(1, 30)]

        # insert days
        insert = [self.store_item(d) for d in days]

        # remove older than 20 days
        affected = sqlite.archive(20)

        self.assertEqual(affected, 10)

    def step5_get_latest_empty(self):
        res = influx.get_latest_measurement(self.tags)
        self.assertEqual(res, -1)

    def step6_sync(self):
        # create specific point in future (to be latest)
        time = self.time_future
        self.store_item(time)

        count = sqlite.sync_to_influx()
        self.assertEqual(count, 21)

    def step8_get_latest_found(self):
        res = influx.get_latest_measurement(self.tags)
        print(res)
        print(self.time_future)
        self.assertEqual(res, self.time_future)

    def step9_sync_emtpy(self):
        count = sqlite.sync_to_influx()
        self.assertEqual(count, 0)

    def step10_sync_nodb(self):
        influx.client.drop_database(Config.config['influx']['dbname'])

        count = sqlite.sync_to_influx()
        # should fail
        self.assertEqual(count, -1)

    def step11_store_dicts(self):
        dicts = {
            self.measurement: self.example_data,
            self.measurement + '2': self.example_data
        }
        sqlite.store_dicts(dicts)

    def step99_example_app(self):
        from sqlite_influx import example_app

    def test_all(self):
        self.step1_store()
        self.step3_archive_none()
        self.step4_archive_10()
        self.step5_get_latest_empty()
        self.step6_sync()
        self.step8_get_latest_found()
        self.step9_sync_emtpy()
        self.step10_sync_nodb()
        self.step11_store_dicts()

        self.step99_example_app()
