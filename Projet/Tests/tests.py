def create_order(client):
    response = client.post('/order', json={
        'product': {
            'id': 1,
            'quantity': 10
        }
    })
    assert response.status_code == 302