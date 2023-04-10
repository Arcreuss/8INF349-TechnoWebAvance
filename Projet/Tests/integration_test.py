from api8inf349 import db, Product, Order , ProductOrder, ShippingInformation, ShippingOrder, CreditCard, CardOrder, Transaction, TransactionOrder,remplir_base,total_price,calc_weight

def test_remplir_base():
    product = Product.select()
    assert len(product) == 50

def test_database(client):
    order = Order.create()
    assert order.id == 1
    product = Product.get(Product.id == 1)
    product_order = ProductOrder.create(product_id = product.id, order_id = order.id, quantity = 15)
    order.total_price = total_price(product.price,product_order.quantity)
    order.shipping_price = calc_weight(product.weight * product_order.quantity)
    shipping = ShippingInformation.create(country = "Canada",address = "201, rue Président-Kennedy",postal_code = "G7X 3Y7",city = "Chicoutimi",province = "QC")
    shipping_order = ShippingOrder.create(shipping_id = shipping.id, order_id = order.id)
    card = CreditCard.create(name = "John Doe",first_digits = "4242",last_digits = "4242",expiration_year = 2024,expiration_month = 9)
    card_order = CardOrder.create(credit_card = card.id, order_id = order.id)
    order.save()
    product.save()
    product_order.save()
    shipping.save()
    shipping_order.save()
    card.save()
    card_order.save()
    assert order.id == Order.get(Order.id == 1)
    assert product == Product.get(Product.id == 1)
    assert product_order == ProductOrder.get(ProductOrder.id == 1)
    assert shipping == ShippingInformation.get(ShippingInformation.id == 1)
    assert shipping_order == ShippingOrder.get(ShippingOrder.id == 1)
    assert card_order == CreditCard.get(CreditCard.id == 1)
    assert card == CardOrder.get(CardOrder.id == 1)