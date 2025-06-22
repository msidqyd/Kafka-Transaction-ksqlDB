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

![Screenshot 2025-06-22 220636](https://github.com/user-attachments/assets/d79f91e2-eb19-4872-b85d-27098c26f9d5)


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
![Screenshot 2025-06-22 220649](https://github.com/user-attachments/assets/b459ab1e-6ce4-4808-bba9-3a6919a4a02e)

## For run the ksqlDB, open localhost:8083

## Setup Topic
![Screenshot 2025-06-22 212359](https://github.com/user-attachments/assets/b728c49d-deb5-4cbb-9e0e-15f5a04569b2)


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
![Screenshot 2025-06-22 213827](https://github.com/user-attachments/assets/577428d0-9d1d-4c35-b233-604b6aa646b9)
![Screenshot 2025-06-22 214121](https://github.com/user-attachments/assets/b57bbdfb-cce6-4031-a325-baab61a435ff)

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
![Screenshot 2025-06-22 214158](https://github.com/user-attachments/assets/8bd95050-0d66-4fe5-ae66-d1b69fdb4f00)

## Query The Table
``` SQL
SELECT * FROM user_agg_total EMIT CHANGES;
```
![Screenshot 2025-06-22 214330](https://github.com/user-attachments/assets/90fda1fe-bd82-4f43-b5df-4c09e1b680d0)

