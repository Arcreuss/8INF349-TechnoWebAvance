from inf349 import app, db, BaseModel, Product, Order , ProductOrder, ShippingInformation, ShippingOrder, CreditCard, CardOrder, Transaction, TransactionOrder,remplir_base

def init_db():
    db.connect()
    db.drop_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    db.create_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    remplir_base()


class TestOrder():
    def test_populate_database(self):
        assert Product.select().count() == 50

    def test_create_order(self, client):
        # create order
        order = Order.create()
        assert order.id == 1
        assert order.shipping_info is None
        assert order.credit_card is None
        assert order.transaction is None
        assert order.order_products == []



