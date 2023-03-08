# conftest file for pytest to set up the test environment
# we use the flask test client to make requests to the app
# we initialize flask and peewee

import pytest

from Api import client as api


@pytest.fixture
def client():
    api.app.config['TESTING'] = True
    client = api.app.test_client()
    api.Database.create_db()
    yield client
    api.Database.delete_db()


@pytest.fixture
def runner():
    return client.test_cli_runner()