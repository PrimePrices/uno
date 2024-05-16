from random import shuffle
from flask import abort
import sqlite3
from typing import Any, Literal
from flask import abort


def card_to_json(string:str) -> dict:
    return {"colour": {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[string[0]],
            "value": {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"r":"reverse","d":"draw2", "s":"skip"}[string[1]]}
def json_to_card(json:dict) -> str:
    return {"green": "g", "blue": "b", "yellow": "y", "red": "r", "none": "u"}[json["colour"]]+json["value"][0]
def access_db() -> tuple:
    conn=sqlite3.connect("apps/uno/database.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db() -> None:
    cursor, conn = access_db()
    with open("apps/uno/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()

class PlayerException(Exception):
    pass
class GameException(Exception):
    pass
class DBClass:
    table="default"
    def __init__(self):self.id=None # This stops the self.id from causing errors when the code is parsed
    def _update_db(self, attribute:str, value:str|list):
        cursor, conn= access_db()
        print(f"updating {attribute} to {value}")
        if type(value)==list:
            value=",".join(value)
        cursor.execute(f"UPDATE {self.table} SET {attribute}='{value}' WHERE id={self.id}")
        conn.commit()
        conn.close()
    def _get_db_attribute(self, attribute:str):
        cursor, conn= access_db()
        value=cursor.execute(f"SELECT {attribute} FROM {self.table} WHERE id={self.id}").fetchone()[0]
        conn.close()
        return value
    @staticmethod
    def _database_property(attribute:str) -> property:
        def getter(self) -> str:
            value= self._get_db_attribute(attribute)
            return value
        def setter(self, value:str|list):
            if type(value)==list:
                value=",".join(value)
            self._update_db(attribute, value)
        return property(getter, setter)
    @staticmethod
    def _database_list(attribute:str, data_type=None) -> property:
        def getter(self) -> CSVList:
            return CSVList(table=self.table, entry_uid=self.id, column=attribute, data_type=data_type)
        def setter(self, iterable:list) -> None:
            CSVList(iterable=iterable, table=self.table, entry_uid=self.id, column=attribute, data_type=data_type)
        return property(getter, setter)
class CSVList(list):
    __slots__=["data", "table", "entry_uid", "column", "data_type"]
    def __init__(self, iterable=None, table=None, entry_uid=None, column=None, data_type=None):
        self.table=table
        self.entry_uid=entry_uid
        self.column=column
        self.data_type=data_type
        if iterable!=None:
            self.set_list(iterable)
    def __contains__(self, value):
        return value in self.get_list()
    def cast_list(self, data):
        if self.data_type==None:
            return data
        a=[]
        if not(data):
            print(f"trying to cast {data=}, appently null")
            return []
        for i in data:
            try:
                a.append(self.data_type(i))
            except:
                raise TypeError(f"Expected value that could be cast into {self.data_type}. Instead got {i} of type={type(i)}")
        return a
    def __getitem__(self, index):#
        return self.get_list()[index]
    def get_list(self) -> list:
        cursor, conn=access_db() 
        data:str=cursor.execute(f"SELECT {self.column} FROM {self.table} WHERE id={self.entry_uid}").fetchone()[0]
        conn.close()
        if not data:
            #print(f"{data=}")
            return []
        list_data: list[str]=data.split(",")
        list_data=self.cast_list(list_data)
        #if self.column!="draw":
            #print(f"FROM get_list SELECT {self.column} FROM {self.table} WHERE id={self.entry_uid} RETRUNS" , data)
            #print(f"LIST_DATA = {list_data}, {type(list_data)=}")
            #print("\n".join([str(i.code_context) for i in stack()]))
        return list_data
    def set_list(self, l:list) -> None:
        if self.data_type!=None:
            l=[str(i) for i in l]
        string=",".join(l)
        cursor, conn=access_db()
        cursor.execute(f"UPDATE {self.table} SET {self.column}='{string}' WHERE id={self.entry_uid}")
        conn.commit()
        conn.close()
    def append(self, value):
        data=self.get_list()
        data.append(value)
        self.set_list(data)
    def pop(self, index):
        data=self.get_list()
        r=data.pop(index)
        self.set_list(data)
        return r
    def __setitem__(self, index, item):
        if type(item)==str and "," in item:
            raise TypeError("Text cannot contain a comma")
        try:
            item=str(item)
        except:
            raise TypeError(f"Item {item} of type {type(item)} couldn't be converted to a string")
        data=self.get_list()
        data[index]=item
        self.set_list(data)
    def __str__(self):
        return str(self.get_list())
    def __len__(self):
        return len(self.get_list())
    def __iter__(self):
        return iter(self.get_list())
    def __list__(self):
        return list(self.get_list())

class Player(DBClass):
    table="hands"
    position = DBClass._database_property("position")
    cards= DBClass._database_list("cards", data_type=str)
    number_of_cards = DBClass._database_property("number_of_cards")

    def __init__(self, username:str, game_id=None, row_id=None):
        self.username=username
        cursor,conn=access_db()
        if game_id != None:
            data = cursor.execute(f"SELECT id FROM {self.table} WHERE username='{username}' AND game_id={game_id}").fetchone()
            self.game_id=game_id  
        else: 
            data = cursor.execute(f"SELECT id, game_id FROM {self.table} WHERE username='{username}'").fetchone()
            self.game_id=data[1]
        conn.close()
        if not data:
            raise PlayerException("Player not valid")
        self.id = data[0]
    def __str__(self) -> str:
        return self.username
    def played_a_card(self, card:str, card_n:int)->int:
        if self.cards[card_n]==card:
            self.cards.pop(card_n)
            self.number_of_cards=self.number_of_cards-1
            return self.number_of_cards
        else:
            raise BaseException(f"Data was invalid, {card=} not in position {card_n} of {self.cards}")
    def __repr__(self) -> str:
        return f"Player (username: {self.username}, cards: {self.cards}, number_of_cards: {self.number_of_cards}, game_id: {self.game_id}, position: {self.position}, id: {self.id})"

        
class Game(DBClass):
    table="games"
    number_of_players:property = DBClass._database_property("number_of_players")
    next_player:property = DBClass._database_property("next_player") #the player currently to play
    direction:property = DBClass._database_property("direction")
    discard:property = DBClass._database_list("discard", data_type=str)
    draw:property = DBClass._database_list("draw", data_type=str)
    rules:property= DBClass._database_list("rules", data_type=str)
    players:property = DBClass._database_list("players", data_type=Player)
    last_activity:property = DBClass._database_property("last_activity")
    def __repr__(self) -> str:
        return f"Game {self.id=} {self.number_of_players=} {self.players[:]=} {self.next_player=} {self.direction=} {self.discard=} {self.draw=}" 
    def __init__(self, id:int|None=None, create=False, username: str|None=None, rules=None) -> None:
        if create:
            this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["u1", "u4"]*4
            shuffle(this_deck)
            cursor, conn = access_db()
            cursor.execute(f'INSERT INTO games(next_player, players, number_of_players) VALUES ("{username}", "", 0)')
            self.id=cursor.lastrowid
            conn.commit()
            conn.close()
            self.draw=this_deck
            self.rules=rules
            self.discard=[this_deck.pop()]
            self.add_player(username) # type: ignore
            """THIS NEEDS TO BE DELETED BEFORE IT ENTERS PRODUCTION!!"""
            self.add_player("Ryan Kabir")
        else:
            cursor, conn = access_db()
            id=int(id) # type:ignore 
            data=cursor.execute(f'SELECT id FROM {self.table} WHERE id="{id}"').fetchone()
            conn.close()
            if data:
                self.id=int(id)
            else:
                raise GameException("Game doesn't exist")
    def increment_players(self) -> None:
        if self.direction == 0:
            self.players = self.players[1:].append(self.players[0])
        else:
            self.players = [self.players[-1]]+self.players[:-1]
        self.next_player=self.players[0]
    def get_game_info(self) -> dict[str, (dict|int|list|str)]:
        """Returns a dictionary of information about the game
        
        Arguments:
            self {Game} -- The Game object
        
        Returns:
            dict[str, (int|list|str)] -- A dictionary of information about the game

        Dict keys:
            id:int
            rules:list
            number_of_players:int
            players:dict
            next_player:str
            direction:int[0|1]
            discard:str
            draw_length:int
        """
        rules: list[str]=self.rules
        players: list[Player]=self.players
        return {"id": self.id, 
                "rules": rules, 
                "number_of_players":self.number_of_players, 
                "players": {player.username: 
                                {"number_of_cards": player.number_of_cards, 
                                 "position": player.position, 
                                 "you": False} 
                            for player in players}, 
                "next_player": self.next_player, 
                "direction": self.direction, 
                "discard": card_to_json(self.discard[-1]), 
                "draw_length": len(self.draw)//2}
    def get_game_info_personalised(self, username:str) -> dict[str, (str|dict|list)]:
        data:dict = self.get_game_info()
        #print(data)
        hand:str = self.get_player_hand(username)
        data["players"][username]["you"]=True
        data["players"][username]["hand"]=[card_to_json(card) for card in hand]
        return data
    def get_player_hand(self, username:str) -> str:
        return Player(username, game_id=self.id).cards
    def add_player(self, username:str) -> Player:
        if username in self.players:
            print("player already in game")
            abort(409)
        self.players.append(username)
        self.number_of_players=self.number_of_players+1
        hand=self.draw_card(n=7)
        cursor, conn = access_db()
        cursor.execute(f'INSERT INTO hands(position, game_id, username, number_of_cards) VALUES ({self.number_of_players}, {self.id}, "{username}", 7)')
        id=cursor.lastrowid
        #print(f"{id=}")
        conn.commit()
        conn.close()
        player=Player(username, game_id=self.id, row_id=id)
        player.cards=hand
        return player
    def draw_card(self, n:int=1) -> list["str"]:
        self.draw, cards = self.draw[n:], self.draw[:n]
        return cards
    def player_played_card(self, username: str, card:dict, card_n: int, colour=None) -> int:
        player=Player(username, game_id=self.id)
        hand = player.cards
        card_str=json_to_card(card)
        if not self.check_if_card_is_valid(card_str, player):
            abort(422, description="card invalid")
        cards_left=player.played_a_card(card_str, int(card_n))
        if card_str in ["u4", "uw"]:
            if colour not in ["g", "r", "b", "y"]:
                abort(422, description="colour not provided")
            self.discard.append(colour+card_str)
        else:
            self.discard.append(card_str)
        self.increment_players()
        return cards_left
    def check_if_card_is_valid(self, card:str, player) -> bool:
        if card not in player.cards:
            abort(422, description="card not in hand")
        value=self.compare_card(card, self.discard[-1])
        print(f"comparison {value=} between {card=} and {self.discard[-1]=}; {self.next_player=}, {player.__repr__()=}")
        if "anyone_can_play_with_identical_cards" in self.rules and value==2:
            return True
        if bool(value) and self.next_player==player:
            return True
        if type(player)==Player:
            if bool(value) and self.next_player==player.username:
                return True
        return False
    def compare_card(self,card, discard)->int: #marker extend for specials
        if card==discard[0]+discard[1]:
            return 2
        if len(discard)>=3:
            if card[0]==discard[2]:
                return 1
        else:
            if card[0]==discard[0]:
                return 1
            if card[1]==discard[1]:
                return 1
            if card[0]=="u":
                return 1
        if card[1]==discard[1]:
            return 1
        return 0  


def make_game(username:str, rules:str|None) -> Game:
    return Game(username=username, create=True, rules=rules)
def get_player_by_property(attribute:Literal["username", "id"], value:str) -> Player:
    cursor, conn = access_db()
    cursor.execute(f"SELECT username, game_id, id FROM hands WHERE {attribute}='{value}'")
    player = cursor.fetchone()
    conn.close()
    if not player:
        abort(404)
    player_obj=Player(player[0], game_id=player[1], row_id=player[2])
    return player_obj
