# FLASK_DEBUG=True FLASK_APP=inf349 python3 -m flask init-db
# FLASK_DEBUG=True FLASK_APP=inf349 python3 -m flask run
# http://dimprojetu.uqac.ca/~jgnault/shops/pay/

# batterie de test (unitaire, fonctionnel et d'intégration)
# trop de classe
# fusionner get et put

import json
import requests

from flask import Flask, jsonify, request, abort, redirect, url_for
import peewee as p
from playhouse.shortcuts import model_to_dict, dict_to_model

app = Flask(__name__)

db = p.SqliteDatabase("db.sqlite3")

class BaseModel(p.Model):
    class Meta:
        database = db

class Product (BaseModel):
    id = p.AutoField(primary_key=True)
    name = p.CharField(unique=True, null=False)
    type = p.CharField(null = False) 
    description = p.CharField()
    image = p.CharField(null=False)
    height = p.IntegerField(null = False)
    weight = p.IntegerField(null = False)
    price = p.DoubleField(null = False)
    in_stock = p.BooleanField(default=False)

class Order (BaseModel):
    id = p.AutoField(primary_key=True)
    total_price = p.FloatField(null = True)
    email = p.CharField(null = True)
    paid = p.BooleanField(default=False)
    shipping_price = p.IntegerField(null = True)

class ProductOrder(BaseModel):
    product_id = p.ForeignKeyField(Product, backref="product",null = False)
    order_id = p.ForeignKeyField(Order, backref="order_product",null = False)
    quantity = p.IntegerField(null = False)

class ShippingInformation(BaseModel):
    id = p.AutoField(primary_key=True)
    country = p.CharField(null = False)
    address = p.CharField(null = False)
    postal_code = p.CharField(null = False)
    city = p.CharField(null = False)
    province = p.CharField(null = False)

class ShippingOrder(BaseModel):
    shipping_id = p.ForeignKeyField(ShippingInformation, backref="shippingInformation",null = False)
    order_id = p.ForeignKeyField(Order, backref="order_shipping",null = False, unique = True)

class CreditCard(BaseModel):
    id = p.AutoField(primary_key=True)
    name = p.CharField(null = False)
    first_digits = p.CharField(null = False)
    last_digits = p.CharField(null = False)
    expiration_year = p.IntegerField(null = False)
    expiration_month = p.IntegerField(null = False)
   
class CardOrder(BaseModel):
    credit_card = p.ForeignKeyField(CreditCard, backref="creditCard")
    order_id = p.ForeignKeyField(Order, backref="order_card")

class Transaction(BaseModel):
    id = p.CharField(primary_key=True,null = False)
    success = p.BooleanField(null = False)
    amount_charged = p.DoubleField(null=False)

class TransactionOrder(BaseModel):
    transact_id = p.ForeignKeyField(Transaction, backref="transaction")
    order_id = p.ForeignKeyField(Order, backref="order_transact")

@app.route('/', methods=['GET']) 
def products_get():
    produits = Product.select()
    produits_array = []
    for produit in produits:
        produits_array.append(model_to_dict(produit))
    return jsonify(produits_array)

def total_price(prix, quantite):
    return prix * quantite

def calc_weight(weight):
    if weight <= 500:
        return 5
    elif weight <= 2000:
        return 10
    else:
        return 25

@app.route('/order', methods=['POST'])
def add_order():
    if not request.is_json:
        return jsonify({
            "errors" : {
                "product": {
                    "code": "missing-fields",
                    "name": "La création d'une commande nécessite un produit" 
                } 
            }
        }), 422
    
    json_payload = request.json['product']

    if json_payload['quantity'] < 1 :
        return jsonify({
            "errors" : {
                "product": {
                    "code": "missing-fields",
                    "name": "La création d'une commande nécessite un produit" 
                } 
            }
        }), 422


    new_order = Order.create()

    produits = Product.select()
    produits_array = []
    for produit in produits:
        produits_array.append(model_to_dict(produit)["id"])
    if not json_payload['id'] in produits_array :
        qry=Order.delete().where (Order.id==new_order.id)
        qry.execute()
        return jsonify({
            "errors" : {
                "product": {
                    "code": "missing-items",
                    "name": "Ce produit n'existe pas" 
                } 
            }
        }), 422


    new_product_order = ProductOrder.create(product_id = json_payload["id"], order_id = new_order.id, quantity = json_payload["quantity"])
    
    product = Product.get(Product.id == new_product_order.product_id)

    if product.in_stock == False:
        return jsonify({
            "errors" : {
                "product": {
                    "code": "out-of-inventory",
                    "name": "Le produit demandé n'est pas en inventaire" 
                } 
            }
        }), 422
    new_order.total_price = total_price(product.price,new_product_order.quantity)
    
    new_order.shipping_price = calc_weight(product.weight * new_product_order.quantity)

    new_product_order.save()
    new_order.save()

    return "Location: /order/{0}".format(new_order.id), 302
    
