from api8inf349 import db, Product, Order , ProductOrder, ShippingInformation, ShippingOrder, CreditCard, CardOrder, Transaction, TransactionOrder,total_price,calc_weight
def test_total_price(client):
    assert total_price(50,3) == 150

def test_shipping_price(client):
    assert calc_weight(400) == 5
    assert calc_weight(1999) == 10
    assert calc_weight(2300) == 25    

class Test_Unit:
    def test_unit(self, client):
        test_total_price(client)
        test_shipping_price(client)