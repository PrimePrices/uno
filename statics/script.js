blank={colour:"none", value:"back"}

function load_card(json){
    const card=document.createElement("div");
    card.className="card";
    const img=document.createElement("object");
    img.data="/uno/images/"+json.colour+"/" + json.value+".svg";
    img.type="image/svg+xml";
    card.appendChild(img);
    return card
}
function player_played_card(data){
    var username = data["username"]
    var card = data["card"]
    var card_n = data["card_n"]
    var cards_left=data["cards_left"]
    const div=document.getElementById(username)
    var hand=div.childNodes()[1]
	var card_elem=hand.childNodes()[card_n]
}
function start_conn(){
    const channel=new URL(window.location).pathname+"/updates"
    var socket = io.connect(channel);
    socket.on('update_game_state', function(data) {
        if (data.action=="player_played_a_card"){
            player_played_card(data)}
        //document.getElementById('gameState').innerText = data.game_state;
    });
}
function load_player(player){
    console.log("player:", player )
    const elem = document.createElement("div");
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
            console.log(player["hand"][i], colour)
            value={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:0,r:"reverse",d:"draw2", s:"skip"}[player["hand"][i+1]]
            hand.push({colour:colour, value:value})
            console.log(hand)
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
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
//This loads each players hand
window.onload = async function(){
    let cookie= String(getCookie("username"))
    var response=await fetch(new URL(window.location).pathname+"/"+cookie+".json")
    var info = await response.json()
    console.log(info)
    var players=info["players"]
    console.log(players)
    const opponents=document.getElementById("opponents")
    for (const i in players){
        opponents.appendChild(load_player(players[i]))
    }
    render_game_state(info.draw_length, info.discard)
    load_player()
    start_conn()
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