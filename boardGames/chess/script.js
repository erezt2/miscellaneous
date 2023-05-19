const temp_board = document.querySelectorAll("#board tr");
const title = document.getElementById("title");
const html_turn_list = document.getElementById("movement_list");
const html_board = [[], [], [], [], [], [], [], []];
const js_board = [
["black-rook", "black-knight", "black-bishop", "black-queen", "black-king", "black-bishop", "black-knight", "black-rook"],
["black-pawn", "black-pawn", "black-pawn", "black-pawn", "black-pawn", "black-pawn", "black-pawn", "black-pawn"],
["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
["empty", "empty", "empty", "empty", "empty", "empty", "empty", "empty"],
["white-pawn", "white-pawn", "white-pawn", "white-pawn", "white-pawn", "white-pawn", "white-pawn", "white-pawn"],
["white-rook", "white-knight", "white-bishop", "white-queen", "white-king", "white-bishop", "white-knight", "white-rook"]];
var turn_list = "";
const ntl = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H"};
const ltn = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7};

const movement_list = {
  "queen": [true, [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]],
  "king": [false, [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]],
  "bishop": [true, [1, 1], [-1, 1], [-1, -1], [1, -1]],
  "rook": [true, [1, 0], [0, 1], [-1, 0], [0, -1]],
  "knight": [false, [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1], [-1, -2], [1, -2]]
};
var seleted_piece_moves = [];
var piece_selected = false;
var selected_piece = [];
var targeting_piece = false;
var white_turn = true;

function is_white(piece_name) {
  if (piece_name[0] == "w") return true;
  if (piece_name[0] == "b") return false;
  return undefined;
}

function generalize(piece_name) {
  if (piece_name === "empty") return "empty";
  return piece_name.slice(piece_name.indexOf("-") + 1, piece_name.length);
}

for (let i = 0; i < 8; i++)
  for (let j = 0; j < 8; j++)
    html_board[i].push(temp_board[i + 1].children[j + 1]);

for (let i = 0; i < 8; i++)
  for (let j = 0; j < 8; j++) {
    if ((i + j) % 2 == 0) html_board[i][j].classList.add("white");
    addClicker(i, j);
  }

function addClicker(indexY, indexX) {
  html_board[indexY][indexX].addEventListener('click', function() {
    click(indexY, indexX);
  })
  html_board[indexY][indexX].addEventListener('mouseover', function() {
    hover(indexY, indexX);
  })
  html_board[indexY][indexX].addEventListener('mouseout', function() {
    unhover(indexY, indexX);
  })
}

if (localStorage.getItem("undo") !== null) undo(localStorage.getItem("undo"));

function reload() {
  if(confirm("restart?"))
    location.reload();
}

function undo(list=null) {
  if (list === null) {
    let i = turn_list.split("  ");
    let mapped_moves = i.splice(0, i.length - 2).map(value => {
      let i = value.split("->");
      return [[8-parseInt(i[0][1]), ltn[i[0][0]]], [8-parseInt(i[1][1]), ltn[i[1][0]]]];
    });
    localStorage.setItem("undo", JSON.stringify(mapped_moves));
    location.reload();
  }
  else {
    for (let i of JSON.parse(list)) {
      move(i[0], i[1]);
    }
    localStorage.removeItem("undo");
  }
}

