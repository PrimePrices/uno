function startGame(){
    const current=new URL(window.location.href)
    root=current.origin
    console.log(current)
    rules=["w", "t", "rt5"]
    stri=rules.toString()
    //var i=document.getElementById("player-count").value
    console.log(stri)
    r=stri.replaceAll(",", "_")
    window.location.href=root+"/uno/newgame"+"/w_t_rt5"
}
// Event listener for the Start Game button click
console.log("JP was here")
const button=document.getElementsByTagName("button")