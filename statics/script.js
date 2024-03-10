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
    return new URL(window.location).pathname
}

function clicked_card(e){
    console.log(e)
    let cardElem= e.target
    if (cardElem.parentNode.parentNode.parentNode.getAttribute("data-you")=="true"){
        console.log("valid")
        console.log(e.target)
        const value = cardElem.getAttribute("data-value");
        const colour = cardElem.getAttribute("data-colour");
        socket.emit({"action": "player_played_a_card", "card": {"value": value, "colour": colour}, "game": get_game_id()});
    }
}

const channel = new URL(window.location).pathname
socket = io.connect(channel);
console.log("connected")
console.log(socket)
socket.on('update_game_state', function(data) {
    if (data.action=="player_played_a_card"){
        player_played_card(data);
    }else if (data.action=="players_turn"){
        console.log(data.player, "'s turn");
    }
        //document.getElementById('gameState').innerText = data.game_state;
});
function player_played_card(data){
    var username = data["username"]
    var card = data["card"]
    var card_n = data["card_n"]
    var cards_left=data["cards_left"]
    const div=document.getElementById(username)
    var hand=div.childNodes()[1]
}	
function load_player(player){
    console.log("player:", player)
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
    if (!("hand" in player)){for(i=0; i<player["number_of_cards"]; i++){hand.push(blank)} 
    } else {
        for(i=0; i<player["number_of_cards"]*2; i=i+2){
            console.log(player["hand"], i)
            colour={r:"red", y:"yellow", g:"green", b:"blue", u:"none"}[player["hand"][i]]
            value={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:0,r:"reverse",d:"draw2", s:"skip"}[player["hand"][i+1]]
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


window.onload = async function(){
    let response = await fetch((new URL(window.location)).pathname+"/personalised.json")
    var info = await response.json()
    console.log(info)
    var players=info["players"]
    console.log(players)
    const opponents=document.getElementById("opponents")
    for (const i in players){
        if (!players[i]["you"]){
            opponents.appendChild(load_player(players[i]))
        }
    }
    render_game_state(info.draw_length, info.discard)
    document.getElementById("myHand").appendChild(load_player(info["you"]))
}