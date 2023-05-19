const blocks = document.querySelectorAll("#board td");
const message = document.getElementById("message");
const playerDirection = document.getElementById("player1ISstarting");
const player1Score = document.getElementById("player1Score");
const player2Score = document.getElementById("player2Score");
const switcher = document.getElementById("switchClicker");
var player1ISstarting = true;
var board =
[undefined, undefined, undefined,
undefined, undefined, undefined,
 undefined, undefined, undefined];
var turn = 0;
var i;
var switching_var = true;

if (localStorage.getItem("player1Score") === null) localStorage.setItem("player1Score", 0);
else player1Score.innerHTML = localStorage.getItem("player1Score");
if (localStorage.getItem("player2Score") === null) localStorage.setItem("player2Score", 0);
else player2Score.innerHTML = localStorage.getItem("player2Score");

// toggles between toggling between player start
function switching() {
  if (switching_var){
    switcher.innerHTML = "switch: false";
    player1ISstarting = true;
  }
  else switcher.innerHTML = "switch: true";
  switching_var = !switching_var;
}

// start listening to clicks
for (i = 0; i < 9; i++) addL(i);

function addL(index){
  blocks[index].addEventListener('click', function() {
    click(index);
  })
}

function reset() {
  board =
  [undefined, undefined, undefined,
  undefined, undefined, undefined,
   undefined, undefined, undefined];
  turn = 0
  for (i = 0; i < 9; i++) {
   blocks[i].classList.remove("selected");
   blocks[i].innerHTML = "";
  }

  if(switching_var) player1ISstarting = !player1ISstarting;
  message.innerHTML = player1ISstarting ? "player1's turn!": "player2's turn!";
}

// register clicks
function click(index) {
  if(board[index] === undefined && turn < 9) {
    board[index] = (turn % 2 == 0) ? true : false;
    blocks[index].innerHTML = ((!player1ISstarting + turn++) % 2 == 0) ? "X" : "O";
    message.innerHTML = ((!player1ISstarting + turn) % 2 == 0) ? "player1's turn!" : "player2's turn!";
    blocks[index].classList.add("selected");
    switch (checkWinner()) {
      case true:
        winnerType(true);
        break;
      case false:
        winnerType(false);
        break;
      case undefined:
        message.innerHTML = "its a tie!";
    }
  }
  else if(turn >= 9){
    reset();
  }
}

function resetScore() {
  player1Score.innerHTML = "0";
  player2Score.innerHTML = "0";
  localStorage.setItem("player2Score", 0);
  localStorage.setItem("player1Score", 0);
}

// checks who won and gives them score
function winnerType(bool){
  for (i = 0; i < 9; i++) blocks[i].classList.add("selected");
  turn = 9;
  if((bool && player1ISstarting) || (!bool && !player1ISstarting)) {
    message.innerHTML = "player1 has won!";
    localStorage.setItem("player1Score", parseInt(player1Score.innerHTML) + 1);
    player1Score.innerHTML = parseInt(player1Score.innerHTML) + 1;
  }
  else {
    message.innerHTML = "player2 has won!";
    localStorage.setItem("player2Score", parseInt(player2Score.innerHTML) + 1);
    player2Score.innerHTML = parseInt(player2Score.innerHTML) + 1;
  }
}

// check all the possible winning layouts
function checkWinner() {
  for(i = 0; i < 3; i++){
    if (checkList.apply(null, board.slice(3*i, 3*i+3)) != null)
      return board[3*i];
    if (checkList(board[i], board[i + 3], board[i + 6]) != null)
      return board[i];
  }
  if (checkList(board[0], board[4], board[8]) != null)
    return board[0];
  if (checkList(board[2], board[4], board[6]) != null)
    return board[2];
  if (turn == 9) return undefined;
  return null;
}

function checkList(obj1, obj2, obj3) {
  if (obj1 === obj2 && obj2 === obj3) return obj1;
  return null;
}
