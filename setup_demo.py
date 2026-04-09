"""
Demo setup script for Live Delivery Tracking
Creates test users and demonstrates the tracking system
"""

from app import app, db, User, Shop, Order, OrderItem, Item
from passlib.hash import pbkdf2_sha256
from datetime import datetime

def create_demo_users():
    """Create demo users for testing live tracking"""

    print("🚚 Setting up Live Delivery Tracking Demo")
    print("=" * 50)

    with app.app_context():
        try:
            # Clear existing demo users
            demo_emails = ['deliverydemo@gmail.com', 'customerdemo@gmail.com', 'shopdemo@gmail.com']
            User.query.filter(User.email.in_(demo_emails)).delete()
            db.session.commit()

            # Create delivery person
            delivery = User(
                name="John Delivery",
                email="deliverydemo@gmail.com",
                role="delivery",
                vehicle_number="DL-01-AB-1234",
                address="Delhi, India",
                phone="9876543210"
            )
            delivery.set_password("password123")
            db.session.add(delivery)
            db.session.flush()  # Get the ID
            print(f"✅ Created delivery person: {delivery.name} (ID: {delivery.id})")

            # Create customer
            customer = User(
                name="Alice Customer",
                email="customerdemo@gmail.com",
                role="customer",
                address="Connaught Place, Delhi",
                phone="9876543211"
            )
            customer.set_password("password123")
            db.session.add(customer)
            db.session.flush()
            print(f"✅ Created customer: {customer.name} (ID: {customer.id})")

            # Create shopkeeper
            shopkeeper = User(
                name="Bob Shop",
                email="shopdemo@gmail.com",
                role="shopkeeper",
                shop_name="Bob's Grocery",
                phone="9876543212"
            )
            shopkeeper.set_password("password123")
            db.session.add(shopkeeper)
            db.session.flush()
            print(f"✅ Created shopkeeper: {shopkeeper.name} (ID: {shopkeeper.id})")

            # Create shop
            shop = Shop(
                owner_id=shopkeeper.id,
                name="Bob's Grocery Store",
                description="Fresh groceries and daily essentials",
                latitude=28.7041,
                longitude=77.1025
            )
            db.session.add(shop)
            db.session.flush()
            print(f"✅ Created shop: {shop.name} (ID: {shop.id})")

            # Create some items
            items_data = [
                ("Milk", "Fresh cow milk", 50.0),
                ("Bread", "Whole wheat bread", 30.0),
                ("Eggs", "Farm fresh eggs", 60.0),
                ("Rice", "Premium basmati rice", 80.0)
            ]

            for name, desc, price in items_data:
                item = Item(shop_id=shop.id, name=name, description=desc, price=price)
                db.session.add(item)

            print("✅ Created sample items")

            # Create a sample order
            order = Order(
                customer_id=customer.id,
                shop_id=shop.id,
                code="DEMO001",
                payment_method="Cash on Delivery",
                status="On the way",
                total_amount=140.0,
                delivery_lat=28.6139,  # Connaught Place
                delivery_lng=77.2090,
                pickup_lat=28.7041,    # Shop location
                pickup_lng=77.1025,
                delivery_id=delivery.id,
                eta=datetime.utcnow()
            )
            db.session.add(order)
            db.session.flush()
            print(f"✅ Created sample order: {order.code} (ID: {order.id})")

            # Add order items
            order_items = [
                (1, 2, 50.0),  # 2 Milk
                (2, 1, 30.0),  # 1 Bread
                (3, 1, 60.0)   # 1 Eggs
            ]

            for item_id_offset, qty, price in order_items:
                # Get actual item ID (offset from first item)
                item = Item.query.filter_by(shop_id=shop.id).offset(item_id_offset-1).first()
                if item:
                    order_item = OrderItem(
                        order_id=order.id,
                        item_id=item.id,
                        quantity=qty,
                        price=price
                    )
                    db.session.add(order_item)

            db.session.commit()
            print("✅ Added order items")

            print("\n🎉 Demo setup complete!")
            print("\n📋 Test Accounts:")
            print("Delivery Person: deliverydemo@gmail.com / password123")
            print("Customer: customerdemo@gmail.com / password123")
            print("Shopkeeper: shopdemo@gmail.com / password123")
            print("\n🔗 Test URLs:")
            print("Login: http://127.0.0.1:5000/login")
            print("Track Order: http://127.0.0.1:5000/track-order/1")
            print("\n📱 How to test:")
            print("1. Start Flask app: python app.py")
            print("2. Login as delivery person and start location sharing")
            print("3. Login as customer and view tracking page")
            print("4. Watch live location updates!")

        except Exception as e:
            print(f"❌ Error setting up demo: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_demo_users()