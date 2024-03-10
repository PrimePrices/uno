import sqlite3, random
from flask_login import current_user
from flask import abort
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("uno/database.db")
        cursor=conn.cursor()
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__ + " error: " + str(x))
            raise
        finally: conn.close()
        return result
    return wrapper
# type: ignore
def access_db():
    conn=sqlite3.connect("uno/database.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db():
    cursor, conn = access_db()
    with open("uno/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()
def card_to_json(string):
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[string[0]], "value":int(string[1])}
def json_to_card(json):
    return {"green": "g", "blue": "b", "yellow": "y", "red": "r", "none": "u"}[json["colour"]]+json["value"][0]
def get_game_info(id):
    cursor, conn = access_db()
    cursor.execute(f'SELECT * FROM games WHERE id={id};')
    a=cursor.fetchall()[0]
    cursor.execute(f'SELECT username, number_of_cards, position FROM hands WHERE game_id={id}')
    hands=cursor.fetchall()
    data=[]
    for i in hands:
        data.append({"position":i[2], "number_of_cards":i[1], "username":i[0]})
    discard=card_to_json(a[6])
    conn.close()
    return {"id": a[0], "rules": a[1], "number_of_players":a[2], "players": data, "next_player": a[4], "direction": a[5], "discard": discard, "draw_length":len(a[7])//2}
def get_game_info_personalised(id, user):
    cursor, conn = access_db()
    data=get_game_info(id)
    cursor.execute(f'SELECT cards FROM hands WHERE username="{user}"')
    a = cursor.fetchall()[0]
    for i in data["players"]:
        if i["username"]==user:
            i["hand"]=a[0]
            data["you"]=i
        i["you"]=(i["username"]==user)
    print(data)
    conn.close()
    return data
def make_game(rules, user):
    cursor, conn= access_db()
    data=cursor.fetchall()
    print(f"{data=} sent for make_game")
    if data: # checks if player is already in game or not
        return "game/"+str(data[0][2])    #need to get link for game
    this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["u1", "u4"]*4
    random.shuffle(this_deck)
    this_deck="".join(this_deck)
    cursor.execute(f'INSERT INTO games(rules, number_of_players, players, next_player, direction, discard, draw) VALUES ("{rules}", 0, "", "{user}", 0, "g5", "{this_deck}")')
    link=cursor.execute(f'SELECT id FROM games WHERE next_player="{user}" AND draw="{this_deck}"').fetchall()[0][0]
    conn.commit()
    print("Made Game")
    add_player(link, user)
    """THIS NEEDS TO BE DELETED BEFOR IT ENTERS PRODUCTION!!"""
    add_player(link, "Ryan Kabir")
    conn.close()
    return "game/"+str(link)
def draw_card(game, number_of_cards=1):
    cursor, conn = access_db()
    cursor.execute(f"SELECT draw FROM games WHERE id='{game}'")
    draw=cursor.fetchall()[0][0]
    if len(draw)>=number_of_cards*2:
        cards=draw[:number_of_cards*2]
        draw=draw[number_of_cards*2:]
        cursor.execute(f"UPDATE games SET draw='{draw}' WHERE id='{game}'")
        conn.commit()
        conn.close
        return cards
    else: 
        conn.close()
        return "g6"*number_of_cards
def check_if_player_is_in_game(game, player):
    cursor, conn = access_db()
    cursor.execute(f'SELECT * FROM hands WHERE game_id={game} AND username="{player}"')
    data=cursor.fetchall()
    conn.close()
    return bool(data)
def add_player(game, player): # returns game=> possibly unnecessary
    if check_if_player_is_in_game(game, player):
        return "error 409"
    cursor, conn= access_db()
    cursor.execute(f'SELECT number_of_players, players FROM games WHERE id="{game}"')
    data=cursor.fetchall()[0]
    number_of_players=data[0]
    players=data[1]
    hand=draw_card(game, number_of_cards=7)
    cursor.execute(f'UPDATE games SET number_of_players={number_of_players+1}, players="{players+","+player}" WHERE id={game}')
    cursor.execute(f'INSERT INTO hands(position, game_id, cards, username, number_of_cards) VALUES ({number_of_players}, {game}, "{hand}", "{player}", 7)')
    conn.commit()
    conn.close()
    return game
def validate_game_exists(game_id):
    cursor, conn = access_db()
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM games WHERE id={game_id})")
    data=cursor.fetchone()[0]
    conn.close()
    return data
def player_played_card(game_id: int, username: str, card:dict, card_n: int):
    if not validate_game_exists(game_id):
        abort(404)
    if not check_if_player_is_in_game(game_id, username):
        abort(414)
    cursor, conn = access_db()
    cursor.execute(f"SELECT cards FROM hands WHERE game_id={game_id} AND username='{username}'")
    data=cursor.fetchone()[0]
    card_str=json_to_card(card)
    print(card_str)
    if card_str not in data:
        print("card not in hand")
        abort(414)
    cursor.execute(f"UPDATE hands SET cards='{data.replace(card_str, "")}' WHERE game_id={game_id} AND username='{username}'")
    conn.commit()
    print(data)
    conn.close()

"""
A user can't log on twice with the same account
Users not logged on get given a random account generated with a "<game_id>;<position>;<random 10 letter string>"
Usernames can only use abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-1234567890
"""