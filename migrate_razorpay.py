from app import db
from sqlalchemy import text

# Add Razorpay fields to Order table
def migrate_razorpay_fields():
    try:
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('order')]
        
        if 'razorpay_order_id' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE 'order' ADD COLUMN razorpay_order_id VARCHAR(100)"))
                print("Added razorpay_order_id column")
        
        if 'razorpay_payment_id' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE 'order' ADD COLUMN razorpay_payment_id VARCHAR(100)"))
                print("Added razorpay_payment_id column")
        
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        migrate_razorpay_fields()