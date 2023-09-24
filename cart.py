import requests
from flask import Flask, jsonify, request
app = Flask(__name__)

def get_product(product_id):
    response = requests.get(f'https://product-service-96lf.onrender.com/products/{product_id}')
    data = response.json()
    return data 

def add_product(product_id, quantity):
    product = {"quantity": quantity}
    response = requests.post(f'https://product-service-96lf.onrender.com/products/add/{product_id}', json=product)
    data = response.json()
    return data
def remove_product(product_id, quantity):
    product = {"quantity": quantity}
    response = requests.post(f'https://product-service-96lf.onrender.com/products/remove/{product_id}', json=product)
    data = response.json()
    return data

# # Cart Model
# class Cart(db.Model):
#     id = db.Column(db.Interger, primary_key=True)
#     product_name = db.Column(db.String(100))
#     product_quantity = db.Column(db.Interger)
#     total_price = db.Column(db.Float)

# Sample Cart Data
carts = [
    {"id": 1, "products": []},
    {"id": 2, "products": []},
    {"id": 3, "products": []},
    {"id": 4, "products": []},
    {"id": 5, "products": []}
]


# Endpoint 1: Get all products in cart by User's ID
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = next((cart for cart in carts if cart["id"] == user_id), None)
    if cart:
        return jsonify({"id": cart["id"], "products": cart["products"]})
    else:
        return jsonify({"error": "User not found"}), 404
    
# Endpoint 2: Add a specified quantity of a product to the cart
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_product_into_cart(user_id, product_id):
    # Get request data
    add_quantity = request.json.get('quantity')
    # Get data from product service
    product = get_product(product_id)['product']
    productName = product.get('name')
    product_price = product.get('price')
    # Add data into cart
    cart = next((cart for cart in carts if cart["id"] == user_id), None)
    if cart:
        cart_product = next((product for product in cart["products"] if product["product_name"] == productName), None)
        if cart_product:
            cart_product["product_quantity"] = str(int(cart_product["product_quantity"]) + int(add_quantity))
            cart_product["total_price"] = str(float(cart_product["product_quantity"])*float(product_price))
        else:
            total_price = float(product_price)*float(add_quantity)
            product = {
                "product_name": productName,
                "product_quantity": add_quantity,
                "total_price": str(total_price)
            }
            cart["products"].append(product)
        # Reduce the product's quantity after adding product
        remove_product(product_id, add_quantity)
        return jsonify({"message": "Product is added into cart", "cart_products": cart})
    else:
        return jsonify({"error": "User not found"})

# Endpoint 3: Remove a specified quantity of a product from the cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_product_from_cart(user_id, product_id):
    # Get request data
    remove_quantity = request.json.get('quantity')
    # Get data from product service
    product_data = get_product(product_id)['product']
    productName = product_data.get('name')
    product_price = product_data.get('price')
    # Add data into cart
    cart = next((cart for cart in carts if cart["id"] == user_id), None)
    # Check if the cart ID is correct
    if cart:
        # Check if the cart is empty or not
        if cart["products"]:
            cart_product = next((product for product in cart["products"] if product["product_name"] == productName), None)
            # Check if the product is in the cart 
            if cart_product:
                # Check if the quantity is more than cart's quantity
                if(int(cart_product["product_quantity"]) < int(remove_quantity)):
                    return jsonify({"error": "The remove quantity is larger than cart's quantity"})
                cart_product["product_quantity"] = str(int(cart_product["product_quantity"]) - int(remove_quantity)) 
                total_price = float(product_price)*float(cart_product["product_quantity"])
                cart_product["total_price"] = str(total_price)
                if int(cart_product["product_quantity"]) == 0:
                    cart["products"].remove(cart_product)
            else:
                return jsonify({"error": "Product is not in cart"}), 404
        # Add the product's quantity back after removing product's quantity
            add_product(product_id, remove_quantity)
            return jsonify({"message": "Product quantity is removed from cart", "cart_products": cart})
        else:
            return jsonify({"error": "Cart is empty"}), 404
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True, port=5001)

    