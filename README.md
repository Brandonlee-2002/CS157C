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

## Frontend Setup

Console-based Python front-end (using 'main.py') that covers all 11 use cases.

### Prerequesites

- **Python3.10+** - [Download here](https://www.python.org/downloads/)

- Backend setup (see steps above)

### Step 1 - Add 'main.py'

Place 'main.py' in the same directory as 'queries.py' and 'db.py':

```
CS157C/
├── main.py   
├── queries.py
├── db.py
├── setup_constraints.py
├── test.py
├── .env
└── .env.example
```

### Step 2 - Run the Frontend

Make sure your Neo4j database is running, then: 

```
python3 main.py
```

You will see the main menu:

```
══════════════════════════════════════════════════════
  SocialGraph  ·  CS157C Team Project
══════════════════════════════════════════════════════
  Graph-powered social network  |  Neo4j backend
 
══════════════════════════════════════════════════════
  SocialGraph  ·  Welcome
══════════════════════════════════════════════════════
  [1] Register
  [2] Login
  [0] Quit
  Select:
```

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

### Use Cases
 
| # | Use Case | How to Access |
|---|---|---|
| UC-1 | User Registration | Guest Menu → `[1] Register` |
| UC-2 | User Login | Guest Menu → `[2] Login` |
| UC-3 | View Profile | Main Menu → `[1] View My Profile` |
| UC-4 | Edit Profile | Main Menu → `[2] Edit Profile` |
| UC-5 | Follow a User | Main Menu → `[3] Follow a User` |
| UC-6 | Unfollow a User | Main Menu → `[4] Unfollow a User` |
| UC-7 | View Following/Followers | Main Menu → `[5] View Following/Followers` |
| UC-8 | Mutual Connections | Main Menu → `[6] Mutual Connections` |
| UC-9 | Friend Recommendations | Main Menu → `[7] Friend Recommendations` |
| UC-10 | Search Users | Main Menu → `[8] Search Users` |
| UC-11 | Explore Popular Users | Main Menu → `[9] Popular Users` |
 
### Troubleshooting
 
**`ModuleNotFoundError: No module named 'neo4j'`**  
→ Re-run `pip install neo4j python-dotenv bcrypt`
 
**`Connection refused` or `ServiceUnavailable`**  
→ Make sure Neo4j Desktop is running and the database is started.  
→ Check that `NEO4J_URI` in `.env` matches the bolt port shown in Neo4j Desktop (default: `7687`).
 
**`Authentication failed`**  
→ Verify `NEO4J_USERNAME` and `NEO4J_PASSWORD` in `.env` match your Neo4j credentials.
 
**`Username already taken` when registering**  
→ That username exists in the database. Try a different one.
 