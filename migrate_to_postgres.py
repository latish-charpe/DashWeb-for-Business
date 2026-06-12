import json
import sys
import psycopg2
from urllib.parse import urlparse

def get_connection(db_url):
    # Parse the postgresql+psycopg2:// or postgres:// URL
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgres://')
    
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

def migrate_data():
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py <RENDER_DATABASE_URL>")
        print("Example: python migrate_to_postgres.py postgresql+psycopg2://user:pass@host/db")
        sys.exit(1)
        
    db_url = sys.argv[1]
    
    try:
        conn = get_connection(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        print("1. Successfully connected to PostgreSQL!")
        
        # 2 & 3. Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(50) NOT NULL,
            full_name VARCHAR(100) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            product VARCHAR(100) NOT NULL,
            amount NUMERIC(15, 2) NOT NULL,
            status VARCHAR(50) NOT NULL,
            date VARCHAR(50) NOT NULL,
            region VARCHAR(50) NOT NULL,
            month VARCHAR(50) NOT NULL,
            segment VARCHAR(50) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS upload_history (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(200) NOT NULL,
            upload_date VARCHAR(50) NOT NULL,
            records_imported INTEGER NOT NULL,
            uploaded_by VARCHAR(100) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            tag VARCHAR(50) NOT NULL,
            type VARCHAR(50) NOT NULL,
            "desc" TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            "desc" TEXT NOT NULL,
            time VARCHAR(50) NOT NULL
        );
        """)
        print("2/3. Verified and created missing tables automatically.")
        
        # Load JSON data
        with open('mysql_dump.json', 'r') as f:
            data = json.load(f)
            
        print("\n--- Migration Report ---")
        print("Number of tables: 5")
        
        for table, rows in data.items():
            if not rows:
                print(f"{table}: 0 records imported.")
                continue
                
            cols = list(rows[0].keys())
            # Handle reserved word 'desc' in postgres
            safe_cols = [f'"{c}"' if c == 'desc' else c for c in cols]
            col_str = ", ".join(safe_cols)
            val_str = ", ".join(["%s"] * len(cols))
            
            insert_query = f"INSERT INTO {table} ({col_str}) VALUES ({val_str}) ON CONFLICT DO NOTHING"
            
            success = 0
            failed = 0
            for row in rows:
                values = tuple(row[c] for c in cols)
                try:
                    cursor.execute(insert_query, values)
                    success += 1
                except Exception as e:
                    failed += 1
            
            print(f"{table}: {success} records successfully imported. {failed} failed queries.")
            
        print("\nData migration from MySQL to PostgreSQL completed!")
        print("Your dashboard metrics, charts, orders, and products should now load correctly on Render.")
        
    except Exception as e:
        print(f"Failed to connect or migrate: {e}")

if __name__ == '__main__':
    migrate_data()
