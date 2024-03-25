from random import shuffle
from flask import abort
import sqlite3
from typing import Literal
def card_to_json(string:str) -> dict:
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[string[0]], "value":int(string[1])}
def json_to_card(json:dict) -> str:
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
def access_db() -> tuple:
    conn=sqlite3.connect("uno/database.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db():
    cursor, conn = access_db()
    with open("uno/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()

class Player():
    def __init__(self, username:str, game_id:int, id:int):
        self.username=username
        self.id=id
        self.game_id=game_id
    def _update_db(self, attribute:str, value:str):
        cursor, conn= access_db()
        cursor.execute(f"UPDATE players SET {attribute}='{value}' WHERE username='{self.username} AND game_id={self.game_id}")
        conn.commit()
        conn.close()
    def _get_db_attribute(self, attribute:str):
        cursor, conn= access_db()
        value=cursor.execute(f"SELECT {attribute} FROM hands WHERE username='{self.username}' AND game_id={self.game_id}").fetchone()[0]
        conn.close()
        return value
    @staticmethod
    def _database_property(attribute:str):
        def getter(self) -> str:
            value= self._get_db_attribute(attribute)
            return value
        def setter(self, value:str):
            self._update_db(attribute, value)
        return property(getter, setter)
    position = _database_property("position")
    cards= _database_property("cards")
    number_of_cards = _database_property("number_of_cards")
class Game():
    def _update_db(self, attribute:str, value:str|list):
        cursor, conn= access_db()
        print(f"updating {attribute} to {value}")
        if type(value)==list:
            value=",".join(value)
        cursor.execute(f"UPDATE games SET {attribute}='{value}' WHERE id={self.id}")
        conn.commit()
        conn.close()
    def _get_db_attribute(self, attribute:str):
        cursor, conn= access_db()
        value=cursor.execute(f"SELECT {attribute} FROM games WHERE id={self.id}").fetchone()[0]
        conn.close()
        return value
    @staticmethod
    def _database_property(attribute:str, array=False):
        def getter(self) -> str|list:
            value= self._get_db_attribute(attribute)
            if array:
                return value.split(",")
            return value
        def setter(self, value:str|list):
            if type(value)==list:
                value=",".join(value)
            self._update_db(attribute, value)
        return property(getter, setter)
    number_of_players = _database_property("number_of_players")
    next_player = _database_property("next_player")
    direction = _database_property("direction")
    discard = _database_property("discard")
    draw = _database_property("draw", array=True)
    rules= _database_property("rules", array=True)
    players = _database_property("players", array=True)
    def __repr__(self) -> str:
        return f"Game {self.id=} {self.number_of_players=} {self.players=} {self.next_player=} {self.direction=} {self.discard=} {self.draw=}" 
    def __init__(self, id:int|str) -> None:
        self.id: int=int(id)
    def get_game_info(self) -> dict:
        cursor, conn = access_db()
        hands={username: {"number_of_cards": number_of_cards, "position": position, "you": False} 
               for username, number_of_cards, position in 
               cursor.execute(f"SELECT username, number_of_cards, position FROM hands WHERE game_id={self.id}").fetchall()}
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
        data:dict = self.get_game_info()
        hand:str = self.get_player_hand(username)
        p:dict = data["players"]
        data["players"][username]["you"]=True
        data["players"][username]["hand"]=hand
        return data
    def get_player_hand(self, username:str) -> str:
        player=get_player_by_property("username", username)
        return player.cards
    def add_player(self, username:str) -> None:
        if username in self.players:
            print("player already in game")
            abort(409)
        self.players.append(username)
        self.players=self.players
        self.number_of_players=self.number_of_players+1
        hand=self.draw_card(n=7)
        cursor, conn = access_db()
        cursor.execute(f'INSERT INTO hands(position, game_id, cards, username, number_of_cards) VALUES ({len(self.players)}, {self.id}, "{hand}", "{username}", 7)')
        conn.commit()
        conn.close()
    def draw_card(self, n:int=1):
        self.draw, cards = self.draw[n*2:], self.draw[:n*2]
        return cards
    def player_played_card(self, username: str, card:dict, card_n: int)->int:
        print(self.__repr__())
        print(self.players)
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
    cursor.execute(f"SELECT id FROM games WHERE id={id}")
    game = cursor.fetchone()
    if not game:
        abort(404)
    game=Game(id)
    conn.close()
    return game
def make_game(username:str, rules:str|None) -> Game:
    cursor, conn = access_db()
    this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["u1", "u4"]*4
    shuffle(this_deck)
    this_deck="".join(this_deck)
    cursor.execute(f'INSERT INTO games(next_player, draw, players, number_of_players) VALUES ("{username}", "{this_deck}", "", 0)')
    id=cursor.execute(f'SELECT id FROM games WHERE next_player="{username}" AND draw="{this_deck}"').fetchall()[0][0]
    conn.commit()
    conn.close()
    game = get_game_by_id(id)
    game.add_player(username)
    """THIS NEEDS TO BE DELETED BEFORE IT ENTERS PRODUCTION!!"""
    game.add_player("Ryan Kabir")

    return game
def get_player_by_property(attribute:Literal["username", "id"], value:str) -> Player:
    cursor, conn = access_db()
    cursor.execute(f"SELECT username, game_id, id FROM hands WHERE {attribute}='{value}'")
    player = cursor.fetchone()
    player_obj=Player(*player)
    if not player:
        abort(404)
    conn.close()
    return player_obj