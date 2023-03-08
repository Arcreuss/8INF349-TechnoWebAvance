def create_order(client):
    response = client.post('/order', json={
        'product': {
            'id': 23,
            'quantity': 2
        }
    })
    assert response.status_code == 302

def put_valid_shipping_info(client):
    response = client.put('/order/1', json={ "order" : { 
        "email" : "jgnault@uqac.ca", 
        "shipping_information" : { 
            "country" : "Canada", 
            "address" : "201, rue Président-Kennedy", 
            "postal_code" : "G7X 3Y7", 
            "city" : "Chicoutimi", 
            "province" : "QC" } 
            } 
        })
    assert response.status_code == 302


def put_valid_credit_card(client):
    response = client.put('/order/1', json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 302


def check_order(client):
    response = client.get('/order/1')
    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["total_price"] == 45.4

class TestGetOrder:
    def test_get_order(self, client):
        create_order(client)
        put_valid_shipping_info(client) 
        put_valid_credit_card(client)
        response = client.get('/order/1')
        assert response.status_code == 200
        check_order(client)