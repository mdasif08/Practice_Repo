#!/usr/bin/env python3
"""
Database connection diagnostic script.
Checks if PostgreSQL is running and if the database connection works.
"""

import sys
import psycopg2
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible."""
    print("🔍 Checking PostgreSQL connection...")
    
    # Test connection parameters
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'newDB',
        'user': 'postgres',
        'password': 'root'
    }
    
    try:
        print(f"  📡 Attempting to connect to PostgreSQL...")
        print(f"     Host: {connection_params['host']}")
        print(f"     Port: {connection_params['port']}")
        print(f"     Database: {connection_params['database']}")
        print(f"     User: {connection_params['user']}")
        
        conn = psycopg2.connect(**connection_params)
        print("  ✅ PostgreSQL connection successful!")
        
        # Check if tables exist
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            print(f"  📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"     - {table[0]}")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"  ❌ PostgreSQL connection failed: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure PostgreSQL is installed and running")
        print("   2. Check if the database 'newDB' exists")
        print("   3. Verify username 'postgres' and password 'root'")
        print("   4. Ensure PostgreSQL is listening on port 5432")
        return False
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {str(e)}")
        return False

def check_database_exists():
    """Check if the database exists."""
    print("\n🔍 Checking if database 'newDB' exists...")
    
    try:
        # Try to connect to postgres database first
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='root'
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT datname FROM pg_database WHERE datname = 'newDB'")
            result = cursor.fetchone()
            
            if result:
                print("  ✅ Database 'newDB' exists")
                conn.close()
                return True
            else:
                print("  ❌ Database 'newDB' does not exist")
                print("\n🔧 Creating database 'newDB'...")
                
                # Create the database
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute("CREATE DATABASE newDB")
                print("  ✅ Database 'newDB' created successfully")
                conn.close()
                return True
                
    except Exception as e:
        print(f"  ❌ Error checking/creating database: {str(e)}")
        return False

def test_database_service():
    """Test the DatabaseService class."""
    print("\n🔍 Testing DatabaseService...")
    
    try:
        from services.database_service import DatabaseService
        
        db_service = DatabaseService()
        print("  ✅ DatabaseService initialized successfully")
        
        # Test getting recent commits
        commits = db_service.get_recent_commits(limit=5)
        print(f"  📝 Found {len(commits)} recent commits")
        
        # Test getting statistics
        stats = db_service.get_statistics()
        print(f"  📊 Database statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ DatabaseService test failed: {str(e)}")
        return False

def main():
    """Run all database checks."""
    print("🚀 Starting database diagnostic...\n")
    
    # Check if PostgreSQL is running
    if not check_postgresql_connection():
        print("\n❌ PostgreSQL connection failed. Please check your PostgreSQL installation.")
        return False
    
    # Check if database exists
    if not check_database_exists():
        print("\n❌ Database check failed.")
        return False
    
    # Test DatabaseService
    if not test_database_service():
        print("\n❌ DatabaseService test failed.")
        return False
    
    print("\n🎉 All database checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



