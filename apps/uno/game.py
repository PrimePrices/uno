from random import shuffle
from flask import abort
from typing import Any, Literal
from flask import abort
from .db import DBClass, CSVList, get_db
from .transmit import transmit

COLOUR_LOOKUP_SHORTHAND = {"green": "g", "blue": "b", "yellow": "y", "red": "r", "none": "u"}
COLOUR_LOOKUP_LONGHAND = {"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}
VALUE_LOOKUP_SHORTHAND = {"0": "0", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", 
                          0:"0", 1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",
                          "reverse": "r", "draw2": "d", "skip": "s", "wild": "w", "draw4": "d4"}
VALUE_LOOKUP_LONGHAND = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "r":"reverse","d":"draw2", "s":"skip", "d4":"draw4", "w":"wild"}
# These should oly be used when handling the database
def card_to_json(string:str) -> dict:
    return {"colour": COLOUR_LOOKUP_LONGHAND[string[0]],
            "value": VALUE_LOOKUP_LONGHAND[string[1:]]}
def json_to_card(json:dict) -> str:
    return COLOUR_LOOKUP_SHORTHAND[json["colour"]]+VALUE_LOOKUP_SHORTHAND[json["value"]]
class Card:
    def __init__(self, colour:str, value:str|int):
        if colour not in ["green", "blue", "yellow", "red", "none"]:
            try:
                colour={"g": "green", "b": "blue", "y":"yellow", "r":"red", "u": "none"}[colour]
            except KeyError:
                raise CardInvalidException("colour invalid")
        if value not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "reverse", "draw2", "skip"]:
            print(f"value exception for card {colour} {value}" )
            raise CardInvalidException("value invalid")
        self.colour=colour
        self.value=value
    def __str__(self) -> str:
        return self.colour+" "+str(self.value)
    def __eq__(self, card) -> bool:
        return self.colour==card.colour and self.value==card.value
    def __gt__(self, card) -> bool:
        return self.value>card.value if self.value!=card.value else self.colour>card.colour
    def __lt__(self, card) -> bool:
        return self.value<card.value if self.value!=card.value else self.colour<card.colour

class PlayerException(Exception):
    pass
class GameException(Exception):
    pass
class CardInvalidException(Exception):
    pass
class ColourNotProvidedException(Exception):
    pass

