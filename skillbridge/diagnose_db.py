
import os
import sqlite3
from config import Config

def diagnose():
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    print(f"Config URI: {db_uri}")
    
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
             # recreate the logic from config.py to be sure
             basedir = os.path.abspath(os.path.dirname(__file__))
             db_path = os.path.join(basedir, db_path)
        
        print(f"Resolved DB Path: {db_path}")
        print(f"File exists: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(orders)")
                columns = cursor.fetchall()
                print("\nColumns in 'orders' table:")
                found_columns = []
                for col in columns:
                    print(f"- {col[1]} ({col[2]})")
                    found_columns.append(col[1])
                
                missing = []
                for req in ['scope', 'budget_tier', 'deadline', 'requirements', 'delivery_note', 'completed_at']:
                    if req not in found_columns:
                        missing.append(req)
                
                if missing:
                    print(f"\nMISSING COLUMNS: {missing}")
                else:
                    print("\nALL REQUIRED COLUMNS PRESENT.")
                    
            except Exception as e:
                print(f"Error querying DB: {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    diagnose()
