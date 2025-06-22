from faker import Faker
import random
import uuid
import json
from kafka import KafkaProducer
from time import sleep
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load environment variables
dotenv_path = Path("/opt/app/.env")
load_dotenv(dotenv_path=dotenv_path)
kafka_host = os.getenv('KAFKA_HOST')
kafka_topic_partition = os.getenv('KAFKA_TOPIC_NAME') + "-1"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=f'{kafka_host}:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"Kafka Producer connected: {producer}")

faker = Faker()

# Memory to track user last country and last transaction date
user_last_country_map = {}
user_transaction_date_count = {}

class DataGenerator(object):
    @staticmethod
    def calculate_fraud_score(amount, current_country, user_id, last_country, transaction_date, user_transaction_date_count):
        score = 0

        # Big amount → suspicious
        if amount > 1_000_000:
            score += 0.3
        
        # Country changed → suspicious
        if current_country != last_country:
            score += 0.4

        # Check if user already transacted today
        key = (user_id, transaction_date)
        count = user_transaction_date_count.get(key, 0)
        if count >= 3:  # If user already did 3+ transactions today → suspicious
            score += 0.2

        # Add randomness
        score += random.uniform(0, 0.1)

        return 1 if score > 0.5 else 0

    @staticmethod
    def transaction_data(user_last_country_map, user_transaction_date_count):
        user_id = random.randint(1, 50)
        merchant_country = random.choice(['US', 'UK', 'SG', 'JP', 'ID'])
        amount = random.randint(5, 10_000_000_000)

        # Get previous country
        last_country = user_last_country_map.get(user_id, 'ID')

        # Generate transaction timestamp
        transaction_datetime = faker.date_time_between(start_date="now", end_date="+3m")
        transaction_timestamp = str(transaction_datetime)
        transaction_date = transaction_datetime.date().isoformat()  # YYYY-MM-DD

        # Calculate fraud
        is_fraud = DataGenerator.calculate_fraud_score(
            amount, merchant_country, user_id, last_country, transaction_date, user_transaction_date_count
        )

        # Update user_last_country_map
        user_last_country_map[user_id] = merchant_country

        # Update transaction count for this day
        key = (user_id, transaction_date)
        user_transaction_date_count[key] = user_transaction_date_count.get(key, 0) + 1

        return [
            random.randint(1, 2000),                       # transaction_id
            user_id,                                       # user_id
            str(uuid.uuid4()),                             # account_id
            transaction_timestamp,                         # transaction_timestamp
            amount,                                        # transaction_amount
            random.choice(['debit', 'credit', 'transfer']),# transaction_type
            random.choice(['grocery', 'fuel', 'electronics', 'travel', 'online_store', 'restaurant']), # merchant_category
            merchant_country,                              # merchant_country
            str(uuid.uuid4()),                             # device_id
            faker.ipv4_public(),                           # ip_address
            is_fraud                                       # is_fraud
        ]

if __name__ == '__main__':
    
    topic_name = 'transactions'

    columns = [
        'transaction_id',
        'user_id',
        'account_id',
        'transaction_timestamp',
        'transaction_amount',
        'transaction_type',
        'merchant_category',
        'merchant_country',
        'device_id',
        'ip_address',
        'is_fraud'
    ]

    for i in range(1, 2000):
        list_transaction = DataGenerator.transaction_data(user_last_country_map, user_transaction_date_count)
        json_data = dict(zip(columns, list_transaction))
        
        # Send message
        response = producer.send(topic=topic_name, value=json_data)
        print(f"Sent: {json_data['transaction_id']} | Fraud: {json_data['is_fraud']} | Response: {response.get()}")
        
        sleep(5) 
