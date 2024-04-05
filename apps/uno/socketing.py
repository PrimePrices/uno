#socketio
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user, login_required
from flask import abort, request
from .game import *


def authenticate_only(f): # wrapper
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
def register_routes(socketio):
    @socketio.on("update")
    @login_required
    def updates(data):
        game_name=data["game_name"]
        data=data["info"]
        if data["action"] == "player_played_a_card":
            game=Game(game_name)
            cards_left=game.player_played_card(current_user.username, data["card"], data["card_n"])
            transmit(str(game_name), data["action"], current_user.username, {"card": data["card"], "card_n": data["card_n"], "cards_left": cards_left})
        elif data["action"] == "player_drew_a_card":
            game=Game(game_name)
            card=game.draw_card()
            player=Player(current_user.username, game_id=game.id)
            player.cards.append(card[0])
            transmit(str(game_name), 
                     data["action"], 
                     current_user.username, 
                     {"draw_length": len(game.draw)}, 
                     exclue_request_sid=True, 
                     request_sid=request.sid, 
                     private_message={"action": "you_drew_a_card", "card": card_to_json(card[0]), "draw_length": len(game.draw)})
        elif data["action"] == "uno_challenge":
            print(f'{data["from"]} uno challenges {data["to"]} at {data["timestamp"]}')
        else: print(data)
        return {"a": True}
    print("registering socketio routes")
    @socketio.on("connect")
    def connect():
        print("user connected")
        return True
    @socketio.on("join")
    def handle_join_room(data):
        print("user joined room " + data["room"]) 
        join_room(data["room"])
    @socketio.on("leave")
    def handle_leave_room(data):
        print("user left room " + data["room"])
        leave_room(data["room"])
    @socketio.on("message")
    def message(json: dict) -> None:
        print(f"recieved {json=}")
    print("routes registered for socketio")
def transmit(game, action, user, other_details={}, exclue_request_sid=False, request_sid= None, private_message=None):
    if action in ["player_joined","player_said_uno", "player_left", "player_won", "player_drew_a_card", "player_reversed_direction", "players_turn", "you_won"]:
        data = {"player": user}
    elif action=="player_drew_a_card":
        data={"player": user, "draw_length": other_details["draw_length"]}
    elif action=="player_played_a_card":
        data={"player": user, "card": other_details["card"], "card_n":other_details["card_n"], "cards_left":  other_details["cards_left"]}
    elif action=="you_drew_a_card":
        data={"player": user, "card": other_details["card"]}
    elif action=="uno_challenge":
        data={"from": other_details["from"], "to": other_details["to"], "timestamp": other_details["timestamp"]}
    elif action=="setting_updated":
        data=other_details["json"]
    elif action=="message_in_chat":
        data={"player":user, "message": other_details["message"]}
    else:
        abort(414)
    data["action"]=action
    print(f"emmiting {data=} to {game=} on /uno/{game}/updates")
    if exclue_request_sid:
        emit('update_game_state', data, namespace="/", to=game, skip_sid=request_sid)
        print(f"emmiting privately {private_message=} to {request_sid=} on /uno/{game}/updates")
        emit("update_game_state", private_message, namespace="/", to=request_sid)
    else:
        emit('update_game_state', data, namespace="/", to=game)