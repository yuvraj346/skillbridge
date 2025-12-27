from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating new tables...")
    db.create_all()
    
    print("Updating 'orders' table...")
    try:
        with db.engine.connect() as conn:
            # Add new columns to orders table
            # Check if columns exist first or just try-except
            try:
                conn.execute(text("ALTER TABLE orders ADD COLUMN scope TEXT"))
                print("- Added 'scope'")
            except Exception as e:
                print(f"- 'scope' might already exist: {e}")
                
            try:
                conn.execute(text("ALTER TABLE orders ADD COLUMN budget_tier VARCHAR(20)"))
                print("- Added 'budget_tier'")
            except Exception as e:
                print(f"- 'budget_tier' might already exist: {e}")

            try:
                conn.execute(text("ALTER TABLE orders ADD COLUMN deadline DATETIME"))
                print("- Added 'deadline'")
            except Exception as e:
                print(f"- 'deadline' might already exist: {e}")
                
            conn.commit()
    except Exception as e:
        print(f"Error updating schema: {e}")

    print("Schema update complete.")