@app.route('/order/<int:id>', methods=['GET'])
def order_get(id):
    order = Order.get_or_none(id)
    if order is None:
        return abort(404)
    
    order = model_to_dict(order)

    try:
        product_order = ProductOrder.get(ProductOrder.order_id == id)
        product_order = model_to_dict(product_order)
        del product_order["order_id"]
        del product_order["id"]
        
        product = {
            "product" : {
            "id": product_order["product_id"]["id"],
            "quantity": product_order["quantity"]
            }
        }
        order.update(product)
    except:
        pass

    try:
        shipping_order = ShippingOrder.get(ShippingOrder.order_id == id)
        shipping_order = model_to_dict(shipping_order)
        del shipping_order["order_id"]
        del shipping_order["id"]
        del shipping_order["shipping_id"]["id"]
        shipping_order["shipping_information"] = shipping_order["shipping_id"]
        del shipping_order["shipping_id"]
        order.update(shipping_order)
    except:
        pass

    try:
        card_order = CardOrder.get(CardOrder.order_id == id)
        card_order = model_to_dict(card_order)
        del card_order["order_id"]
        del card_order["id"]
        del card_order["credit_card"]["id"]
        order.update(card_order)
    except:
        pass

    try:
        transac_order = TransactionOrder.get(TransactionOrder.order_id == id)
        transac_order = model_to_dict(transac_order)
        del transac_order["id"]
        del transac_order["order_id"]
        transac_order["transaction"] = transac_order["transact_id"]
        del transac_order["transact_id"]
        order.update(transac_order)
    except:
        pass

    return jsonify(order),200

@app.route('/order/<int:id>', methods=['PUT'])
def put_order(id):
    if not request.is_json:
        return abort(400)
    try:
        order = Order.get(Order.id == id)
    except:
        return jsonify({
            "errors" : {
                "order": {
                    "code": "missing-items",
                    "name": "La commande {0} n'existe pas".format(id) 
                } 
            }
        }), 422
    
    fr = list(request.json.keys())[0]
    if fr == "order":
        json_payload = request.json['order']
        try:
            order.email = json_payload["email"]        
        except:
            return jsonify({
            "errors" : {
                "order": {
                    "code": "missing-fields",
                    "name": "Le champ email est obligatoire" 
                } 
            }
        }), 400
        json_payload = json_payload["shipping_information"]
        try:
            shipping = ShippingInformation.create(country = json_payload["country"],address = json_payload["address"],postal_code = json_payload["postal_code"],city = json_payload["city"],province = json_payload["province"])
        except:
            return jsonify({
            "errors" : {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires" 
                } 
            }
        }), 422

        try:
            new_shipping_order = ShippingOrder.create(shipping_id = shipping.id, order_id = order.id)
        except:
            qry=ShippingInformation.delete().where (ShippingInformation.id==shipping.id)
            qry.execute()
            return jsonify({
            "errors" : {
                "order": {
                    "code": "unique-item",
                    "name": "Une adresse à déja été assigné à cette commande" 
                } 
            }
        }), 422
        new_shipping_order.save()
        shipping.save()
        order.save()

    elif fr == "credit_card":
        if order.email is None:
            return jsonify({
                "errors" : {
                    "order": {
                        "code": "missing-fields",
                        "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit" 
                    } 
                }
            }), 422
        json_payload = request.json['credit_card']
        try:
            number = json_payload["number"]
            first = number[0:4]
            last = number[-4:]
            card = CreditCard.create(name = json_payload["name"],first_digits = first,last_digits = last,expiration_year = json_payload["expiration_year"],expiration_month = json_payload["expiration_month"])
        except:
            return jsonify({
            "errors" : {
                "card": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires" 
                } 
            }
        }), 422
        new_card_order = CardOrder.create(credit_card = card.id, order_id = order.id)

        if order.paid:
            return jsonify({
                "errors" : {
                    "order": {
                        "code": "already-paid",
                        "name": "La commande a déjà été payée" 
                    } 
                }
            }), 422
        amount_charged = order.shipping_price + order.total_price
        amount_charged = {'amount_charged':amount_charged}
        data = model_to_dict(card)
        data.update(amount_charged)

        card_order = CardOrder.get(CardOrder.order_id == id)
        card_order = model_to_dict(card_order)

        del card_order["order_id"]
        del card_order["id"]
        del card_order["credit_card"]["id"]
        card_order.update(amount_charged)
        del card_order["credit_card"]["first_digits"]
        del card_order["credit_card"]["last_digits"]
        card_order["credit_card"]["number"] = json_payload["number"]
        card_order["credit_card"]["cvv"] = json_payload["cvv"]
        
        data = json.dumps(card_order)
        url = "http://dimprojetu.uqac.ca/~jgnault/shops/pay/"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        
        response = requests.post(url, headers=headers, data=data)
        
        json_payload = response.json()
        cle = list(json_payload)[0]
        if cle == "errors":
            qry=CardOrder.delete().where (CardOrder.order_id==card.id)
            qry.execute()
            qry=CreditCard.delete().where (CreditCard.id==card.id)
            qry.execute()
            return jsonify({
                "errors" : {
                    "order": {
                        "code": "card-declined",
                        "name": "La carte de crédit a été déclinée." 
                    } 
                }
            }), 422

        json_payload = json_payload["transaction"]
        order.paid = json_payload["success"]

        
        
        transact = Transaction.create(id = json_payload["id"],success = json_payload["success"],amount_charged = json_payload["amount_charged"])
        transacOrder = TransactionOrder.create(transact_id = transact.id,order_id = order.id)
        transact.save()
        transacOrder.save()
        new_card_order.save()
        card.save()
        order.save()

    return redirect(url_for("order_get", id=order.id))
    
def remplir_base():
    url = "http://dimprojetu.uqac.ca/~jgnault/shops/products/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.get(url, headers=headers)
    json_payload = response.json()
    for product in json_payload["products"]:
        product['id'] = None
        new = dict_to_model(Product,product)
        new.save()

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.drop_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    db.create_tables([Product,Order,ProductOrder,ShippingInformation,ShippingOrder,CreditCard,CardOrder,Transaction,TransactionOrder])
    remplir_base()