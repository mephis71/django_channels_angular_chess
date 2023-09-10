import os
from http.cookies import SimpleCookie
from uuid import uuid4

import pytest
from django.contrib.auth import authenticate


@pytest.fixture(autouse=True)
def _always_use_db(db):
    """To avoid having to use db fixture in every test."""


@pytest.fixture
def admin_client(client, django_user_model):
    """Test client for jwt"""
    username = "user1"
    password = "bar"
    django_user_model.objects.create_superuser(username=username, password=password)
    authenticated_user = authenticate(username=username, password=password)
    client.cookies = SimpleCookie({"jwt": authenticated_user.token})
    return client


@pytest.fixture
def game_file_path() -> str:
    game_file_path = f"/tmp/game_{uuid4()}"
    yield game_file_path

    if os.path.exists(game_file_path):
        os.remove(game_file_path)
