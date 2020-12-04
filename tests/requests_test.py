import pytest
import requests
import os

os.environ['NO_PROXY'] = '127.0.0.1'

def test_api_crud():
    r = requests.get("http://127.0.0.1:5000/user")
    assert r.status_code == 200
  
    
