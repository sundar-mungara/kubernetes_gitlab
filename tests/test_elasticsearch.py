import pytest
import requests
import os
import time
from elasticsearch import Elasticsearch

# Configuration
ELASTICSEARCH_NODE_PORT = 30200
INDEX_NAME = "test-results"

def get_elasticsearch_host():
    """Get Elasticsearch host from Kubernetes service"""
    node_ip = os.getenv("KUBERNETES_NODE_IP", "localhost")
    return f"http://{node_ip}:{ELASTICSEARCH_NODE_PORT}"

@pytest.fixture(scope="module")
def es_client():
    """Create an Elasticsearch client"""
    max_retries = 30
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            es = Elasticsearch([get_elasticsearch_host()])
            if es.ping():
                yield es
                break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

@pytest.fixture(scope="module", autouse=True)
def setup_elasticsearch(es_client):
    """Setup Elasticsearch index and insert test data"""
    # Wait for Elasticsearch to be ready
    time.sleep(10)
    
    # Create index with mapping
    mapping = {
        "mappings": {
            "properties": {
                "test_id": {"type": "keyword"},
                "name": {"type": "text"},
                "status": {"type": "keyword"},
                "duration_ms": {"type": "integer"},
                "timestamp": {"type": "date"}
            }
        }
    }
    
    if not es_client.indices.exists(index=INDEX_NAME):
        try:
            # Try new API first (8.x)
            es_client.indices.create(index=INDEX_NAME, mappings=mapping["mappings"])
        except TypeError:
            # Fallback to old API (7.x)
            es_client.indices.create(index=INDEX_NAME, body=mapping)
    
    # Insert three test records
    test_records = [
        {
            "test_id": "VAFT-002",
            "name": "Test Case 2",
            "status": "fail",
            "duration_ms": 150,
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "test_id": "VAFT-003",
            "name": "Test Case 3",
            "status": "pass",
            "duration_ms": 200,
            "timestamp": "2024-01-01T10:01:00Z"
        },
        {
            "test_id": "VAFT-004",
            "name": "Test Case 4",
            "status": "pass",
            "duration_ms": 180,
            "timestamp": "2024-01-01T10:02:00Z"
        }
    ]
    
    for i, record in enumerate(test_records):
        try:
            # Try new API first (8.x)
            es_client.index(index=INDEX_NAME, id=i+1, document=record)
        except TypeError:
            # Fallback to old API (7.x)
            es_client.index(index=INDEX_NAME, id=i+1, body=record)
    
    # Refresh index to make documents searchable
    es_client.indices.refresh(index=INDEX_NAME)
    
    yield
    
    # Cleanup (optional)
    # es_client.indices.delete(index=INDEX_NAME, ignore=[404])

def test_elasticsearch_connection(es_client):
    """Test Elasticsearch connection"""
    assert es_client.ping(), "Elasticsearch should be reachable"

def test_elasticsearch_index_exists(es_client):
    """Verify test-results index exists"""
    assert es_client.indices.exists(index=INDEX_NAME), f"Index '{INDEX_NAME}' should exist"

def test_elasticsearch_query_vaft_004(es_client):
    """Test 2: Query for test_id='VAFT-004' and assert status is 'pass'"""
    query = {
        "query": {
            "term": {
                "test_id": "VAFT-004"
            }
        }
    }
    
    try:
        # Try new API first (8.x)
        response = es_client.search(index=INDEX_NAME, query=query["query"])
    except TypeError:
        # Fallback to old API (7.x)
        response = es_client.search(index=INDEX_NAME, body=query)
    
    assert response["hits"]["total"]["value"] > 0, "Should find at least one document with test_id='VAFT-004'"
    
    hits = response["hits"]["hits"]
    assert len(hits) > 0, "Should have at least one hit"
    
    document = hits[0]["_source"]
    assert document["test_id"] == "VAFT-004", f"test_id should be 'VAFT-004', got '{document['test_id']}'"
    assert document["status"] == "pass", f"status should be 'pass', got '{document['status']}'"

