from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

def get_elasticsearch():
    return Elasticsearch(
        [{
            'host': os.getenv("ELASTICSEARCH_HOST"),
            'port': int(os.getenv("ELASTICSEARCH_PORT")),
            'scheme': 'http'
        }]
    )
