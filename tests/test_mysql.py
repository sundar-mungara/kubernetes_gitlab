import pytest
import pymysql
import os
import time

# Configuration
MYSQL_NODE_PORT = 30306
MYSQL_USER = "root"
MYSQL_PASSWORD = "rootpassword"
MYSQL_DATABASE = "testdb"

def get_mysql_host():
    """Get MySQL host from Kubernetes service or use localhost for testing"""
    # In a real scenario, you'd get the node IP from kubectl
    # For now, we'll use an environment variable or default to localhost
    node_ip = os.getenv("KUBERNETES_NODE_IP", "localhost")
    return node_ip

@pytest.fixture(scope="module")
def mysql_connection():
    """Create a MySQL connection"""
    max_retries = 30
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(
                host=get_mysql_host(),
                port=MYSQL_NODE_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connect_timeout=10
            )
            yield connection
            connection.close()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def test_mysql_connection(mysql_connection):
    """Test 1: Connect to MySQL using NodePort"""
    assert mysql_connection is not None
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
    cursor.close()

def test_mysql_database_exists(mysql_connection):
    """Verify testdb database exists"""
    cursor = mysql_connection.cursor()
    cursor.execute("SHOW DATABASES LIKE 'testdb'")
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "testdb"
    cursor.close()

def test_mysql_table_exists(mysql_connection):
    """Verify results table exists"""
    cursor = mysql_connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'results'")
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "results"
    cursor.close()

def test_mysql_table_structure(mysql_connection):
    """Verify table structure"""
    cursor = mysql_connection.cursor()
    cursor.execute("DESCRIBE results")
    columns = cursor.fetchall()
    
    column_names = [col[0] for col in columns]
    assert "id" in column_names
    assert "test_id" in column_names
    assert "status" in column_names
    assert "executed_at" in column_names
    cursor.close()

def test_mysql_record_exists(mysql_connection):
    """Test 1: Query the record and verify data is correct"""
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT id, test_id, status, executed_at FROM results WHERE test_id = 'VAFT-001'")
    result = cursor.fetchone()
    
    assert result is not None, "Record with test_id='VAFT-001' should exist"
    assert result[1] == "VAFT-001", f"test_id should be 'VAFT-001', got '{result[1]}'"
    assert result[2] == "pass", f"status should be 'pass', got '{result[2]}'"
    assert result[0] is not None, "id should not be None"
    assert result[3] is not None, "executed_at should not be None"
    
    cursor.close()

