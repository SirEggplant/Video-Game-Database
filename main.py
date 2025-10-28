import psycopg # pyright: ignore[reportMissingImports]
from SteamUltraDeluxHDRemixRemastered2.authentication_and_session.authentication import (
    login_with_email, register
)


UUID :str = ""
LOGGED_IN : bool = False


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

register <username, password, firstname, lastname, email>
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


def show_reg_help():
    print(""" 
          register <username, password, firstname, lastname, email>
    Create a new user account. You’ll be prompted for name, email
          """)
    

def handle_login(tokens):
    if(len(tokens) != 3):
        print("login <email> <password>")
        return
    
    user = login_with_email(tokens[1], tokens[2])
    UUID = user[0]
    if(UUID != ""):
        LOGGED_IN = True
        print("Welcome Back " + user[3])
    else:
        print("User Could not be found")

def handle_reg(tokens):
    if(len(tokens) == 6):
        user = register(username=tokens[1], password=tokens[2], firstname=tokens[3], lastname=tokens[4], email=tokens[5])
        if(user != None):
            LOGGED_IN = True
            UUID = user[0]
            print("Welcome " + user[3])
        else:
            print("Username already exists")
            return
    else:
        show_reg_help()
        return

def main():

    show_help()
    while(True):
        command = input(">")
        if command == "q" or command == "quit" or command == "exit":
            return
        
        tokens = command.split(" ")
        if tokens[0] == "login":
            handle_login(tokens=tokens)
            continue

        elif tokens[0] == "reg" or tokens[0] == "register":
            handle_reg(tokens=tokens)
            continue





    


if __name__ =="__main__":
    main()