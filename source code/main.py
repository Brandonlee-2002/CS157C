"""
CS157C Social Network — Console Front-End
Connects to queries.py (backend) which connects to Neo4j via db.py.

Usage:
    python main.py

Requirements (already in your repo):
    pip install neo4j python-dotenv bcrypt
"""

from queries import (
    create_user,
    login_user,
    get_profile,
    edit_profile,
    follow_user,
    unfollow_user,
    get_following,
    get_followers,
    get_mutual_connections,
    get_recommendations,
    search_users,
    get_popular_users,
)

# ─── Helpers ────────────────────────────────────────────────────────────────

LINE  = "─" * 54
DLINE = "═" * 54

def banner(text: str) -> None:
    print(f"\n{DLINE}")
    print(f"  {text}")
    print(DLINE)

def section(text: str) -> None:
    print(f"\n{LINE}")
    print(f"  {text}")
    print(LINE)

def prompt(text: str) -> str:
    return input(f"  {text}: ").strip()

def pause() -> None:
    input("\n  [Press Enter to continue]")

def clear_screen() -> None:
    # Simple blank-line separator instead of os.system("clear") for screenshot
    # friendliness — keeps full output visible in the terminal.
    print("\n" * 2)

# ─── Guest Menu (not logged in) ──────────────────────────────────────────────

def guest_menu() -> dict | None:
    """Show the guest menu and return the logged-in user dict, or None to quit."""
    while True:
        banner("SocialGraph  ·  Welcome")
        print("  [1] Register")
        print("  [2] Login")
        print("  [0] Quit")
        choice = prompt("Select")

        if choice == "1":
            register_flow()
        elif choice == "2":
            user = login_flow()
            if user:
                return user
        elif choice == "0":
            print("\n  Goodbye!\n")
            return None
        else:
            print("  ✗  Invalid option.")

def register_flow() -> None:
    """UC-1: User Registration"""
    section("UC-1 · Register New Account")
    name     = prompt("Full name")
    username = prompt("Username")
    email    = prompt("Email")
    password = prompt("Password")

    user_id, msg = create_user(name, username, email, password)
    if user_id:
        print(f"\n  ✓  {msg}  (id={user_id})")
    else:
        print(f"\n  ✗  {msg}")
    pause()

def login_flow() -> dict | None:
    """UC-2: User Login"""
    section("UC-2 · Login")
    username = prompt("Username")
    password = prompt("Password")

    user, msg = login_user(username, password)
    if user:
        print(f"\n  ✓  {msg}  —  Welcome back, {user.get('name') or user['username']}!")
        pause()
        return user
    else:
        print(f"\n  ✗  {msg}")
        pause()
        return None

# ─── Main Menu (logged in) ───────────────────────────────────────────────────

def main_menu(user: dict) -> None:
    """Drive the application for a logged-in user."""
    while True:
        banner(f"SocialGraph  ·  @{user['username']}")
        print("  ── Profile ──────────────────────────")
        print("  [1] View My Profile          (UC-3)")
        print("  [2] Edit Profile             (UC-4)")
        print("  ── Social Graph ─────────────────────")
        print("  [3] Follow a User            (UC-5)")
        print("  [4] Unfollow a User          (UC-6)")
        print("  [5] View Following/Followers (UC-7)")
        print("  [6] Mutual Connections       (UC-8)")
        print("  [7] Friend Recommendations   (UC-9)")
        print("  ── Explore ──────────────────────────")
        print("  [8] Search Users             (UC-10)")
        print("  [9] Popular Users            (UC-11)")
        print("  ─────────────────────────────────────")
        print("  [0] Logout")

        choice = prompt("Select")
        clear_screen()

        if   choice == "1": view_profile(user)
        elif choice == "2": user = edit_profile_flow(user)
        elif choice == "3": follow_flow(user)
        elif choice == "4": unfollow_flow(user)
        elif choice == "5": connections_flow(user)
        elif choice == "6": mutual_flow(user)
        elif choice == "7": recommendations_flow(user)
        elif choice == "8": search_flow(user)
        elif choice == "9": popular_flow()
        elif choice == "0":
            print(f"\n  Logged out. See you, @{user['username']}!\n")
            break
        else:
            print("  ✗  Invalid option.")

# ─── UC-3: View Profile ───────────────────────────────────────────────────────

def view_profile(user: dict) -> None:
    section("UC-3 · View My Profile")
    data = get_profile(user["id"])
    if not data:
        print("  ✗  Could not load profile.")
    else:
        print(f"  ID       : {data['id']}")
        print(f"  Name     : {data['name']}")
        print(f"  Username : @{data['username']}")
        print(f"  Email    : {data['email']}")
        print(f"  Bio      : {data['bio'] or '(empty)'}")
    pause()

# ─── UC-4: Edit Profile ───────────────────────────────────────────────────────

