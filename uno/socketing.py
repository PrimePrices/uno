#socketio
from flask_socketio import emit, join_room, leave_room, disconnect, Namespace
from flask_login import current_user



def authenticate_only(f): # wrapper
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
def register_routes(socketio):
    def transmit(self, game, action, user, other_details={}):
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
        elif action=="message_in_chat":
            data={"player":user, "message": other_details["message"]}
        data["action"]=action
        emit('update_game_state', data, namespace=f'/uno/{game}/updates')
    @socketio.on("message")
    def message(json: dict) -> None:
        print(f"recieved {json=}")
    
    @socketio.on("event")
    def event(json: dict) -> None:
        game: str = json["game"] 
        action: str = json["action"]
        user: str = current_user.username
        other_details: dict = json["other_details"]
        print(f"recieved {json=}")
        transmit(game, action, user, other_details)
    print("routes registered for socketio")