function move(from, to) {
  if (js_board[from[0]][from[1]] == "white-king" && !turn_list.includes("E1")) {
    if (to[1] == 6) {
      html_board[7][7].classList.remove("white-rook");
      js_board[7][7] = "empty";
      html_board[7][5].classList.add("white-rook");
      js_board[7][5] = "white-rook";
    }
    if (to[1] == 2) {
      html_board[7][0].classList.remove("white-rook");
      js_board[7][0] = "empty";
      html_board[7][3].classList.add("white-rook");
      js_board[7][3] = "white-rook";
    }
  }
  else if (js_board[from[0]][from[1]] == "black-king" && !turn_list.includes("E8")) {
    if (to[1] == 6) {
      html_board[0][7].classList.remove("black-rook");
      js_board[0][7] = "empty";
      html_board[0][5].classList.add("black-rook");
      js_board[0][5] = "black-rook";
    }
    if (to[1] == 2) {
      html_board[0][0].classList.remove("black-rook");
      js_board[0][0] = "empty";
      html_board[0][3].classList.add("black-rook");
      js_board[0][3] = "black-rook";
    }
  }

  turn_list += (""+ntl[from[1]]+(8-from[0])+"->"+ntl[to[1]]+(8-to[0])+"  ");
  html_turn_list.innerHTML = turn_list;
  html_board[to[0]][to[1]].classList.remove(js_board[to[0]][to[1]]);
  js_board[to[0]][to[1]] = js_board[from[0]][from[1]];
  js_board[from[0]][from[1]] = "empty";
  html_board[from[0]][from[1]].classList.remove(js_board[to[0]][to[1]])
  html_board[to[0]][to[1]].classList.add(js_board[to[0]][to[1]]);

  if (to[0] == 0 && js_board[0][to[1]] == "white-pawn") {
    js_board[0][to[1]] = "white-queen";
    html_board[0][to[1]].classList.remove("white-pawn");
    html_board[0][to[1]].classList.add("white-queen");
  }
  else if (to[0] == 7 && js_board[7][to[1]] == "black-pawn") {
    js_board[7][to[1]] = "black-queen";
    html_board[7][to[1]].classList.remove("black-pawn");
    html_board[7][to[1]].classList.add("black-queen");
  }

  white_turn = !white_turn;
}

