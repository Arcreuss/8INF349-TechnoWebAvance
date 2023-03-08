from inf349 import db, Product, Order , ProductOrder, ShippingInformation, ShippingOrder, CreditCard, CardOrder, Transaction, TransactionOrder,remplir_base

class TestOrder():
    def test_remplir_base(self):
        product = Product.select()
        # assert product.count() == 50

    def test_create_order(self, client):
        order = Order.create()
        assert order.id == 1