class Player(DBClass):
    table="hands"
    position = DBClass._database_property("position")
    cards= DBClass._database_list("cards", data_type=str)
    number_of_cards = DBClass._database_property("number_of_cards")
    request_sid = DBClass._database_property("request_sid")
    def __init__(self, username:str, game_id=None, row_id=None):
        self.username=username
        conn=get_db()
        if game_id != None:
            data = conn.execute(f"SELECT id FROM {self.table} WHERE username='{username}' AND game_id={game_id}").fetchone()
            self.game_id=game_id  
        else: 
            data = conn.execute(f"SELECT id, game_id FROM {self.table} WHERE username='{username}'").fetchone()
            self.game_id=data[1]
        conn.close()
        if not data:
            raise PlayerException("Player not valid")
        self.id = data[0]
    def __str__(self) -> str:
        return self.username
    def played_a_card(self, card:str, card_n:int)->int:
        self.cards.pop(card_n)
        self.number_of_cards=self.number_of_cards-1
        return self.number_of_cards
    def drew_a_card(self, card:str):
        self.number_of_cards=self.number_of_cards+1
        self.cards.append(card)
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
    last_activity:property = DBClass._database_property("last_activity")
    def __repr__(self) -> str:
        return f"Game {self.id=} {self.number_of_players=} {self.next_player=} {self.direction=} {self.discard=} {self.draw=}" 
    def __init__(self, id:int|None=None, create=False, username: str|None=None, rules=None) -> None:
        if create:
            this_deck=["r0", "y0", "b0", "g0"]+[i+j for i in "rgby" for j in "123456789rsd"]*2+["u1", "u4"]*4
            shuffle(this_deck)
            conn = get_db()
            self.id=conn.execute(f'INSERT INTO games(next_player, number_of_players) VALUES ("{username}", 0)').lastrowid
            conn.commit()
            conn.close()
            self.draw=this_deck
            self.rules=rules
            self.discard=[this_deck.pop()]
            while self.discard[-1][0]=="u":
                self.discard.append(this_deck.pop())
            self.add_player(username) # type: ignore
        else:
            conn = get_db()
            id=int(id) # type:ignore 
            data=conn.execute(f'SELECT id FROM {self.table} WHERE id="{id}"').fetchone()
            conn.close()
            if data:
                self.id=int(id)
            else:
                print(f"{id=}")
                raise GameException("Game doesn't exist")
    def increment_players(self, transmit_increment=False, previous_function=None) -> None: 
        """
        Shift the order of the players
        Not to be called alongside reverse_players()
        """
        players=self.get_players()
        if len(players) == 1:
            return None
        if self.direction == 0:
            players.append(players.pop(0))
        else:
            players=[players[-1]]+players[:-1]
        for n, v in enumerate(players):
            v.position=n
        self.next_player=players[0]
        print(f"{self.next_player=}  {previous_function=}(game.increment_players)")
        if transmit_increment:
            transmit(self.id, "players_turn", self.next_player, {})# type:ignore
    def reverse_players(self, transmit_increment=False):
        """
        Reverse the order of the players
        To be called instead of increment_players
        """
        players=self.get_players()
        if self.number_of_players == 2:
            return None
        players.reverse()
        for n, v in enumerate(players):
            v.position=n
        self.next_player=players[0]
        if transmit_increment:
            transmit(self.id, "players_turn", self.next_player, {})# type:ignore
    def get_players(self) -> list[Player]:
        conn=get_db()
        data=conn.execute(f"SELECT id, username FROM hands WHERE game_id={self.id}").fetchall()
        conn.close()
        players=[Player(row[1], game_id=self.id, row_id=row[0]) for row in data]
        players.sort(key=lambda player: player.position) 
        return players
    def get_game_info(self) -> dict[str, Any|dict|int|list|str]:
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
        players: list[Player] = self.get_players()
        return {"id": self.id, 
                "rules": rules, 
                "number_of_players":self.number_of_players, 
                "players": {player.username: 
                                {"number_of_cards": len(self.get_player_hand(player.username)), 
                                 "position": player.position, 
                                 "you": False} 
                            for player in players}, 
                "next_player": self.next_player, 
                "direction": self.direction, 
                "discard": card_to_json(self.discard[-1]), 
                "draw_length": len(self.draw)//2}
    def get_game_info_personalised(self, username:str) -> dict[str, (str|dict|list)]:
        data:dict = self.get_game_info()
        hand:str = self.get_player_hand(username)
        data["players"][username]["you"]=True
        data["players"][username]["hand"]=[card_to_json(card) for card in hand]
        return data
    def get_player_hand(self, username:str) -> str:
        return Player(username, game_id=self.id).cards
    def add_player(self, username:str) -> Player:
        conn = get_db()
        data = conn.execute(f"SELECT id FROM hands WHERE username='{username}' AND game_id={self.id}").fetchone()
        if data:
            print("ERROR player already in game (Game.add_player)")
            abort(409)
        self.number_of_players=self.number_of_players+1
        hand=self.draw_card(n=7)
        
        id = conn.execute(f'''INSERT INTO hands(position, game_id, username, number_of_cards) VALUES 
                          ({self.number_of_players}, {self.id}, "{username}", 7)''').lastrowid
        conn.commit()
        conn.close()
        player=Player(username, game_id=self.id, row_id=id)
        player.cards=hand
        return player
    def draw_card(self, n:int=1) -> list["str"]:
        """Returns a list of cards drawn from the draw pile of length n
        Default n=1"""
        self.draw, cards = self.draw[n:], self.draw[:n]
        return cards
    def player_played_card(self, username: str, card:dict, card_n: int, colour=None) -> int:
        player: Player=Player(username, game_id=self.id)
        if type(card_n) != int:
            card_n=int(card_n)
        hand = player.cards
        print(f"{card=} {card_n=} {colour=} {self.next_player=}")
        if not self.check_if_card_is_valid(card, card_n, player):
            raise CardInvalidException("card invalid")
        card_str = json_to_card(card)
        cards_left=player.played_a_card(card_str, int(card_n))
        self.discard.append(card_str)
        transmit(int(self.id), #type:ignore
                 "player_played_a_card", 
                 username, 
                 {"card": card, "card_n": card_n, "cards_left": cards_left})
        if card["value"] == "draw2":
            self.increment_players(previous_function="game.player_played_card@draw2")
            next_player=Player(self.next_player, game_id=self.id)
            for i in range(2):
                next_player.drew_a_card(drawn_cards:=self.draw_card()[0])
                transmit(self.id, "player_drew_a_card", next_player.username, {}, # type:ignore
                          exclue_request_sid=True, request_sid=next_player.request_sid,
                          private_message={"action": "you_drew_a_card", "card": card_to_json(drawn_cards)})
        if card["value"] == "draw4":
            self.increment_players(transmit_increment=False, previous_function="game.player_played_card@draw4")
            next_player=Player(self.next_player, game_id=self.id)
            for i in range(4):
                next_player.drew_a_card(drawn_card:=self.draw_card()[0])
                transmit(self.id, "player_drew_a_card", next_player.username, {}, # type:ignore
                          exclue_request_sid=True, request_sid=next_player.request_sid,
                          private_message={"action": "you_drew_a_card", "card": card_to_json(drawn_card)})
        if card["value"] == "skip":
            self.increment_players(transmit_increment=False, previous_function="game.player_played_card@skip")
        if card["value"] == "reverse":
            self.reverse_players(transmit_increment=True)
            return cards_left
        else:
            self.increment_players(transmit_increment=True, previous_function="game.player_played_card@normal")

        print()
        print()
        return cards_left
    def check_if_card_is_valid(self, card:dict, card_n: int, player: Player) -> bool:
        print("checking card validity")
        print(f"cards = {str(player.cards)}")
        if card["value"] in ("wild", "draw4"):
            if card["value"] == "wild":
                if ("uw" not in player.cards) and ("u1" not in player.cards) :
                    raise CardInvalidException("card not found in hand")
                if player.cards[card_n] not in ("uw", "u1"):
                    print("card not at specified location in hand")
                    raise CardInvalidException("card not valid")
            if card["value"] == "draw4":
                if "u4" not in player.cards:
                    raise CardInvalidException("card not found in hand")
                if player.cards[card_n]!="u4":
                    print("card not at specified location in hand")
                    raise CardInvalidException("card not valid")
        else:
            if json_to_card(card) not in player.cards:
                print(f"{json_to_card(card)=}")
                raise CardInvalidException("card not found in hand")
                abort(422, description="card not in hand")
            if player.cards[card_n]!=json_to_card(card):
                print("card not at specified location in hand")
                raise CardInvalidException("card not valid")
        #only reach this point if card is in player hand
        discard=card_to_json(self.discard[-1])
        print(f"{discard=} {self.discard[-1]=}")
        next_player=self.next_player
        next_username=next_player.username if type(next_player)==Player else next_player
        if player.username!=next_username:
            print(f"{player.username=} {next_username=}")
            if card==discard and "anyone_can_play_with_identical_cards" in self.rules:
                return True
            else: 
                raise CardInvalidException("not your turn")
        #only reach this point if correct player has played a card
        if str(card["value"]) == str(discard["value"]):
            return True
        if card["value"] == "wild":
            return True
        if card["value"] == "draw4":
            return True
        if card["colour"] == discard["colour"]:
            return True
        print(f" {card=} and {self.discard[-1]=}; {self.next_player=}, {player.__repr__()=} (Game.player_played_a_card)")
        raise CardInvalidException("card not valid")



def make_game(username:str, rules:str|None) -> Game:
    return Game(username=username, create=True, rules=rules)

def get_player_by_property(attribute:Literal["username", "id"], value:str) -> Player:
    conn=get_db()
    player = conn.execute(f"SELECT username, game_id, id FROM hands WHERE {attribute}='{value}'").fetchone()
    if not player:
        abort(404)
    player_obj=Player(player[0], game_id=player[1], row_id=player[2])
    return player_obj
