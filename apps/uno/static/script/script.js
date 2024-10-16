blank={colour:"none", value:"back"}
function load_card({colour, value}, position=null) {
    const img = document.createElement("img");
    img.className = "card";
    img.addEventListener("click", clicked_card);
    img.src = `/uno/static/image/${colour}/${value}.svg`;
    img.setAttribute("data-value", value);
    img.setAttribute("data-colour", colour);
    if (position != null) {
        img.setAttribute("data-position", position);
        img.setAttribute("style", `--position:${position}`);
    }
    return img;
}
function get_game_id(){
    return new URL(window.location).pathname.split("/")[3]
}
function remove_popup(){
    const popup=document.getElementById("popup")
    popup.style.display="none"
    const cancel=document.getElementById("popup-cancel")
    const red=document.getElementById("popup-red")
    const yellow=document.getElementById("popup-yellow")
    const green=document.getElementById("popup-green")
    const blue=document.getElementById("popup-blue")
    cancel.removeEventListener("click", remove_popup)
    const new_red = red.cloneNode()
    const new_yellow = yellow.cloneNode()
    const new_green = green.cloneNode()
    const new_blue = blue.cloneNode()
    red.parentNode.replaceChild(new_red, red)
    yellow.parentNode.replaceChild(new_yellow, yellow)
    green.parentNode.replaceChild(new_green, green)
    blue.parentNode.replaceChild(new_blue, blue)
    red.remove()
    yellow.remove()
    green.remove()
    blue.remove()
}
function get_colour_choice(card, position){
    console.log(card)
    const popup=document.getElementById("popup")
    popup.style.display="block"
    const cancel=document.getElementById("popup-cancel")
    const red = document.getElementById("popup-red")
    const yellow = document.getElementById("popup-yellow")
    const green = document.getElementById("popup-green")
    const blue = document.getElementById("popup-blue")
    cancel.addEventListener("click", remove_popup)
    const value= card.getAttribute("data-value")
    console.log(value)
    red.addEventListener("click", function(){
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": "red"}, "card_n": position}})
        remove_popup()
    })
    yellow.addEventListener("click", function(){
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": "yellow"}, "card_n": position}})
        remove_popup()
    })
    green.addEventListener("click", function(){
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": "green"}, "card_n": position}})
        remove_popup()
    })
    blue.addEventListener("click", function(){
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": "blue"}, "card_n": position}})
        remove_popup()
    })

}
function clicked_card(e){
    console.log(e)
    let cardElem= e.target
    const url = new URL(window.location).pathname + "/updates"
    if (cardElem.parentNode.parentNode.getAttribute("data-you")=="true"){
        console.log("valid")
        console.log(e.target)
        const value = cardElem.getAttribute("data-value");
        const colour = cardElem.getAttribute("data-colour");

        const hand_list=Array.from(cardElem.parentNode.children)
        console.log(colour, value)
        console.log(hand_list)
        for (const i in hand_list){
            if (hand_list[i]===cardElem){var position=i}
        }
        console.log("position=", position)
        if (cardElem.classList.contains("blank")){
            get_colour_choice(cardElem, position) // get colour 
        } else {        
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": colour}, "card_n": position}})
        }
    } else if (cardElem.parentNode.id=="draw"){
        socket.emit("update", {"game_name": get_game_id(), "info":{"action": "player_drew_a_card"}})
    } else {console.log("somethings gone wrong")}
};
function add_event_listener_to_cards(){
    console.log("adding event listener to cards")
    for (const i in document.getElementsByClassName("card")){
        document.getElementsByClassName("card")[i].addEventListener("click", clicked_card)
    }
} 

