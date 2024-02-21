#socketio
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
def authenticate_only(f): # wrapper
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
def transmit(game, action, user, other_details={}):
    if action in ["player_joined","player_said_uno", "player_left", "player_won", "player_drew_a_card", "player_reversed_direction", "players_turn", "you_won"]:
        data = {"player": user}
    elif action=="player_played_a_card":
        data={"player": user, "card": other_details["card"], "card_n":other_details["card_n"], "cards_left":  other_details["cards_left"]}
    elif action=="you_drew_a_card":
        data={"player": user, "card": other_details["card"]}
    elif action=="uno_challenge":
        data={"from": other_details["from"], "to": other_details["to"], "timestamp": other_details["timestamp"]}
    elif action=="setting_updated":
        data=other_details["json"]
    elif action=="message_in_chat"
        data={"player":user, "message": other_details["message"]}
    data["action"]=action
    socketio.emit('update_game_state', data, namespace=f'/uno/{game}/updates')
@socketio.on("json")
def recieved(json):
    game=json["game"]
    action=json["action"]