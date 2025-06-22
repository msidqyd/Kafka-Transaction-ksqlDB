# Kafka Transaction Streaming with ksqlDB

This project sends fake transaction data events to Kafka topic `transactions`, reads it with a consumer, and aggregates it in ksqlDB.

---

## Setup

- Clone this repo
- Make Docker Build
- Make Kafka
- Make Jupyter
- Open Jupyter Notebook: `producer-transaction.py` & `consumer-transaction.py`

---

## Kafka Producer

Sends fake transaction events into Kafka topic `transactions`, with fields:

- transaction_id
- user_id
- account_id
- transaction_timestamp
- transaction_amount
- transaction_type
- merchant_category
- merchant_country
- device_id
- ip_address
- is_fraud

---

## Kafka Consumer

Consumes messages from Kafka topic `transactions`:

```python
consumer = KafkaConsumer(
    'transactions',
    group_id='transaction-group',
    bootstrap_servers=[f'{kafka_host}:9092']
)

for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
```

## For run the ksqlDB, open localhost:8083
## ksqlDB Stream
```SQL
CREATE STREAM transactions_stream (
    transaction_id INT,
    user_id INT,
    account_id STRING,
    transaction_timestamp STRING,
    transaction_amount BIGINT,
    transaction_type STRING,
    merchant_category STRING,
    merchant_country STRING,
    device_id STRING,
    ip_address STRING,
    is_fraud INT
) WITH (
    KAFKA_TOPIC = 'transactions',
    VALUE_FORMAT = 'JSON'
);
```
## ksqlDB Table (aggregation)

```SQL
CREATE TABLE user_agg_total AS
SELECT
    user_id,
    COUNT(*) AS total_transactions,
    SUM(transaction_amount) AS total_amount,
    SUM(is_fraud) AS total_fraud_count
FROM transactions_stream
GROUP BY user_id
EMIT CHANGES;
```

## Query The Table
``` SQL
SELECT * FROM user_agg_total EMIT CHANGES;
```

