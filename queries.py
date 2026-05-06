from db import run_query
import hashlib
import time

# HELPERS

# Converts a plain text password into a SHA-256 hash for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generates a unique ID using the current timestamp in milliseconds
# Dataset IDs are small integers, so timestamp-based IDs won't collide with them
def generate_id():
    return int(time.time() * 1000)

# UC-1: User Registration 
    # Registered users get extra properties (name, email, password, bio)
    # Dataset users only have: id, username

def create_user(name, username, email, password):
    # Check if username is already taken before creating
    # MATCH finds any existing user node with the same username
    existing = run_query("MATCH (u:user {username: $username}) RETURN u", {"username": username})
    if existing:
        return None, "Username already taken."
    new_id = generate_id()
    # CREATE makes a new user node with all required properties
    # Password is hashed before storing — never stored as plain text
    run_query("""
        CREATE (u:user {id: $id, name: $name, username: $username,
                        email: $email, password: $password, bio: ''})
    """, {
        "id": new_id,
        "name": name,
        "username": username,
        "email": email,
        "password": hash_password(password)
    })
    return new_id, "User created successfully."

# UC-2: User Login 

def login_user(username, password):
    # MATCH finds the user node by username and returns all login-relevant fields
    result = run_query("""
        MATCH (u:user {username: $username})
        RETURN u.id AS id, u.username AS username,
               u.name AS name, u.email AS email,
               u.password AS password, u.bio AS bio
    """, {"username": username})
    if not result:
        return None, "User not found."
    user = result[0]
    # Dataset users have no password property — block login attempts on them
    if not user.get("password"):
        return None, "This account was not registered through the app."
    # Hash the input password and compare against the stored hash
    if user["password"] != hash_password(password):
        return None, "Incorrect password."
    return user, "Login successful."

# UC-3: View Profile 

def get_profile(user_id):
    # MATCH finds the user node by id
    # coalesce() returns the first non-null value — handles dataset users
    # who have no name, email, or bio by falling back to safe defaults
    result = run_query("""
        MATCH (u:user {id: $id})
        RETURN u.id AS id,
               u.username AS username,
               coalesce(u.name, u.username) AS name,
               coalesce(u.email, 'N/A') AS email,
               coalesce(u.bio, '') AS bio
    """, {"id": user_id})
    return result[0] if result else None

# UC-4: Edit Profile

def edit_profile(user_id, name=None, bio=None):
    # MATCH finds the user node, SET updates only the properties provided
    # Each field is updated independently so partial updates are supported
    if name:
        run_query("MATCH (u:user {id: $id}) SET u.name = $name", {"id": user_id, "name": name})
    if bio is not None:
        run_query("MATCH (u:user {id: $id}) SET u.bio = $bio", {"id": user_id, "bio": bio})
    return "Profile updated."

# UC-5: Follow a User 

def follow_user(follower_id, followee_id):
    if follower_id == followee_id:
        return "You cannot follow yourself."
    # Check if the FOLLOWS relationship already exists between the two users
    already = run_query("""
        MATCH (a:user {id: $ferId})-[:FOLLOWS]->(b:user {id: $feeId})
        RETURN a
    """, {"ferId": follower_id, "feeId": followee_id})
    if already:
        return "Already following."
    # MERGE creates the FOLLOWS relationship only if it doesn't already exist
    # This prevents duplicate edges in the graph
    run_query("""
        MATCH (a:user {id: $ferId}), (b:user {id: $feeId})
        MERGE (a)-[:FOLLOWS]->(b)
    """, {"ferId": follower_id, "feeId": followee_id})
    return "Followed successfully."

# UC-6: Unfollow a User

def unfollow_user(follower_id, followee_id):
    # MATCH finds the specific FOLLOWS edge between the two users
    # DELETE removes only the relationship, not the user nodes themselves
    run_query("""
        MATCH (a:user {id: $ferId})-[r:FOLLOWS]->(b:user {id: $feeId})
        DELETE r
    """, {"ferId": follower_id, "feeId": followee_id})
    return "Unfollowed successfully."

# UC-7: View Connections (Following + Followers)

def get_following(user_id):
    # Traverses outgoing FOLLOWS edges from the user
    # Returns every user that this user is following
    return run_query("""
        MATCH (u:user {id: $id})-[:FOLLOWS]->(f:user)
        RETURN f.id AS id, f.username AS username
    """, {"id": user_id})

def get_followers(user_id):
    # Traverses incoming FOLLOWS edges toward the user
    # Returns every user that follows this user
    return run_query("""
        MATCH (f:user)-[:FOLLOWS]->(u:user {id: $id})
        RETURN f.id AS id, f.username AS username
    """, {"id": user_id})

# UC-8: Mutual Connections

def get_mutual_connections(user_id_a, user_id_b):
    # Finds users that both A and B follow simultaneously
    # The pattern matches a shared node (mutual) pointed to by both users
    return run_query("""
        MATCH (a:user {id: $idA})-[:FOLLOWS]->(mutual:user)<-[:FOLLOWS]-(b:user {id: $idB})
        RETURN mutual.id AS id, mutual.username AS username
    """, {"idA": user_id_a, "idB": user_id_b})

# UC-9: Friend Recommendations 

def get_recommendations(user_id, limit=10):
    # Two-hop graph traversal: me -> friend -> rec
    # Finds users followed by people I follow, that I don't already follow
    # WHERE filters out existing follows and self
    # count(*) ranks recommendations by how many mutual connections lead to them
    return run_query("""
        MATCH (me:user {id: $id})-[:FOLLOWS]->(friend:user)-[:FOLLOWS]->(rec:user)
        WHERE NOT (me)-[:FOLLOWS]->(rec) AND rec.id <> $id
        RETURN rec.id AS id, rec.username AS username,
               count(*) AS commonConnections
        ORDER BY commonConnections DESC
        LIMIT $limit
    """, {"id": user_id, "limit": limit})

# UC-10: Search Users

def search_users(query):
    # toLower() on both sides makes the search case-insensitive
    # CONTAINS checks if the username includes the search string anywhere
    return run_query("""
        MATCH (u:user)
        WHERE toLower(u.username) CONTAINS toLower($query)
        RETURN u.id AS id, u.username AS username
        LIMIT 20
    """, {"query": query})

# UC-11: Explore Popular Users

def get_popular_users(limit=10):
    # Counts incoming FOLLOWS edges per user to measure popularity
    # WHERE filters out phantom nodes (dataset followees with no username)
    # ORDER BY DESC puts the most followed users first
    return run_query("""
        MATCH (u:user)<-[:FOLLOWS]-(f:user)
        WHERE u.username IS NOT NULL
        RETURN u.id AS id, u.username AS username,
               count(f) AS followerCount
        ORDER BY followerCount DESC
        LIMIT $limit
    """, {"limit": limit})
