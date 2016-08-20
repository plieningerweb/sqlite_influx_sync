# Sqlite to InfluxDB Sync

* Sqlite as local cach for InfluxDB measurements
* Sync measurements to remote InfluxDB

Short example, for details check `sqlite_influx/example_app.py`.
```
from sqlite_influx import Config, sqlite

measurements = {
  'test2': {
      'field3': 'data3'
  }
}
sqlite.store_dicts(measurements)
sqlite.sync_to_influx()
sqlite.archive(Config.config['archive_older_than_days'])
```

## Use Case

* Run on node (e.g. raspberry pi)
* Use autossh port forwarding to connect to remote InfluxDB
* Run example_app every X seconds
* Will sync measurements with InfluxDB, even if can not connect for some time (send all cached data from sqlite to remote InfluxDB)

## Setup

Autossh port forwarding to InfluxDB server
```
# add to /etc/rc.local before exit 0:

# do always restart autossh, even after failure
export AUTOSSH_GATETIME=0
# important, preserve variables when using sudo (-E)
sudo -E -u pi /usr/bin/autossh -M 19103 -oExitOnForwardFailure=yes -oStrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=1 -L 8086:localhost:8086 -N pi@plieninger.org &
```

Use crontab to run example app every 5 minutes
```
crontab -e

# add line
*/5 * * * * /usr/bin/python /path-to/sqlite_influx/example_app.py > /dev/null
```

## Run Tests or Example

```
docker-compose up
make test
python sqlite_influx/example_app.py
```