function click(indexY, indexX) {
  if (piece_selected) {
    if (indexY == selected_piece[0] && indexX == selected_piece[1]) {
      for(let i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.remove("option-block")
      html_board[indexY][indexX].classList.remove("selected");
      piece_selected = false;
      selected_piece = [];
      seleted_piece_moves = [];
    }
    else if (is_white(js_board[indexY][indexX]) === white_turn && whereCanIMove(indexY, indexX).length != 0) {
      for(let i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.remove("option-block");
      html_board[selected_piece[0]][selected_piece[1]].classList.remove("selected");
      html_board[indexY][indexX].classList.add("selected");
      selected_piece = [indexY, indexX];
      seleted_piece_moves = whereCanIMove(indexY, indexX);
      for(let i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.add("option-block");
    }
    else {
      let moveable_location = false;
      for (let i of seleted_piece_moves)
        if (i[0] == indexY && i[1] == indexX) {
          moveable_location = true;
          break;
        }

      if (moveable_location) {
        move(selected_piece, [indexY, indexX])

        if (can_move(white_turn)) {
          if (is_check(white_turn))
            title.innerHTML = "chess - check";
          else
            title.innerHTML = "chess";
        }
        else {
          if (is_check(white_turn))
            title.innerHTML = "chess - " + (white_turn ? "black wins!" : "white wins!");
          else
            title.innerHTML = "chess - stalemate";
        }

      }

      for(let i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.remove("option-block");
      html_board[selected_piece[0]][selected_piece[1]].classList.remove("selected");
      html_board[selected_piece[0]][selected_piece[1]].classList.remove("pointer");
      html_board[indexY][indexX].classList.remove("option-block-selected");
      piece_selected = false;
      selected_piece = [];
      seleted_piece_moves = [];
    }
  }
  else if (is_white(js_board[indexY][indexX]) === white_turn && whereCanIMove(indexY, indexX).length != 0) {
    selected_piece = [indexY, indexX];
    piece_selected = true;
    html_board[indexY][indexX].classList.add("selected");
    seleted_piece_moves = whereCanIMove(indexY, indexX);
    for(let i of seleted_piece_moves)
      html_board[i[0]][i[1]].classList.add("option-block")
  }
}

function hover(indexY, indexX) {
  if (is_white(js_board[indexY][indexX]) === white_turn && whereCanIMove(indexY, indexX).length != 0)
    html_board[indexY][indexX].classList.add("pointer");
    for(let i of seleted_piece_moves)
      if (i[0] == indexY && i[1] == indexX)
        html_board[indexY][indexX].classList.add("option-block-selected");
}

function unhover(indexY, indexX) {
  html_board[indexY][indexX].classList.remove("pointer");
  html_board[indexY][indexX].classList.remove("option-block-selected");
}

function is_check(white) {
  let temp_pieces = white ? "white-king" : "black-king";
  let king_pos;
  for (let i = 0; i < 8; i++)
    for (let j = 0; j < 8; j++)
      if(js_board[i][j] == temp_pieces) {
        king_pos = [i, j];
        break;
      }

  let c;
  temp_pieces = white ?  ["black-queen", "black-rook"] : ["white-queen", "white-rook"];
  for (let i of [[1,0],[0,1],[-1,0],[0,-1]]) {
    c = 1;
    while (king_pos[0] + c * i[0] >= 0 && king_pos[0] + c * i[0] <= 7 && king_pos[1] + c * i[1] >= 0 && king_pos[1] + c * i[1] <= 7) {
      if (is_white(js_board[king_pos[0] + c * i[0]][king_pos[1] + c * i[1]]) !== undefined) {
        if (temp_pieces.includes(js_board[king_pos[0] + c * i[0]][king_pos[1] + c * i[1]])) return true;
        break;
      }
      c += 1;
    }
  }
  temp_pieces = white ? ["black-queen", "black-bishop"] : ["white-queen", "white-bishop"];
  for (let i of [[1,1],[-1,1],[-1,-1],[1,-1]]) {
    c = 1;
    while (king_pos[0] + c * i[0] >= 0 && king_pos[0] + c * i[0] <= 7 && king_pos[1] + c * i[1] >= 0 && king_pos[1] + c * i[1] <= 7) {
      if (is_white(js_board[king_pos[0] + c * i[0]][king_pos[1] + c * i[1]]) !== undefined) {
        if (temp_pieces.includes(js_board[king_pos[0] + c * i[0]][king_pos[1] + c * i[1]])) return true;
        break;
      }
      c += 1;
    }
  }
  temp_pieces = white ? "black-knight" : "white-knight";
  for (let i of [[2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1], [-1, -2], [1, -2]]) {
    if (king_pos[0] + i[0] < 0 || king_pos[0] + i[0] > 7 || king_pos[1] + i[1] < 0 || king_pos[1] + i[1] > 7) continue;
    if (js_board[king_pos[0] + i[0]][king_pos[1] + i[1]] == temp_pieces) return true;
  }

  temp_pieces = white ? "black-king" : "white-king";
  for (let i of [[1,1],[-1,1],[-1,-1],[1,-1],[1,0],[0,1],[-1,0],[0,-1]]) {
    if (king_pos[0] + i[0] < 0 || king_pos[0] + i[0] > 7 || king_pos[1] + i[1] < 0 || king_pos[1] + i[1] > 7) continue;
    if (js_board[king_pos[0] + i[0]][king_pos[1] + i[1]] == temp_pieces) return true;
  }

  temp_pieces = white ? ["black-pawn", -1] : ["white-pawn", 1];
  for (let i of [1, -1]) {
    if (king_pos[1] + i < 0 || king_pos[1] + i > 7 || king_pos[0] + temp_pieces[1] < 0 || king_pos[0] + temp_pieces[1] > 7) continue;
    if (js_board[king_pos[0] + temp_pieces[1]][king_pos[1] + i] == temp_pieces[0]) return true;
  }

  return false;
}

function check_decorator(white, from_to) {
  // bug: if from == to the piece will just disappear (no insteance in this code)
  let temp = js_board[from_to[1][0]][from_to[1][1]];
  js_board[from_to[1][0]][from_to[1][1]] = js_board[from_to[0][0]][from_to[0][1]];
  js_board[from_to[0][0]][from_to[0][1]] = "empty";
  let result = is_check(white);
  js_board[from_to[0][0]][from_to[0][1]] = js_board[from_to[1][0]][from_to[1][1]];
  js_board[from_to[1][0]][from_to[1][1]] = temp;
  return result;
}

function can_move(white) {
  for (let i = 0; i < 8; i++)
    for (let j = 0; j < 8; j++)
      if (is_white(js_board[i][j]) === white && whereCanIMove(i, j).length != 0) {
        return true;
      }
  return false;
}

function whereCanIMove(indexY, indexX) {
  let current_piece = js_board[indexY][indexX]
  let result = [];
  let temp = [];
  if (generalize(current_piece) === "pawn") {
    let sign = (white_turn ? -1 : 1);
    if (is_white(js_board[indexY + sign][indexX]) === undefined &&
        !check_decorator(white_turn, [[indexY, indexX], [indexY + sign, indexX]]))
      result.push([indexY + sign, indexX])
    if (indexY == (white_turn ? 6 : 1) && is_white(js_board[indexY + sign][indexX]) === undefined && is_white(js_board[indexY + 2 * sign][indexX]) === undefined &&
        !check_decorator(white_turn, [[indexY, indexX], [indexY + 2 * sign, indexX]]))
      result.push([indexY + 2 * sign, indexX])
    for (let i of [-1, 1]) {
      if (indexX + i < 0 || indexX + i > 7) continue;
      if (is_white(js_board[indexY + sign][indexX + i]) !== !white_turn) continue;
      if (check_decorator(white_turn, [[indexY, indexX], [indexY + sign, indexX + i]])) continue;
      result.push([indexY + sign, indexX + i])
    }
  }
  else {
    let is_once = movement_list[generalize(current_piece)][0];
    let c;
    for (let i of movement_list[generalize(current_piece)].slice(1)) {
      c = 0;
      do {
        c += 1;
        temp = [indexY + c * i[0], indexX + c * i[1]]
        if (temp[0] < 0 || temp[0] > 7 || temp[1] < 0 || temp[1] > 7) break;
        if (white_turn === is_white(js_board[temp[0]][temp[1]])) break;
        if (check_decorator(white_turn, [[indexY, indexX], [indexY + c * i[0], indexX + c * i[1]]])) continue;
        result.push(temp);
        if (!white_turn === is_white(js_board[temp[0]][temp[1]])) break;
      } while (is_once);
    }
  }
  // castling
  if (js_board[indexY][indexX] == "white-king" && !turn_list.includes("E1")) {
    // right
    if (!turn_list.includes("H1") && js_board[7][5] == "empty" && js_board[7][6] == "empty" &&
      !is_check(true) && !check_decorator(true, [[7,4],[7,5]]) && !check_decorator(true, [[7,4],[7,6]]))
        result.push([7,6]);
    if (!turn_list.includes("A1") && js_board[7][1] == "empty" && js_board[7][2] == "empty" && js_board[7][3] == "empty" &&
      !is_check(true) && !check_decorator(true, [[7,4],[7,1]]) && !check_decorator(true, [[7,4],[7,2]]) && !check_decorator(true, [[7,4],[7,3]]))
        result.push([7,2]);
  }
  else if (js_board[indexY][indexX] == "black-king" && !turn_list.includes("E8")) {
    // right
    if (!turn_list.includes("H8") && js_board[0][5] == "empty" && js_board[0][6] == "empty" &&
      !is_check(false) && !check_decorator(false, [[0,4],[0,5]]) && !check_decorator(false, [[0,4],[0,6]]))
        result.push([0,6]);
    if (!turn_list.includes("A8") && js_board[0][1] == "empty" && js_board[0][2] == "empty" && js_board[0][3] == "empty" &&
      !is_check(false) && !check_decorator(false, [[0,4],[0,1]]) && !check_decorator(false, [[0,4],[0,2]]) && !check_decorator(false, [[0,4],[0,3]]))
        result.push([0,2]);
  }

  return result;
}
