import sqlite3, random
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("uno/database.db")
        cursor=conn.cursor()
        print(f"{function.__name__} access granted")
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__)
            raise
        finally: conn.close()
        print(f"{function.__name__} access finished")
        return result
    return wrapper
# type: ignore
@connect_db
def init_db(cursor, conn):
    with open("uno/create.sql", "r") as create:
        cursor.executescript(create.read())

def card_to_json(string):
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[string[0]], "value":int(string[1])}
# type: ignore
@connect_db
def get_game_info(cursor, conn, id):
    cursor.execute(f'SELECT * FROM games WHERE id={id};')
    a=cursor.fetchall()[0]
    cursor.execute(f'SELECT username, number_of_cards, position FROM hands WHERE game_id={id}')
    hands=cursor.fetchall()
    data=[]
    for i in hands:
        data.append({"position":i[2], "number_of_cards":i[1], "username":i[0]})
    discard=card_to_json(a[6])
    return {"id": a[0], "rules": a[1], "number_of_players":a[2], "players": data, "next_player": a[4], "direction": a[5], "discard": discard, "draw_length":len(a[7])//2}
# type: ignore
@connect_db
def get_game_info_personalised(cursor, conn, id, user):
    data=get_game_info(id)
    print(data)
    cursor.execute(f'SELECT cards FROM hands WHERE username="{user}"')
    a = cursor.fetchall()[0]
    print(f"players-hand={a} sent from get_game_info_personalised")
    for i in data["players"]:
        if i["username"]==user:
            i["hand"]=a[0]
            data["you"]=i
        i["you"]=(i["username"]==user)
    print(data)
    return data
# type: ignore
@connect_db
def make_game(cursor, conn, rules, user):
    cursor.execute(f"SELECT * FROM hands WHERE username='{user}'")
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
    print(cursor.execute(f'SELECT * FROM games WHERE next_player="{user}"').fetchall()[0])
    add_player(cursor, conn, link, user)
    """THIS NEEDS TO BE DELETED BEFOR IT ENTERS PRODUCTION!!"""
    add_player(cursor, conn, link, "Ryan Kabir")
    return "game/"+str(link)
def draw_card(cursor, conn, game, number_of_cards=1):
    cursor.execute(f"SELECT draw FROM games WHERE id='{game}'")
    draw=cursor.fetchall()[0][0]
    print(f"{draw=} sent from draw_card")
    if len(draw)>=number_of_cards*2:
        cards=draw[:number_of_cards*2]
        draw=draw[number_of_cards*2:]
        cursor.execute(f"UPDATE games SET draw='{draw}' WHERE id='{game}'")
        conn.commit()
        return cards
    else: 
        return "g6"*number_of_cards
def check_if_player_is_in_game(cursor, conn, game, player):
    cursor.execute(f'SELECT * FROM hands WHERE game_id={game} AND username="{player}"')
    data=cursor.fetchall()
    print(f"{data=}")
    return bool(data)
def add_player(cursor, conn, game, player): # returns game=> possibly unnecessary
    if check_if_player_is_in_game(cursor, conn, game, player):
        return "error 409"
    cursor.execute(f'SELECT number_of_players, players FROM games WHERE id="{game}"')
    data=cursor.fetchall()[0]
    print(f"{data=} sent from add_player")
    number_of_players=data[0]
    players=data[1]
    hand=draw_card(cursor, conn, game, number_of_cards=7)
    cursor.execute(f'UPDATE games SET number_of_players={number_of_players+1}, players="{players+","+player}" WHERE id={game}')
    cursor.execute(f'INSERT INTO hands(position, game_id, cards, username, number_of_cards) VALUES ({number_of_players}, {game}, "{hand}", "{player}", 7)')
    conn.commit()
    return game
"""
A user can't log on twice with the same account
Users not logged on get given a random account generated with a "<game_id>;<position>;<random 10 letter string>"
Usernames can only use abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-1234567890
"""