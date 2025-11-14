import pytest
import requests
import os
import time

# Configuration
NGINX_NODE_PORT = 30080

def get_nginx_url():
    """Get Nginx URL from Kubernetes service"""
    node_ip = os.getenv("KUBERNETES_NODE_IP", "localhost")
    return f"http://{node_ip}:{NGINX_NODE_PORT}"

@pytest.fixture(scope="module")
def nginx_available():
    """Wait for Nginx to be available"""
    max_retries = 30
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(get_nginx_url(), timeout=5)
            if response.status_code == 200:
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise
    
    return False

def test_nginx_connection(nginx_available):
    """Test 3: Connect to Nginx NodePort"""
    assert nginx_available, "Nginx should be available"

def test_nginx_default_page(nginx_available):
    """Test 3: Fetch the default HTML page and verify it contains 'Welcome to nginx'"""
    response = requests.get(get_nginx_url(), timeout=10)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    html_content = response.text
    assert "Welcome to nginx" in html_content, "HTML page should contain 'Welcome to nginx'"

