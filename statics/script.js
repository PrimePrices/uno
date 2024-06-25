blank={colour:"none", value:"back"}
function load_card({colour, value}) {

    const img = document.createElement("img");
    img.className = "card";
    img.addEventListener("click", clicked_card);
    img.src = `/uno/images/${colour}/${value}.svg`;
    img.setAttribute("data-value", value);
    img.setAttribute("data-colour", colour);
    return img;
}
function get_game_id(){
    return new URL(window.location).pathname.split("/")[3]
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
        socket.emit("update", {"game_name": get_game_id(), 
                                "info":{"action": "player_played_a_card", "card":{"value":value, "colour": colour}, "card_n": position}})

    } else if (cardElem.parentNode.id="draw"){
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
    var card = data["card"]
    var card_n = data["card_n"]
    var cards_left=data["cards_left"]
    const div=get_player(username)
    var hand=div.children[1]
    card=hand.children[card_n]
    console.log("card played")
    hand.removeChild(card)
    const discard = document.getElementById("discard")
    card.classList.remove("clickable")
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
    elem.id=player_data["username"]
    const name=document.createElement("div")
    name.innerHTML=String(player_data.position)+") "+player_data["username"]
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
    let player;
    switch(data.action) {
        case "player_played_a_card":
            //username, card, card_n, cards_left
            console.log("recieved!!", data)
            player_played_card(data);
            break;
        case "players_turn":
            //player
            console.log(data.player, "'s turn");
            break;
        case "player_joined":
            //username position number_of_cards draw_length
            player=load_player()
            break;
        case "player_left":
            //username
            break;
        case "player_won":
            //username
            break;
        case "player_drew_a_card":
            console.log(data)
            if (data.player!==get_my_name()){ //need to now get my username
                player = get_player(data.player)    
                player.children[2].append(load_card({colour:"none", value:"back"}))
                console.log(get_player(data.player))
            } else {
                console.log("admin drew a card")
            }
            //username draw_length
            break;
        case "your_turn":
            //none
            break;
        case "you_drew_a_card":
            console.log(data)
            player = document.getElementById("myHand").children[0]
            console.log(player, player.children[1])
            player.children[1].appendChild(load_card(data["card"]))
            //username, card, draw_length
            break;
        case "you_won":
            //username
            break;
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
