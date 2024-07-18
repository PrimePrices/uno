#socketio
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user, login_required
from flask import abort, request
from .transmit import transmit
from .game import *
def flash(message):
    emit("flash", {"message": message}, namespace="/", to=request.sid)#type: ignore

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
            print(data, "(socketinge.py line25)")
            game.player_played_card(current_user.username, data["card"], data["card_n"])
        elif data["action"] == "player_drew_a_card":
            game=Game(game_name)
            card=game.draw_card()
            game.increment_players()
            player=Player(current_user.username, game_id=game.id)
            player.drew_a_card(card[0])
            transmit(str(game_name), 
                     data["action"], 
                     current_user.username, 
                     {"draw_length": len(game.draw)}, 
                     exclue_request_sid=True, 
                     request_sid=request.sid, #type: ignore
                     private_message={"action": "you_drew_a_card", "card": card_to_json(card[0]), "draw_length": len(game.draw)})
        elif data["action"] == "uno_challenge":
            print(f'{data["from"]} uno challenges {data["to"]} at {data["timestamp"]}')
        else: print(data)
        return {"a": True}
    print("registering socketio routes")
    @socketio.on("connect")
    def connect():
        print("user connected", current_user.username, request.sid)# type: ignore
        if not current_user.is_authenticated:
            return disconnect()
        conn=get_db()
        conn.execute(f"UPDATE hands SET request_sid='{request.sid}' WHERE username='{current_user.username}'")# type: ignore
        conn.commit()
        conn.close()
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

    @socketio.on_error_default
    def DefaultErrorHandler(error):
        print(error)
        if str(error)=="card invalid":
            print("Card invalid error raised (socketio)")
            flash("Card invalid")
        elif str(error)=="colour not provided":
            print("Colour not provided error raised (socketio)")
            print(error)
            flash("Please provide colour")

