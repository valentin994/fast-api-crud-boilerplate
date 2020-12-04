import pytest
import requests
import os

os.environ['NO_PROXY'] = '127.0.0.1'

def test_api_get_all_users():
    r = requests.get("http://127.0.0.1:5000/user")
    assert r.status_code == 200
  
def test_api_post_user():
    user = {
        "name": "John Doe",
        "email": "johndoe@gmail.com",
        "password": "password123"
    }
    r = requests.post("http://127.0.0.1:5000/user", json=user)
    assert r.status_code == 200
    
def test_api_get_by_email():
    r = requests.get("http://127.0.0.1:5000/user/johndoe@gmail.com")
    assert r.status_code == 200