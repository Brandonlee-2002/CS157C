from db import run_query

try:
    print("Creating constraints...")

    run_query("""
        CREATE CONSTRAINT user_id IF NOT EXISTS
        FOR (u:user) REQUIRE u.id IS UNIQUE
    """)
    run_query("""
        CREATE CONSTRAINT username IF NOT EXISTS
        FOR (u:user) REQUIRE u.username IS UNIQUE
    """)
    run_query("""
        CREATE INDEX user_name IF NOT EXISTS
        FOR (u:user) ON (u.name)
    """)

    print("All constraints and indexes created successfully.")

except Exception as e:
    print(f"Setup failed: {e}")
    print("Make sure Neo4j is running and your .env credentials are correct.")
