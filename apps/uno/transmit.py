from flask import abort
from flask_socketio import emit
def transmit(game:int, action:str, user:str, other_details: dict={}, exclue_request_sid=False, request_sid= None, private_message=None):
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
        print(action)
        abort(500)
    data["action"]=action
    print(f"emmiting {data=} to {game=} on /uno/{game}/updates")
    if exclue_request_sid:
        emit('update_game_state', data, namespace="/", to=str(game), skip_sid=request_sid)
        print(f"emmiting privately {private_message=} to {request_sid=} on /uno/{game}/updates")
        emit("update_game_state", private_message, namespace="/", to=request_sid)
    else:
        emit('update_game_state', data, namespace="/", to=str(game))