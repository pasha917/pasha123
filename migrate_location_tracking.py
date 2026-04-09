"""
Database migration to add location tracking fields to User model.
Run this script once to update your database schema.
"""

from app import app, db
from sqlalchemy import text

def run_migration():
    """Add location tracking columns to user table"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]

            # Add new columns if they don't exist
            if 'current_lat' not in columns:
                print("Adding current_lat column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN current_lat FLOAT"))
                print("✓ Added current_lat column")

            if 'current_lng' not in columns:
                print("Adding current_lng column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN current_lng FLOAT"))
                print("✓ Added current_lng column")

            if 'location_updated_at' not in columns:
                print("Adding location_updated_at column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN location_updated_at DATETIME"))
                print("✓ Added location_updated_at column")

            if 'is_sharing_location' not in columns:
                print("Adding is_sharing_location column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN is_sharing_location BOOLEAN DEFAULT 0"))
                print("✓ Added is_sharing_location column")

            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("New columns added to user table:")
            print("- current_lat: FLOAT")
            print("- current_lng: FLOAT")
            print("- location_updated_at: DATETIME")
            print("- is_sharing_location: BOOLEAN")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    run_migration()