#!/usr/bin/env python3
"""
Migration Script: Transfer commits from JSONL file to PostgreSQL database
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import psycopg2
import os

def connect_to_database():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'newDB'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'root')
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None

def create_commits_table(conn):
    """Create commits table if it doesn't exist."""
    try:
        with conn.cursor() as cursor:
            # Create schema if it doesn't exist
            cursor.execute("CREATE SCHEMA IF NOT EXISTS CraftNudge;")
            
            # Create commits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CraftNudge.Commits (
                    id SERIAL PRIMARY KEY,
                    commit_id VARCHAR(40) UNIQUE NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create commit files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CraftNudge.Commit_Files (
                    file_id SERIAL PRIMARY KEY,
                    commit_id VARCHAR(40) REFERENCES CraftNudge.Commits(commit_id),
                    file_name VARCHAR(500) NOT NULL,
                    change_type VARCHAR(20) DEFAULT 'modified'
                );
            """)
            
            conn.commit()
            print("✅ Database tables created successfully")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        conn.rollback()

def migrate_commits():
    """Migrate commits from JSONL file to database."""
    jsonl_file = Path("legacy/data/behaviors/commits.jsonl")
    
    if not jsonl_file.exists():
        print(f"❌ JSONL file not found: {jsonl_file}")
        return False
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return False
    
    # Create tables
    create_commits_table(conn)
    
    try:
        migrated_count = 0
        
        with open(jsonl_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse JSON line
                    commit_data = json.loads(line.strip())
                    
                    # Extract commit information
                    commit_id = commit_data.get('commit_hash', '')
                    author = commit_data.get('author', '')
                    message = commit_data.get('message', '')
                    timestamp_str = commit_data.get('timestamp_commit', '')
                    changed_files = commit_data.get('changed_files', [])
                    
                    if not commit_id or not author or not message:
                        print(f"⚠️ Skipping line {line_num}: Missing required fields")
                        continue
                    
                    # Parse timestamp
                    try:
                        if timestamp_str.endswith('Z'):
                            timestamp_str = timestamp_str[:-1] + '+00:00'
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        timestamp = datetime.now()
                    
                    # Insert commit
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO CraftNudge.Commits (commit_id, author, message, timestamp)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (commit_id) DO NOTHING
                            RETURNING id
                        """, (commit_id, author, message, timestamp))
                        
                        result = cursor.fetchone()
                        if result:
                            # Insert changed files
                            for file_name in changed_files:
                                cursor.execute("""
                                    INSERT INTO CraftNudge.Commit_Files (commit_id, file_name, change_type)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT DO NOTHING
                                """, (commit_id, file_name, 'modified'))
                            
                            migrated_count += 1
                            print(f"✅ Migrated commit: {commit_id[:8]}... - {message[:50]}...")
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Invalid JSON on line {line_num}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing line {line_num}: {str(e)}")
                    continue
        
        conn.commit()
        print(f"\n🎉 Migration completed! {migrated_count} commits migrated to database.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration():
    """Verify that commits were migrated correctly."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Count commits in database
            cursor.execute("SELECT COUNT(*) FROM CraftNudge.Commits;")
            db_count = cursor.fetchone()[0]
            
            # Count commits in JSONL file
            jsonl_file = Path("legacy/data/behaviors/commits.jsonl")
            jsonl_count = 0
            if jsonl_file.exists():
                with open(jsonl_file, 'r') as f:
                    jsonl_count = sum(1 for line in f if line.strip())
            
            print(f"\n📊 Migration Verification:")
            print(f"  - JSONL file commits: {jsonl_count}")
            print(f"  - Database commits: {db_count}")
            
            if db_count > 0:
                print("✅ Migration successful! Commits are now in the database.")
                return True
            else:
                print("❌ No commits found in database after migration.")
                return False
                
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Commit Migration")
    print("=" * 40)
    
    success = migrate_commits()
    
    if success:
        verify_migration()
        print("\n✨ Migration process completed!")
        print("💡 You can now see commits in the UI and they will be automatically processed by AI agents.")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