def edit_profile_flow(user: dict) -> dict:
    section("UC-4 · Edit Profile")
    print("  (Leave blank to keep current value)")
    new_name = prompt(f"Name [{user.get('name') or ''}]")
    new_bio  = prompt("Bio")

    msg = edit_profile(
        user["id"],
        name=new_name  if new_name  else None,
        bio=new_bio    if new_bio   else None,
    )
    print(f"\n  ✓  {msg}")

    # Refresh local user dict so the banner shows updated name
    refreshed = get_profile(user["id"])
    if refreshed:
        user.update(refreshed)
    pause()
    return user

# ─── UC-5: Follow a User ──────────────────────────────────────────────────────

def follow_flow(user: dict) -> None:
    section("UC-5 · Follow a User")
    query = prompt("Search username to follow")
    results = search_users(query)

    if not results:
        print("  No users found.")
        pause()
        return

    _print_user_list(results)
    target_id = _pick_user_id(results)
    if target_id is None:
        return

    msg = follow_user(user["id"], target_id)
    print(f"\n  ✓  {msg}")
    pause()

# ─── UC-6: Unfollow a User ────────────────────────────────────────────────────

def unfollow_flow(user: dict) -> None:
    section("UC-6 · Unfollow a User")
    following = get_following(user["id"])

    if not following:
        print("  You are not following anyone.")
        pause()
        return

    _print_user_list(following)
    target_id = _pick_user_id(following)
    if target_id is None:
        return

    msg = unfollow_user(user["id"], target_id)
    print(f"\n  ✓  {msg}")
    pause()

# ─── UC-7: View Connections ───────────────────────────────────────────────────

def connections_flow(user: dict) -> None:
    section("UC-7 · Following & Followers")

    following = get_following(user["id"])
    print(f"\n  People you follow ({len(following)}):")
    if following:
        for u in following:
            print(f"    • @{u['username']}  (id={u['id']})")
    else:
        print("    (none)")

    followers = get_followers(user["id"])
    print(f"\n  Your followers ({len(followers)}):")
    if followers:
        for u in followers:
            print(f"    • @{u['username']}  (id={u['id']})")
    else:
        print("    (none)")

    pause()

# ─── UC-8: Mutual Connections ─────────────────────────────────────────────────

def mutual_flow(user: dict) -> None:
    section("UC-8 · Mutual Connections")
    query = prompt("Search username to compare with")
    results = search_users(query)

    if not results:
        print("  No users found.")
        pause()
        return

    _print_user_list(results)
    target_id = _pick_user_id(results)
    if target_id is None:
        return

    mutuals = get_mutual_connections(user["id"], target_id)
    print(f"\n  Mutual connections ({len(mutuals)}):")
    if mutuals:
        for u in mutuals:
            print(f"    • @{u['username']}  (id={u['id']})")
    else:
        print("    (none)")
    pause()

# ─── UC-9: Friend Recommendations ────────────────────────────────────────────

def recommendations_flow(user: dict) -> None:
    section("UC-9 · Friend Recommendations")
    recs = get_recommendations(user["id"])

    if not recs:
        print("  No recommendations available yet. Try following more people!")
    else:
        print(f"  Top {len(recs)} suggested connections:\n")
        for i, r in enumerate(recs, 1):
            print(f"  {i:2}. @{r['username']:<20}  "
                  f"({r['commonConnections']} mutual connection(s))")
    pause()

# ─── UC-10: Search Users ──────────────────────────────────────────────────────

def search_flow(user: dict) -> None:
    section("UC-10 · Search Users")
    query = prompt("Enter name or username")
    results = search_users(query)

    if not results:
        print("  No users found.")
    else:
        print(f"\n  Found {len(results)} result(s):\n")
        for r in results:
            tag = " ← (you)" if r["id"] == user["id"] else ""
            print(f"    • @{r['username']:<20}  id={r['id']}{tag}")
    pause()

# ─── UC-11: Explore Popular Users ────────────────────────────────────────────

def popular_flow() -> None:
    section("UC-11 · Most-Followed Users")
    try:
        limit = int(prompt("How many to show? [default 10]") or "10")
    except ValueError:
        limit = 10

    popular = get_popular_users(limit=limit)

    if not popular:
        print("  No data available.")
    else:
        print(f"\n  {'Rank':<6} {'Username':<22} Followers")
        print("  " + "─" * 40)
        for i, u in enumerate(popular, 1):
            print(f"  {i:<6} @{u['username']:<21} {u['followerCount']}")
    pause()

# ─── Internal utilities ───────────────────────────────────────────────────────

def _print_user_list(users: list) -> None:
    print()
    for i, u in enumerate(users, 1):
        print(f"  [{i}] @{u['username']:<20}  id={u['id']}")

def _pick_user_id(users: list) -> int | None:
    raw = prompt("Select number (0 to cancel)")
    try:
        idx = int(raw)
    except ValueError:
        print("  ✗  Invalid input.")
        pause()
        return None
    if idx == 0:
        return None
    if 1 <= idx <= len(users):
        return users[idx - 1]["id"]
    print("  ✗  Out of range.")
    pause()
    return None

# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    banner("SocialGraph  ·  CS157C Team Project")
    print("  Graph-powered social network  |  Neo4j backend\n")

    while True:
        user = guest_menu()
        if user is None:
            break
        main_menu(user)

if __name__ == "__main__":
    main()