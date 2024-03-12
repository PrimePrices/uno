from random import shuffle
from flask import abort
import sqlite3
def card_to_json(string):
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[string[0]], "value":int(string[1])}
def json_to_card(json):
    return {"green": "g", "blue": "b", "yellow": "y", "red": "r", "none": "u"}[json["colour"]]+json["value"][0]
def connect_db(function):
    def wrapper(* args, ** kwargs):
        conn=sqlite3.connect("uno/database.db")
        cursor=conn.cursor()
        try:
            result=function(cursor, conn, * args, ** kwargs)
        except BaseException as x:
            print(function.__name__ + " error: " + str(x))
            raise x
        finally: conn.close()
        return result
    return wrapper
def access_db():
    conn=sqlite3.connect("uno/database.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db():
    cursor, conn = access_db()
    with open("uno/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()
class Game():
    def __init__(self, id:int|str, rules:str, number_of_players:int, players:str, next_player:str, direction:int|bool, discard: str, draw: str) -> None:
        self.id: int=int(id)
        self.rules: str=rules
        self.number_of_players: int=number_of_players
        self.players: list[str]=players.split(",")
        self.next_player: str=next_player
        self.direction: int=direction
        self.discard:str=discard
        self.draw: str=draw
    def get_game_info(self):
        cursor, conn = access_db()
        hands={username: {"number_of_cards": number_of_cards, "position": position, "you": False} for username, number_of_cards, position in cursor.execute(f"SELECT username, number_of_cards, position FROM hands WHERE game_id={self.id}").fetchall()}
        conn.close()
        return {"id": self.id, 
                "rules": self.rules, 
                "number_of_players":self.number_of_players, 
                "players": hands, 
                "next_player": self.next_player, 
                "direction": self.direction, 
                "discard": card_to_json(self.discard), 
                "draw_length": len(self.draw)//2}
    def get_game_info_personalised(self, username:str):
        data= self.get_game_info()
        hand = self.get_player_hand(username)
        p:dict = data["players"]
        data["players"][username]["you"]=True
        data["players"][username]["hand"]=hand
        return data
    def get_player_hand(self, username:str):
        cursor, conn = access_db()
        cursor.execute(f"SELECT cards FROM hands WHERE username='{username}' AND game_id={self.id}")
        hand = cursor.fetchone()[0]
        conn.close()
        return hand
    def add_player(self, username:str)->None:
        if username in self.players:
            print("player already in game")
            abort(409)
        self.players.append(username)
        hand=self.draw_card(n=7)
        cursor, conn = access_db()
        cursor.execute(f'INSERT INTO hands(position, game_id, cards, username, number_of_cards) VALUES ({len(self.players)}, {self.id}, "{hand}", "{username}", 7)')
        cursor.execute(f'UPDATE games SET players="{",".join(self.players)}", number_of_players={len(self.players)} WHERE id={self.id}')
        conn.commit()
        conn.close()
    def draw_card(self, n:int=1):
        self.draw, cards = self.draw[n*2:], self.draw[:n*2]
        cursor, conn = access_db()
        cursor.execute(f"UPDATE games SET draw='{self.draw}' WHERE id={self.id}")
        conn.close()
        return cards
    def player_played_card(self, username: str, card:dict, card_n: int)->int:
        if username not in self.players:
            print("player not in game so can't play card")
            abort(414)
        hand = self.get_player_hand(username)
        card_str=json_to_card(card)
        
        if card_str not in hand:
            print("card not in hand")
            abort(414)
        card_n=int(card_n)
        print(f"{card_str=} {card_n=}")
        if hand[card_n*2:card_n*2+2] != card_str:
            print("invalid card position")
            print(f"{hand[card_n*2:card_n*2+2]=}")
            abort(418)
        cursor, conn = access_db()
        cursor.execute(f"UPDATE hands SET cards='{hand.replace(card_str, "")}', number_of_cards=number_of_cards-1 WHERE game_id={self.id} AND username='{username}'")
        conn.commit()
        cards_left=cursor.execute(f"SELECT number_of_cards FROM hands WHERE game_id={self.id} AND username='{username}'").fetchone()[0]
        conn.close()
        return cards_left


def get_game_by_id(id) -> Game:
    #this needs to also return none if the game doesn't exist
    cursor, conn = access_db()
    cursor.execute(f"SELECT * FROM games WHERE id={id}")
    game = cursor.fetchone()
    if not game:
        abort(404)
    game=Game(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7])
    conn.close()
    return game
def make_game(username:str, rules:str|None) -> Game:
    cursor, conn = access_db()
    this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["u1", "u4"]*4
    shuffle(this_deck)
    this_deck="".join(this_deck)
    cursor.execute(f'INSERT INTO games(rules, number_of_players, players, next_player, direction, discard, draw) VALUES ("{str(rules)}", 0, "", "{username}", 0, "g5", "{this_deck}")')
    id=cursor.execute(f'SELECT id FROM games WHERE next_player="{username}" AND draw="{this_deck}"').fetchall()[0][0]
    conn.commit()
    game = get_game_by_id(id)
    game.add_player(username)
    """THIS NEEDS TO BE DELETED BEFOR IT ENTERS PRODUCTION!!"""
    game.add_player("Ryan Kabir")
    conn.close()
    return game