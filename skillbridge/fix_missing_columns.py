
from app import create_app
from models import db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    print("Inspecting 'orders' table...")
    inspector = inspect(db.engine)
    columns_info = inspector.get_columns('orders')
    existing_columns = [col['name'] for col in columns_info]
    print(f"Existing columns: {existing_columns}")

    columns_to_add = [
        ('scope', 'TEXT'),
        ('budget_tier', 'VARCHAR(20)'),
        ('deadline', 'DATETIME'),
        ('requirements', 'TEXT'),
        ('delivery_note', 'TEXT'),
        ('completed_at', 'DATETIME')
    ]

    with db.engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column '{col_name}'...")
                try:
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"))
                    print(f"- Successfully added '{col_name}'")
                except Exception as e:
                    print(f"- Failed to add '{col_name}': {e}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
    
    print("Schema update check complete.")
