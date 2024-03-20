blank={colour:"none", value:"back"}

function load_card({colour, value}) {
    const card = document.createElement("div");
    card.className = "card";
    const img = document.createElement("img");
    img.addEventListener("click", clicked_card);
    img.src = `/uno/images/${colour}/${value}.svg`;
    img.setAttribute("data-value", value);
    img.setAttribute("data-colour", colour);
    card.appendChild(img);
    return card;
}
function get_game_id(){
    console.log(new URL(window.location).pathname.split("/"))
    console.log(new URL(window.location).pathname.split("/")[-1])
    return new URL(window.location).pathname.split("/")[3]
}

function clicked_card(e){
    console.log(e)
    let cardElem= e.target
    if (cardElem.parentNode.parentNode.getAttribute("data-you")=="true"){
        console.log("valid")
        console.log(e.target)
        const value = cardElem.getAttribute("data-value");
        const colour = cardElem.getAttribute("data-colour");
        const url = new URL(window.location).pathname + "/updates"
        const hand_list=Array.from(cardElem.parentNode.children)
        console.log(colour, value)
        console.log(hand_list)
        for (const i in hand_list){
            if (hand_list[i]===cardElem){var position=i}
        }
        console.log("position=", position)
        fetch(url, {method: "POST", body: JSON.stringify({"action": "player_played_a_card", "card":{"value":value, "colour": colour}, "card_n": position}), headers: {'Content-Type': 'application/json'}})
    }
}

function add_event_listener_to_cards(){
    console.log("adding event listener to cards")
    for (const i in document.getElementsByClassName("card")){
        document.getElementsByClassName("card")[i].addEventListener("click", clicked_card)}
} 

function player_played_card(data){
    console.log(data)
    var username = data["player"]
    var card = data["card"]
    var card_n = data["card_n"]
    var cards_left=data["cards_left"]
    console.log(username, card, card_n, cards_left)
    const div=document.getElementById(username)
    console.log(div)
    var hand=div.children[1]
    console.log(div, hand)
    card=hand.children[card_n]
    console.log(card)
    console.log("card played")
    hand.removeChild(card)
}	
function load_player(player){
    const elem = document.createElement("div");
    elem.setAttribute("data-you", player["you"])
    elem.className="player";
    elem.id=player["username"]
    const name=document.createElement("div")
    name.innerHTML=String(player.position)+") "+player["username"]
    name.className="player-name"
    elem.append(name)
    const cards=document.createElement("div")
    elem.append(cards)
    cards.id="player-hand"
    hand=[]
    if (!("hand" in player)){
        for(i=0; i<player["number_of_cards"]; i++){hand.push(blank)} 
    } else {
        for(i=0; i<player["number_of_cards"]*2; i=i+2){
            console.log(player["hand"], i, player["hand"][i], player["hand"][i+1])
            colour={r:"red", y:"yellow", g:"green", b:"blue", u:"none"}[player["hand"][i]]
            value={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:0,r:"reverse",d:"draw2", s:"skip"}[player["hand"][i+1]]
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


function render_game_state(draw_cards, discard){
    console.log(discard)
    const env = document.getElementById("gameState")
    env.appendChild(load_card(discard))
    env.appendChild(load_card(blank))
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

socket.on('update_game_state', function(data) {
    switch(data.action) {
        case "player_played_a_card:
            console.log("recieved!!")
            player_played_card(data);
            break;
        case "players_turn":
            console.log(data.player, "'s turn");
            break;
        case "other:
            console.log("misc", data)
            break;
        default:
            console.log("misc", data)
            break;
    }
});

window.onload = async function(){
    add_event_listener_to_cards()
    let response = await fetch((new URL(window.location)).pathname+"/personalised.json")
    var info = await response.json()
    console.log(info)
    var players=info["players"]
    console.log(players)
    const opponents=document.getElementById("opponents")
    for (var key in players){
        players[key]["username"]=key
        console.log(key, players[key])
        if (!players[key]["you"]){
            opponents.appendChild(load_player(players[key]))
        } else {
            document.getElementById("myHand").appendChild(load_player(players[key]))
        }
    }
    render_game_state(info.draw_length, info.discard)
}
