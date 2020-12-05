import pytest
import requests
import os

os.environ["NO_PROXY"] = "127.0.0.1"


def test_api_get_all_users_with_no_user_registered():
    r = requests.get("http://127.0.0.1:5000/user")
    assert r.status_code == 404


def test_api_post_user():
    user = {"name": "John Doe", "email": "johndoes@example.com", "password": "password"}
    r = requests.post("http://127.0.0.1:5000/user/", json=user)
    assert r.status_code == 200


def test_api_get_all_users_with_user_registered():
    r = requests.get("http://127.0.0.1:5000/user")
    assert r.status_code == 200


def test_api_try_to_create_same_user():
    user = {
        "name": "John Doe",
        "email": "johndoes@example.com",
        "password": "password123",
    }
    r = requests.post("http://127.0.0.1:5000/user/", json=user)
    assert r.status_code == 400


def test_api_get_by_email():
    r = requests.get("http://127.0.0.1:5000/user/johndoes@example.com")
    assert r.status_code == 200


def test_api_update_existing_user():
    user = {"name": "Marko Markic"}
    r = requests.put("http://127.0.0.1:5000/user/johndoes@example.com", json=user)
    assert r.status_code == 200


def test_api_update_non_existant_user():
    user = {"name": "Marko Markic"}
    r = requests.put("http://127.0.0.1:5000/user/idonotexist@example.com", json=user)
    assert r.status_code == 404


def test_api_delete_user():
    r = requests.delete("http://127.0.0.1:5000/user/johndoes@example.com")
    assert r.status_code == 200


def test_api_delete_non_existing_user():
    r = requests.delete("http://127.0.0.1:5000/user/idonotexist@example.com")
    assert r.status_code == 404
