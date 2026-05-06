# CS157C

## Neo4j Backend Setup

## Setup

1. Install dependencies:
   pip install neo4j pandas python-dotenv bcrypt

2. Create `.env` file using `.env.example`

3. Start Neo4j Desktop and run your database

4. Initialize constraints:
   python setup_constraints.py

5. Test connection:
   python test.py

## Available Query Functions

Import from `queries.py` to use these in the frontend:

```python
from queries import create_user, login_user, get_profile, ...
```

| Function | Parameters | Returns |
|---|---|---|
| `create_user` | `name, username, email, password` | `(id, message)` |
| `login_user` | `username, password` | `(user_dict, message)` |
| `get_profile` | `user_id` | `user_dict` |
| `edit_profile` | `user_id, name=None, bio=None` | `message` |
| `follow_user` | `follower_id, followee_id` | `message` |
| `unfollow_user` | `follower_id, followee_id` | `message` |
| `get_following` | `user_id` | `list of {id, username}` |
| `get_followers` | `user_id` | `list of {id, username}` |
| `get_mutual_connections` | `user_id_a, user_id_b` | `list of {id, username}` |
| `get_recommendations` | `user_id` | `list of {id, username, commonConnections}` |
| `search_users` | `query` | `list of {id, username}` |
| `get_popular_users` | `limit=10` | `list of {id, username, followerCount}` |
