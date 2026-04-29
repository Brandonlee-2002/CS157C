from db import run_query

print("Creating constraints...")

run_query("""
CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (u:User)
REQUIRE u.userId IS UNIQUE
""")

run_query("""
CREATE CONSTRAINT username IF NOT EXISTS
FOR (u:User)
REQUIRE u.username IS UNIQUE
""")

run_query("""
CREATE CONSTRAINT email IF NOT EXISTS
FOR (u:User)
REQUIRE u.email IS UNIQUE
""")

print("All constraints created successfully")