function player_played_card(data){
    console.log(data)
    var username = data["player"]
    var card_data = data["card"]
    var card_n = data["card_n"]
    var cards_left=data["cards_left"]
    const div=get_player(username)
    var hand=div.children[1]
    card=hand.children[card_n]
    console.log("card played")
    hand.removeChild(card)
    const discard = document.getElementById("discard")
    card=load_card(card_data)
    while (!(discard.firstChild in [" "])) {
        console.log(discard, discard.firstChild)
        if (discard.firstChild!=null){
            discard.removeChild(discard.firstChild);
        } else {break}
        
    }
    console.log(discard)
    discard.appendChild(card)

}	
function load_player(player_data){
    const elem = document.createElement("div");
    elem.setAttribute("data-you", player_data["you"])
    elem.className="player";
    elem.setAttribute("id", player_data["username"])
    elem.setAttribute("name",player_data["username"])
    elem.focus=false
    elem.number_of_cards=player_data["number_of_cards"]
    const name=document.createElement("div")
    name.setAttribute("id", "player-name")
    if (player_data["position"]==undefined){
        name.innerHTML=player_data["username"]
    } else {
        name.innerHTML=String(player_data.position)+") "+player_data["username"]
    }
    name.className="player-name"
    elem.append(name)
    const cards=document.createElement("div")
    elem.append(cards)
    cards.id="player-hand"
    hand=[]
    if (!("hand" in player_data)){
        for(i=0; i<player_data["number_of_cards"]; i++){hand.push(blank)} 
    } else {
        for(i=0; i<player_data["number_of_cards"]*2; i=i+2){
            console.log(player_data["hand"], i, player_data["hand"][i], player_data["hand"][i+1])
            colour={r:"red", y:"yellow", g:"green", b:"blue", u:"none"}[player_data["hand"][i]]
            value={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:0,r:"reverse",d:"draw2", s:"skip"}[player_data["hand"][i+1]]
            console.log({colour: colour, value:value})
            hand.push({colour:colour, value:value})
        }
    }
    for (const j in hand){
        const card=load_card(hand[j]);
        distance=-Math.abs(hand.length/2-j)*5-5  
        if (j!=0){
            card.style.marginLeft=distance.toString()+"px";
        }
        if (j!=hand.length-1){
            card.style.marginRight=distance.toString()+"px";
        }
        cards.append(card);
    }
    return elem
}


function display_art(){
    colors=["red", "yellow", "green", "blue"]
    values=[0,1,2,3,4,5,6,7,8,9,0,"reverse","draw2","skip"]
    for (i in colors){
        const elem = document.createElement("div");
        elem.id="player-hand";
        for (j in values){
            elem.appendChild(create_card({color:colors[i], value:values[j]}))
        } 
        document.body.appendChild(elem)
    }
}
function get_player(username){
    return document.getElementsByName(username)[0]
}
function get_my_name(){
    return document.getElementById("myHand").firstChild.name
}

const channel = new URL(window.location).hostname
//const channel = new URL(window.location).hostname+"/uno"
const socket = io.connect(channel+":5000" );
socket.port=window.port
socket.connect()
console.log(socket)
const room=get_game_id()
console.log(room)
socket.emit("join", {room: get_game_id()})
socket.on("connect", function(){
    console.log("connected")
    console.log(socket, channel)
})
socket.on("disconnect", function(){
    console.log("disconnected")
})
socket.on("flash", function(data){
    console.log(data)
    alert(data.message)
})
socket.on('update_game_state', function(data) {
    switch(data.action) {
        case "player_played_a_card":
            //username, card, card_n, cards_left
            console.log("recieved!!", data)
            player=data.player
            player_played_card(data);
            break;
        case "players_turn":
            var players=document.getElementsByClassName("player")
            for (const player_i in players){
                if (players[player_i].classList!=undefined){
                    if (players[player_i].classList.contains("player-turn")){
                        players[player_i].classList.remove("player-turn")
                    }
                }
            }
            var player = get_player(data.player)
            player.classList.add("player-turn")
            console.log(player, player.classList)

            break;
        case "player_joined":
            //username position number_of_cards draw_length
            var new_data={"you":false, 
                "username":data.player, 
                "position":data.position, 
                "number_of_cards":7}
            if (get_player(data.player) == undefined) {
                player=load_player(new_data)
                var opponents=document.getElementById("opponents")
                opponents.append(player)
            }
            
            break;
        case "player_left":
            player = get_player(data.player)
            player.remove()
        case "player_won":
            //username
            break;
        case "player_drew_a_card":
            console.log(data)
            if (data.player!==get_my_name()){ //need to now get my username
                player = get_player(data.player)
                var card=load_card({colour:"none", value:"back"})
                player.children[1].append(card)
                console.log(get_player(data.player))
            } else {
                console.log("You drew a card")
            }
            //username draw_length
            break;

        case "you_drew_a_card":
            console.log(data)
            var player = document.getElementById("myHand").children[0]
            console.log(player, player.children[1])
            var number_of_cards=player.children[1].children.length
            var card=load_card(data["card"], position = number_of_cards)
            card.classList.add("clickable")
            if (data["card"].colour=="none"){
                card.classList.add("blank")
            }
            player.children[1].appendChild(card)
            //username, card, draw_length
            break;
        case "you_won":
            console.log(document.getElementById("popupYouWon"))
        case "uno_challenge":
            //from, to, timestamp
            break;
        case "player_said_uno":
            //username, timestamp, number_of_cards_left
            break;
        case "setting_updated":
            //new_settings
            break;
        case "message_in_chat":                          //maybe won't include this
            alert(data.username, "says", data.message)
            //username, message
            break;
        default:
            console.log("unrecognised message:", data)
            break;
    }
});

window.onload = async function(){
    add_event_listener_to_cards()
}
