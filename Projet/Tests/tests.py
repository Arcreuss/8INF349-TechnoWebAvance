def create_order(client):
    response = client.post('/order', json={
        'product': {
            'id': 1,
            'quantity': 10
        }
    })
    assert response.status_code == 302

class TestGetOrder:
    def test_get_order(self, client):
        create_order(client)
        response = client.get('/order/1')
        assert response.status_code == 200