import unittest as unittest
import datetime

from sqlite_influx import sqlite, influx

import sqlite_influx.Config as Config

class HighlevelTest(unittest.TestCase):
    measurement = 'test_measurement'
    example_data = {
        'channel1': 123.2,
        'channel2': 22.4
    }
    tags = {
        'server': 'test',
        'tag2': 'value2'
    }
    time_future = datetime.datetime(2099, 01, 01)

    def setUp(self):
        Config.config['engine'] = 'sqlite:///:memory:'

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
        res = influx.get_latest_measurement(self.measurement,
            self.tags)
        self.assertEqual(res, -1)

    def step6_sync(self):
        # create specific point in future (to be latest)
        time = self.time_future
        self.store_item(time)

        self.influx_sync()

    def step8_get_latest_found(self):
        res = influx.get_latest_measurement(self.measurement,
            self.tags)
        self.assertEqual(res, self.time_future)


    def influx_sync(self):
        pass

    def test_all(self):
        self.step1_store()
        self.step3_archive_none()
        self.step4_archive_10()
        self.step5_get_latest_empty()
        self.step6_sync()
        self.step8_get_latest_found()

    def something():
        stats_body = [
            {
                "measurement": "monitor-opcua-server",
                "tags": {
                    "host": "iot1",
                    "monitor-server": "pvlern"
                },
                #time always in utc
                "time":  datetime.datetime.utcnow(),
                "fields": {
                    #1 for up / ok
                    "value": 1
                }
            }
        ]
