import pytest
import requests
import os

# Tests have to be made again from the beggining


def test_api_get_all_users_with_no_user_registered():
    r = requests.get("http://localhost:8000/user")
    assert True
