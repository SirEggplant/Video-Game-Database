import psycopg



def show_help():
    print("""
──────────────────────────────────────────────
🎮  Steam Ultra Deluxe HD Remix Remastered 2
──────────────────────────────────────────────
A Command-Line Application for Managing Users, Games, and Collections
CSCI-320 • Principles of Data Management • Phase 2
──────────────────────────────────────────────

Welcome! This CLI tool connects to a PostgreSQL database that stores
information about video games, users, developers, publishers, ratings,
and playtime logs. Use it to create accounts, search games, build
collections, record play sessions, and explore your data.

──────────────────────────────────────────────
🧩  BASIC COMMANDS
──────────────────────────────────────────────
help
    Show this help screen.

exit | quit
    Close the application and terminate the database session.

login <email> <password>
    Log in as an existing user.

register
    Create a new user account. You’ll be prompted for name, email,
    and preferred platforms. The creation date is stored automatically.

──────────────────────────────────────────────
🎮  GAME & COLLECTION COMMANDS
──────────────────────────────────────────────
games list
    List all available games (name, platform, genre, release date, price).

games search <field> <keyword>
    Search for games by title, genre, platform, release year, developer,
    publisher, or price range.
    Example: games search genre RPG

collections list
    Show all your collections sorted alphabetically with:
        • Collection name
        • Number of games
        • Total playtime (hh:mm)

collections create <name>
    Create a new collection.

collections rename <old_name> <new_name>
    Rename an existing collection.

collections delete <name>
    Permanently delete a collection.

collections add <collection_name> <game_id>
    Add a game to a collection.
    ⚠ Warns you if you don’t own the required platform.

collections remove <collection_name> <game_id>
    Remove a game from a collection.

──────────────────────────────────────────────
⭐  PLAY & RATINGS
──────────────────────────────────────────────
rate <game_id> <stars>
    Rate a game from 1–5 stars. (A single rating per game.)

play <game_id> <minutes>
    Record that you played the game for the given time.
    The timestamp is stored automatically.

play random <collection_name>
    Play a random game from a chosen collection.

──────────────────────────────────────────────
👥  SOCIAL COMMANDS
──────────────────────────────────────────────
users search <email_part>
    Search for other users by email.

follow <user_id>
    Follow another user.

unfollow <user_id>
    Unfollow a user.

followers
    List users who follow you.

following
    List users you are following.

""")


def main():

    show_help()
    while(True):
        command = input()
        if command == "q" or command == "quit" or command == "exit":
            return



    


if __name__ =="__main__":
    main()