
import os
import sqlite3

def check_and_fix_db(db_path):
    print(f"\nChecking database: {db_path}")
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        print(f"Existing columns in orders: {existing_columns}")
        
        columns_to_add = [
            ('scope', 'TEXT'),
            ('budget_tier', 'VARCHAR(20)'),
            ('deadline', 'DATETIME'),
            ('requirements', 'TEXT'),
            ('delivery_note', 'TEXT'),
            ('completed_at', 'DATETIME')
        ]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column '{col_name}'...")
                try:
                    cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}")
                    print(f"- Successfully added '{col_name}'")
                except Exception as e:
                    print(f"- Failed to add '{col_name}': {e}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
        print(f"Completed check/fix for {db_path}")
        
    except Exception as e:
        print(f"Error processing {db_path}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Pathway 1: skillbridge.db in current dir
    db1 = os.path.join(base_dir, 'skillbridge.db')
    check_and_fix_db(db1)
    
    # Pathway 2: instance/skillbridge.db
    db2 = os.path.join(base_dir, 'instance', 'skillbridge.db')
    check_and_fix_db(db2)
