import sqlite3, random
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("database.db")
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

@connect_db
def init_db(cursor, conn):
    with open("create.sql", "r") as create:
        cursor.executescript(create.read())

def card_to_json(string):
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red"}[string[0]], "value":int(string[1])}

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
@connect_db
def get_game_info_personalised(cursor, conn, id, user):
    data=get_game_info(id)
    print(data)
    cursor.execute(f'SELECT cards FROM hands WHERE username="{user}"')
    a = cursor.fetchall()[0]
    print(f"players-hand={a}")
    for i in data["players"]:
        if i["username"]==user:
            i["hand"]=a[0]
        
    print(data)
    return data

@connect_db
def make_game(cursor, conn, rules, user):
    this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["uw", "u4"]*4
    random.shuffle(this_deck)
    this_deck="".join(this_deck)
    cursor.execute(f'INSERT INTO games(rules, number_of_players, players, next_player, direction, discard, draw) VALUES ("{rules}", 0, "", "{user}", 0, "g5", "{this_deck}")')
    link=cursor.execute(f'SELECT id FROM games WHERE next_player="{user}" AND draw="{this_deck}"').fetchall()[0][0]
    conn.commit()
    print("Made Game")
    print(cursor.execute(f'SELECT * FROM games WHERE next_player="{user}"').fetchall()[0])
    add_player(cursor, conn, link, user)
    return "game/"+str(link)
def check_if_player_is_in_game(cursor, conn, game, player):
    cursor.execute(f'SELECT * FROM hands WHERE game_id={game} AND username="{player}"')
    data=cursor.fetchall()
    print(f"{data=}")
    return bool(data)
def add_player(cursor, conn, game, player):
    if check_if_player_is_in_game(cursor, conn, game, player):
        return "error 409"
    cursor.execute(f'SELECT number_of_players, players, draw FROM games WHERE id={game}')
    data=cursor.fetchall()[0]
    print(f"{data=}")
    number_of_players=data[0]
    players=data[1]
    draw=data[2]
    cursor.execute(f'SELECT draw FROM games WHERE id={game}')
    draw=cursor.fetchall()[0]#[0]
    print(f"{draw=}")
    hand=draw[:14]
    draw=draw[14:]
    print(f"given hand {hand} to {player} leaving a deck of {draw}")
    cursor.execute(f'UPDATE games SET draw="{draw}", number_of_players={number_of_players+1}, players="{players+","+player}" WHERE id={game}')
    cursor.execute(f'INSERT INTO hands(position, game_id, cards, username, number_of_cards) VALUES ({number_of_players}, {game}, "{"".join(hand)}", "{player}", 7)')
    conn.commit()
    return game
    
"""
A user can't log on twice with the same account
Users not logged on get given a random account generated with a "<game_id>;<position>;<random 10 letter string>"
Usernames can only use abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-1234567890
"""