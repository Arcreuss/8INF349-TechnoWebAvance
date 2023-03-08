# conftest file for pytest to set up the test environment
# we use the flask test client to make requests to the app
# we initialize flask and peewee

import pytest

from inf349 import app, db, BaseModel, Product, Order , ProductOrder, ShippingInformation, ShippingOrder, CreditCard, CardOrder, Transaction, TransactionOrder,remplir_base

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    
    db.connect()
    db.create_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    remplir_base()

    yield client

    db.drop_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    db.close()


@pytest.fixture
def runner():
    return client.test_cli_runner()