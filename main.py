import psycopg # pyright: ignore[reportMissingImports]
from authentication_and_session.authentication import (
    login_with_email, register
)

from collection_crud.collection import (
    create_collection, list_users_collections, add_game_to_collection, rename_collection, delete_collection, check_if_collection_exists
)

from game_search_and_sorting.game import (
    get_game_by_title, get_game_by_release_year, get_game_by_genre, get_game_by_platform, get_game_by_uuid, get_game_by_developer, get_game_by_publisher, get_game_by_price_between, get_game_by_price_lower_than, sort_by, get_games_by_esrb
)

from playing_games.game_Interactions import (
    play_Game, rate_Game, buy_Game
)
from printers.print_helper import (
    print_games
)

from collection_membership.collection_membership import(
    add_platform_to_user
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

play <minutes> <collection_name>
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
        Create a new user account. You’ll be prompted for name, emailSky
          """)
    

def handle_login_with_email(tokens):
    global UUID, LOGGED_IN
    if(len(tokens) != 3):
        print("login <email> <password>")
        return
    
    user = login_with_email(tokens[1], tokens[2])
    if(user != None):
        UUID = user[0]
        LOGGED_IN = True
        print("Welcome Back " + user[3])
    else:
        print("User Could not be found")

def handle_reg(tokens):
    global UUID, LOGGED_IN
    if(len(tokens) == 6):
        user = register(username=tokens[1], password=tokens[2], firstname=tokens[3], lastname=tokens[4], email=tokens[5])
        if(user != None):
            LOGGED_IN = True
            UUID = user[0]
            print("Welcome " + user[3])
        else:
            print("Username already exists or email already exist")
            return
    else:
        show_reg_help()
        return

# AI collection print formating
def print_collections(rows):
    if not rows:
        print("No collections found.")
        return

    # Define column headers
    headers = ["Name", "Number of Games", "Total Playtime"]

    # Compute column widths
    name_width = max(len(headers[0]), max(len(str(r[2])) for r in rows))
    num_width = max(len(headers[1]), max(len(str(r[3])) for r in rows))
    time_width = max(len(headers[2]), max(len(str(r[4])) for r in rows))

    # Create a horizontal separator
    separator = f"+-{'-' * name_width}-+-{'-' * num_width}-+-{'-' * time_width}-+"

    # Print header
    print(separator)
    print(f"| {headers[0]:<{name_width}} | {headers[1]:<{num_width}} | {headers[2]:<{time_width}} |")
    print(separator)

    # Print each row
    for r in rows:
        print(f"| {r[2]:<{name_width}} | {r[3]:<{num_width}} | {r[4]:<{time_width}} |")

    # Final line
    print(separator)

def handle_create_collection(tokens):
    if(check_if_logged_in()):
        if(len(tokens) != 3 and tokens[2] != None):
            print("collections create <name>")
        else:
            collection = create_collection(UUID, tokens[2])
            if collection == None:
                print("Collection already exists")
                return

def handle_list_collection():
    if(check_if_logged_in()):
        rows = list_users_collections(UUID)
        print_collections(rows)

def handle_rename_collection(tokens):
    if(check_if_logged_in()):
        if(len(tokens) != 4):
            print("collections rename <old_name> <new_name>")
        if(tokens[3] != ""):
            row = rename_collection(UUID, tokens[2], tokens[3])
            if(row == None):
                print("Collection you are trying to rename does not exists")
                return
            handle_list_collection()

def handle_delete_collection(tokens):
    if(len(tokens) == 3 and check_if_logged_in()):
        collection_name = tokens[2]
        if(check_if_collection_exists(UUID, collection_name)):
            response = input("(Y/N) Are you sure you want to delete collection (" + collection_name + "): ")
            if(response.lower() == "y"):
                delete_collection(UUID, collection_name)
            else:
                return
        else:
            print("Collection does not exist")
            return
    


# TODO: ADD PRINT STATEMENTS FOR INSTRUCTIONS


def handle_game_search(tokens):
    if(len(tokens) <  4):
        print("""
games search <field> <keyword>
    Search for games by title, genre, platform, release year, developer,
    publisher, or price range.
    Example: games search genre RPG
              """)
    else:
        term = tokens[2].lower()
        match term:
            case "genre":
                rows = get_game_by_genre(tokens[3])
                print_games(rows=rows)
                return
            case "title":
                rows = get_game_by_title(tokens)
                print_games(rows=rows)
                return
            case "platform":
                rows = get_game_by_platform(tokens[3])
                print_games(rows=rows)
                return
            case "year":
                rows = get_game_by_release_year(tokens[3])
                print_games(rows=rows)
                return
            case "developer":
                rows = get_game_by_developer(tokens)
                print_games(rows=rows)
                return
            case "dev":
                rows = get_game_by_developer(tokens)
                print_games(rows=rows)
                return
            case "publisher":
                rows = get_game_by_publisher(tokens)
                print_games(rows=rows)
                return
            case "pub":
                rows = get_game_by_publisher(tokens)
                print_games(rows=rows)
                return
            case "price":
                if(len(tokens) == 4):
                    rows = get_game_by_price_lower_than(tokens[3])
                    print_games(rows=rows)
                    return  
                elif(len(tokens) == 5):
                    rows = get_game_by_price_between(tokens[3], tokens[4])
                    print_games(rows=rows)
                    return
                else:
                    print("game search price <Max Price> OR \ngame search price <Min Price> <Max price>")

                    return
            case "esrb":
                if(len(tokens) == 4):
                    rows = get_games_by_esrb(tokens[3])
                    print_games(rows=rows)
                    return


def handle_add_platform(tokens):
    if check_if_logged_in():
        try:
            result = add_platform_to_user(uuid=UUID, platform_name=tokens[2])
            if(result != None):
                print("Platform added")
            return

        except Exception as e:
            print(e)
            return None
    else:
        print("Please login")
        return



def handle_sort_result(tokens):
    fields = ["title", "price", "genre", "year"]
    orders = ["asc", "desc"]
    try:
        if(len(tokens) == 2):
            if tokens[1].lower() in fields:
                rows = sort_by(field=tokens[1], order="desc") 
        elif(len(tokens) == 3):
            if tokens[2].lower() in orders:
                rows = sort_by(field=tokens[1], order=tokens[2]) 
        print_games(rows=rows)
    except Exception as e:
        print(e)


def handle_play_game(tokens):
    if not check_if_logged_in():
        print("You must be logged in to play a game.")
        return

    if len(tokens) < 2:
        print("Allowed Formats: \n play <game_name>" \
        "\n play <game_name> <playtime>" \
        "\n play <playtime> <collection_name>")
        return

    if tokens[1] != "":
        game = play_Game(UUID, tokens)
        if game is None:
            print("You do not own the game you are trying to play.")
            return
        else:
            print("Played game: " + game[0] + " for " + game[1] + " minutes.")
            return
    else:
        print("Game name cannot be empty.")

def handle_rate_game(tokens):
    if not check_if_logged_in():
        print("You must be logged in to rate a game.")
        return

    if len(tokens) < 2:
        print("Format must be: rate <game_name> <rating>")
        return 

    if tokens[1] != "":
        game = rate_Game(UUID, tokens)
        if game is None:
            print("The game you are trying to rate does not exist.")
            return
        else:
            print("You gave " + game[0] + " a rating of " + str(game[1]))
            return
    else:
        print("Game name cannot be empty.")


def handle_buy_game(tokens):
    if not check_if_logged_in():
        print("You must be logged in to rate a game.")
        return

    if len(tokens) < 2:
        print("Format must be: buy <game_name>")
        return 

    if tokens[1] != "":
        game = buy_Game(UUID, tokens)
        if game is None:
            print("The game you are trying to buy does not exist.")
            return
        else:
            print("Bought game: " + game)
            return
    else:
        print("Game name cannot be empty.")

def check_if_logged_in():
    if UUID == "" or LOGGED_IN == False:
        print("Please Login to create a collection")
        return False
    return True

def main():
    global UUID, LOGGED_IN

    show_help()
    while(True):
        command = input(">")
        if command == "q" or command == "quit" or command == "exit":
            UUID = ""
            LOGGED_IN = False
            return
        
        tokens = command.split(" ")
        if tokens[0].lower() == "login":
            handle_login_with_email(tokens)
            continue

        elif tokens[0].lower() == "reg" or tokens[0].lower() == "register":
            handle_reg(tokens=tokens)
            continue

        elif tokens[0].lower() == "logout":
            UUID = ""
            LOGGED_IN = False
            continue

        elif tokens[0].lower() == "collections":
            if (len(tokens) == 3  or len(tokens) == 2) and tokens[1] == "create":
                handle_create_collection(tokens)
            elif(len(tokens) == 2 and tokens[1] == "list"):
                handle_list_collection()
            elif(tokens[1].lower() == "rename"):
                handle_rename_collection(tokens)
            elif(tokens[1].lower() == "delete"):
                handle_delete_collection(tokens)
            continue
            
        elif tokens[0].lower() == "game":
            if(len(tokens) >= 2 and tokens[1] == "search"):
                handle_game_search(tokens=tokens)
                continue
        
        elif tokens[0].lower() == "sort":
            if(len(tokens) >= 2):
                handle_sort_result(tokens=tokens)
        elif tokens[0].lower() == "platform":
            if(len(tokens) > 2 and tokens[1] == "add"):
                handle_add_platform(tokens=tokens)
                
        elif tokens[0].lower() == "play":
            if(len(tokens) >= 2):
                handle_play_game(tokens=tokens)
                
        elif tokens[0].lower() == "rate":
            if(len(tokens) >= 2):
                handle_rate_game(tokens=tokens)
                
        elif tokens[0].lower() == "buy":
            if(len(tokens) >= 2):
                handle_buy_game(tokens=tokens)
                

                
if __name__ =="__main__":
    main()