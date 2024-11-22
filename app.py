from flask import Flask, jsonify, request
import os
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI') 

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')  # Verify connection
    print("Database connected successfully.")
    db = client["FoodDeliveryApp"]
    users = db["user"]
    menus = db["menu"]
    orders = db["order"]
except ConnectionFailure:
    print("Failed to connect to the database.")


################## Admin Section #################
# Admin Get all user details
@app.route('/admin/all_users', methods=['GET'])
def get_all_users_admin():
    try:
        all_users = list(users.find({}))
        for user in all_users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify({"msg": "All users retrieved successfully", "users": all_users}), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving users", "error": str(e)}), 500

# admin get all restaurant
@app.route('/admin/all_restaurants', methods=['GET'])
def get_all_restaurants_admin():
    try:
        all_restaurants = list(menus.find({}))
        for restaurant in all_restaurants:
            restaurant['_id'] = str(restaurant['_id'])
            restaurant['restaurant_id'] = str(restaurant['restaurant_id'])
        return jsonify({"msg": "All restaurants retrieved successfully", "restaurants": all_restaurants}), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving restaurants", "error": str(e)}), 500

# admin get all orders
@app.route('/admin/all_orders', methods=['GET'])
def get_all_orders_admin():
    try:
        all_orders = list(orders.find({}))
        for order in all_orders:
            order['_id'] = str(order['_id'])
            order['user_id'] = str(order['user_id'])
            order['restaurant_id'] = str(order['restaurant_id'])
            order['delivery_person_id'] = str(order['delivery_person_id'])
        return jsonify({"msg": "All orders retrieved successfully", "orders": all_orders}), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving orders", "error": str(e)}), 500

# Admin delete user
@app.route('/admin/user/<user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    try:
        result = users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({"msg": "User deleted successfully", "user_id": user_id}), 200
        else:
            return jsonify({"msg": "User not found"}), 404
    except Exception as e:
        return jsonify({"msg": "Error deleting user", "error": str(e)}), 500

#Admin delete restaurant
@app.route('/admin/restaurant/<restaurant_id>', methods=['DELETE'])
def admin_delete_restaurant(restaurant_id):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(restaurant_id):
            return jsonify({"msg": "Invalid restaurant ID"}), 400
        
        # Convert string to ObjectId
        restaurant_object_id = ObjectId(restaurant_id)
        
        # Delete from users collection (assuming _id matches restaurant_id)
        user_result = users.delete_one({"_id": restaurant_object_id, "role": "restaurant_owner"})
        
        # Delete from menus collection (using restaurant_id reference)
        menu_result = menus.delete_many({"restaurant_id": restaurant_object_id})
        
        # Check if anything was deleted
        if user_result.deleted_count > 0 or menu_result.deleted_count > 0:
            return jsonify({
                "msg": "Restaurant deleted successfully",
                "user_deleted": user_result.deleted_count,
                "menu_entries_deleted": menu_result.deleted_count,
                "restaurant_id": restaurant_id
            }), 200
        else:
            return jsonify({"msg": "Restaurant not found"}), 404
    except Exception as e:
        app.logger.error(f"Error deleting restaurant: {e}")
        return jsonify({"msg": "Error deleting restaurant", "error": str(e)}), 500

# Admin delete order
@app.route('/admin/order/<order_id>', methods=['DELETE'])
def admin_delete_order(order_id):
    try:
        result = orders.delete_one({"_id": ObjectId(order_id)})
        if result.deleted_count > 0:
            return jsonify({"msg": "Order deleted successfully", "order_id": order_id}), 200
        else:
            return jsonify({"msg": "Order not found"}), 404
    except Exception as e:
        return jsonify({"msg": "Error deleting order", "error": str(e)}), 500


# Start the Flask app
if __name__ == "__main__":
    print("Starting the server...")
    app.run(host="0.0.0.0", port=8080, debug=True)
