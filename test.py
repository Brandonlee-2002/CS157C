from queries import (
    create_user, login_user, get_profile, edit_profile,
    follow_user, unfollow_user, get_following, get_followers,
    get_mutual_connections, get_recommendations,
    search_users, get_popular_users
)
from db import run_query

print("RUNNING BACKEND TESTS")

# Get two real users from the dataset
real_users = run_query("MATCH (u:user) RETURN u.id AS id, u.username AS username LIMIT 2")
if not real_users:
    print("ERROR: No users found in database. Check your connection.")
    exit()

real_id_1 = real_users[0]["id"]
real_id_2 = real_users[1]["id"]
print(f"\nUsing dataset users: {real_users[0]['username']} (id={real_id_1}), {real_users[1]['username']} (id={real_id_2})")

# Register user
print("\n[UC-1] User Registration")
new_id, msg = create_user("Test User", "testuser_abc", "test@example.com", "password123")
print(f"  Result: {msg} (id={new_id})")

# Testing login
print("\n[UC-2] User Login")
user, msg = login_user("testuser_abc", "password123")
print(f"  Result: {msg}")
if user:
    print(f"  Logged in as: {user['username']} (id={user['id']})")
wrong, msg2 = login_user("testuser_abc", "wrongpassword")
print(f"  Wrong password: {msg2}")

# View user's profile 
print("\n[UC-3] View Profile (registered user)")
profile = get_profile(new_id)
print(f"  Profile: {profile}")
print("\n[UC-3] View Profile (dataset user)")
ds_profile = get_profile(real_id_1)
print(f"  Profile: {ds_profile}")

# Attempt editing the profile 
print("\n[UC-4] Edit Profile")
result = edit_profile(new_id, name="Updated Name", bio="This is my bio.")
print(f"  Result: {result}")
print(f"  Updated: {get_profile(new_id)}")

# Follow
print("\n[UC-5] Follow User")
print(f"  {follow_user(new_id, real_id_1)}")
print(f"  Follow again: {follow_user(new_id, real_id_1)}")
print(f"  Follow self: {follow_user(new_id, new_id)}")

# Unfollow
print("\n[UC-6] Unfollow User")
print(f"  {unfollow_user(new_id, real_id_1)}")

# Re-follow for remaining tests
follow_user(new_id, real_id_1)
follow_user(new_id, real_id_2)

# View Connections 
print("\n[UC-7] Following / Followers")
following = get_following(new_id)
print(f"  Following ({len(following)}): {following[:3]}")
followers = get_followers(real_id_1)
print(f"  Followers of {real_users[0]['username']} ({len(followers)}): {followers[:3]}")

# Mutual Connections 
print("\n[UC-8] Mutual Connections")
mutuals = get_mutual_connections(real_id_1, real_id_2)
print(f"  Mutuals ({len(mutuals)}): {mutuals[:3]}")

# Recommendations 
print("\n[UC-9] Friend Recommendations")
recs = get_recommendations(real_id_1)
print(f"  Recommendations for {real_users[0]['username']} ({len(recs)}): {recs[:3]}")

# Search 
print("\n[UC-10] Search Users")
results = search_users("not")
print(f"  Search 'not' ({len(results)} results): {results[:3]}")

# Popular Users 
print("\n[UC-11] Popular Users")
popular = get_popular_users(5)
print(f"  Top 5: {popular}")

# Cleanup test user 
print("\n[Cleanup] Removing test user...")
run_query("MATCH (u:user {username: 'testuser_abc'}) DETACH DELETE u")
print("  Test user removed.")

print("ALL TESTS COMPLETE")
