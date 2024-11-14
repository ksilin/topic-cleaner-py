### play:

#### install dependencies

`uv sync`

#### start container

`docker compose up -d`

#### create topic

`uv run create_topic.py -t my_topic -p 1 -c fast_compact.props`


#### trail logs, look for log cleaner

`docker logs -f topic-cleaner-broker | grep -i cleaner`

#### watch log segments

```sh
docker container exec -it topic-cleaner-broker sh

> cd /var/lib/kafka/data/my_topic-0
> watch ls -la
```

#### produce data

`uv run serial_tombstone_prod.py --topic init4 --keys key1,key2,key3 --num_messages 500 --wait_time 100`

#### consume data

`uv run consume.py -t my_topic -m view -s 0.1`

#### additional info

See topic offsets:

`kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:29092 --topic my_topic --time -1`

Get topic configs:

`kafka-topics --bootstrap-server localhost:29092 --topic my_topic --describe`


### relevant configurations for compacted topics

#### Topic

`segment.bytes` - 1GB by default

`segment.ms` - 24h by default

`min.cleanable.dirty.ratio` - 

`min.compaction.lag.ms` - 

`max.compaction.lag.ms` - 


#### Log cleaner threads - broker

Not available on CCloud. 

`log.cleaner.backoff.ms` - 

`log.cleaner.threads` - 

`log.retention.check.interval.ms` - 

`log.cleaner.io.max.bytes.per.second` - 


### example for handling tombstones

```py
    if value is None:
        if key in state:
            logging.info(f"Removing key {key} from state due to tombstone message.")
            del state[key]
```

### reference

https://kafka.apache.org/documentation/#compaction