var temp_board = document.querySelectorAll("#board tr");
const header_text = document.getElementsByTagName("h1")[0];
const html_board = [];
const js_board = [];
const turn = {"white-pawn": true, "white-bishop": true, "black-pawn": false, "black-bishop": false, "empty": undefined};
const upgrade = {"white-pawn": "white-bishop", "black-pawn": "black-bishop", "white-bishop": "white-bishop", "black-bishop": "black-bishop"}
var white_turn = true;
var targeting_piece = false;
var double_eating = false;
var piece_targeted = [];
var seleted_piece_moves = [];
var i, j;
var old_element, new_element;

for(i = 0; i < 8; i++)
  html_board.push(temp_board[i].children);

for(i = 0; i < 8; i++) {
  temp_board = [];
  for(j = 0; j < 8; j++) {
    if((i + j) % 2 == 0) html_board[i][j].style.backgroundColor = "white";
    if((i + j) % 2 == 1) addClicker(i, j);
    if((i + j) % 2 == 1 && i < 3) {
       html_board[i][j].classList.add("black-pawn");
       temp_board.push("black-pawn");
    }
    else if((i + j) % 2 == 1 && i > 4) {
      html_board[i][j].classList.add("white-pawn");
      temp_board.push("white-pawn");
    }
    else {
      temp_board.push("empty");
    }
  }
  js_board.push(temp_board);
}
delete temp_board;

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

function changeTurn() {
  white_turn = !white_turn;
  if (js_board.map(function(value, index, array) {return !value.includes("white-pawn") && !value.includes("white-bishop")}).every(function (value, index, array) {return value}) || canImove(true)) {
    old_element = document.getElementById("board");
    new_element = old_element.cloneNode(true);
    old_element.parentNode.replaceChild(new_element, old_element);
    header_text.innerHTML = "checkers - black wins!";
  }
  else if (js_board.map(function(value, index, array) {return !value.includes("black-pawn") && !value.includes("black-bishop")}).every(function (value, index, array) {return value}) || canImove(false)) {
    old_element = document.getElementById("board");
    new_element = old_element.cloneNode(true);
    old_element.parentNode.replaceChild(new_element, old_element);
    header_text.innerHTML = "checkers - white wins!";
  }
}

function canImove(bool) {
  return js_board.map(function (value, index, array)
    {
      return value.map(function (value1, index1, array1) {
        if (turn[value1] === bool) {
          return (whereCanIMove(index, index1).length == 0);
        }
        return true;
      }).every(function (value2, index2, array2) {return value2})
    }).every(function (value3, index3, array3) {return value3});
}

function click(indexY, indexX) {
  if (double_eating) {
    if (piece_targeted[0] == indexY && piece_targeted[1] == indexX) {
      for(j of seleted_piece_moves)
        html_board[j[0]][j[1]].classList.remove("option-block", "option-block-selected");
      html_board[indexY][indexX].classList.remove("option-block", "option-block-selected");
      seleted_piece_moves = [];
      piece_targeted = [];
      double_eating = false;
      if (indexY == (turn[js_board[indexY][indexX]] ? 0 : 7)) {
        js_board[indexY][indexX] = upgrade[js_board[indexY][indexX]];
        html_board[indexY][indexX].classList.remove("black-pawn", "white-pawn");
        html_board[indexY][indexX].classList.add(js_board[indexY][indexX]);
      }
      changeTurn();
      return;
    }
    for(i of seleted_piece_moves) {
      if (i[0] == indexY && i[1] == indexX) {
        html_board[piece_targeted[0]][piece_targeted[1]].classList.remove("black-pawn", "black-bishop", "white-pawn", "white-bishop", "selected");
        html_board[indexY][indexX].classList.add(js_board[piece_targeted[0]][piece_targeted[1]]);
        js_board[indexY][indexX] = js_board[piece_targeted[0]][piece_targeted[1]];
        js_board[piece_targeted[0]][piece_targeted[1]] = "empty";
        for(j of seleted_piece_moves)
          html_board[j[0]][j[1]].classList.remove("option-block", "option-block-selected");
        html_board[piece_targeted[0]][piece_targeted[1]].classList.remove("option-block", "option-block-selected");
        html_board[i[2]][i[3]].classList.remove("black-pawn", "black-bishop", "white-pawn", "white-bishop", "selected");
        js_board[i[2]][i[3]] = "empty";
        seleted_piece_moves = whereCanIMoveAfterFirstTurn(indexY, indexX);
        if (seleted_piece_moves.length != 0) {
          for(j of seleted_piece_moves)
            html_board[j[0]][j[1]].classList.add("option-block")
          html_board[indexY][indexX].classList.add("option-block", "option-block-selected");
          piece_targeted = [indexY, indexX];
        }
        else {
          seleted_piece_moves = [];
          piece_targeted = [];
          double_eating = false;
          if (indexY == (turn[js_board[indexY][indexX]] ? 0 : 7)) {
            js_board[indexY][indexX] = upgrade[js_board[indexY][indexX]];
            html_board[indexY][indexX].classList.remove("black-pawn", "white-pawn");
            html_board[indexY][indexX].classList.add(js_board[indexY][indexX]);
          }
          changeTurn()
        }
      }
    }
    return;
  }
  if (targeting_piece) {
    if (piece_targeted[0] == indexY && piece_targeted[1] == indexX) {
      for(i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.remove("option-block")
      html_board[indexY][indexX].classList.remove("selected");
      targeting_piece = false;
      piece_targeted = [];
      seleted_piece_moves = [];
    }
    else if (turn[js_board[indexY][indexX]] === white_turn && whereCanIMove(indexY, indexX).length != 0) {
      for(i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.remove("option-block");
      html_board[piece_targeted[0]][piece_targeted[1]].classList.remove("selected");
      html_board[indexY][indexX].classList.add("selected");
      piece_targeted = [indexY, indexX];
      seleted_piece_moves = whereCanIMove(indexY, indexX);
      for(i of seleted_piece_moves)
        html_board[i[0]][i[1]].classList.add("option-block")
    }
    else {
      for(i of seleted_piece_moves) {
        if (i[0] == indexY && i[1] == indexX) {
          html_board[piece_targeted[0]][piece_targeted[1]].classList.remove("black-pawn", "black-bishop", "white-pawn", "white-bishop", "selected");
          html_board[indexY][indexX].classList.add(js_board[piece_targeted[0]][piece_targeted[1]]);
          js_board[indexY][indexX] = js_board[piece_targeted[0]][piece_targeted[1]];
          js_board[piece_targeted[0]][piece_targeted[1]] = "empty";
          for(j of seleted_piece_moves)
            html_board[j[0]][j[1]].classList.remove("option-block", "option-block-selected");
          if (i[2]) {
            html_board[i[3]][i[4]].classList.remove("black-pawn", "black-bishop", "white-pawn", "white-bishop", "selected");
            js_board[i[3]][i[4]] = "empty";
            seleted_piece_moves = whereCanIMoveAfterFirstTurn(indexY, indexX);
            if (seleted_piece_moves.length != 0) {
              for(j of seleted_piece_moves)
                html_board[j[0]][j[1]].classList.add("option-block")
              html_board[indexY][indexX].classList.add("option-block", "option-block-selected");
              double_eating = true;
              piece_targeted = [indexY, indexX];
            }
            else {
              seleted_piece_moves = [];
              piece_targeted = [];
              if (indexY == (turn[js_board[indexY][indexX]] ? 0 : 7)) {
                js_board[indexY][indexX] = upgrade[js_board[indexY][indexX]];
                html_board[indexY][indexX].classList.remove("black-pawn", "white-pawn");
                html_board[indexY][indexX].classList.add(js_board[indexY][indexX]);
              }
              changeTurn()
            }
          }
          else {
            seleted_piece_moves = [];
            piece_targeted = [];
            if (indexY == (turn[js_board[indexY][indexX]] ? 0 : 7)) {
              js_board[indexY][indexX] = upgrade[js_board[indexY][indexX]];
              html_board[indexY][indexX].classList.remove("black-pawn", "white-pawn");
              html_board[indexY][indexX].classList.add(js_board[indexY][indexX]);
            }
            changeTurn();
          }
          targeting_piece = false;
          break;
        }
      }
    }
  }
  else if (turn[js_board[indexY][indexX]] === white_turn && whereCanIMove(indexY, indexX).length != 0) {
    html_board[indexY][indexX].classList.add("selected");
    targeting_piece = true;
    piece_targeted = [indexY, indexX];
    seleted_piece_moves = whereCanIMove(indexY, indexX);
    for(i of seleted_piece_moves)
      html_board[i[0]][i[1]].classList.add("option-block")
  }
}

function hover(indexY, indexX) {
  if (turn[js_board[indexY][indexX]] === white_turn && whereCanIMove(indexY, indexX).length != 0 && !double_eating)
    html_board[indexY][indexX].classList.add("pointer");
  for(i of seleted_piece_moves) {
    if (i[0] == indexY && i[1] == indexX || (double_eating && piece_targeted[0] == indexY & piece_targeted[1] == indexX))
      html_board[indexY][indexX].classList.add("option-block-selected");
  }
}

function unhover(indexY, indexX) {
  html_board[indexY][indexX].classList.remove("pointer");
  html_board[indexY][indexX].classList.remove("option-block-selected");
}

function whereCanIMove(indexY, indexX) {
  let returned_value = [];
  if (js_board[indexY][indexX] == "white-pawn" || js_board[indexY][indexX] == "black-pawn") {
    let sign = turn[js_board[indexY][indexX]] ? -1 : 1;
    let final_row = turn[js_board[indexY][indexX]] ? 0 : 7;
    for (i of [-1, 1]) {
      if (indexX != (i == -1 ? 0 : 7)) {
        if (js_board[indexY + sign][indexX + i] == "empty")
        returned_value.push([indexY + sign, indexX + i, false]);
        else if (indexX != (i == -1 ? 1 : 6) && indexY != final_row - sign &&
        turn[js_board[indexY + sign][indexX + i]] != turn[js_board[indexY][indexX]] &&
        js_board[indexY + 2*sign][indexX + 2*i] == "empty")
        returned_value.push([indexY + 2*sign, indexX + 2*i, true, indexY + sign, indexX + i]);
      }
    }
  }
  else {
    let step, step1;
    for (i of [[1, 1], [-1, 1], [-1 , -1], [1, -1]]) {
      step = 0;
      while (true) {
        step += 1;
        if (indexY + step * i[0] == (i[0] == 1 ? 8 : -1) || indexX + step * i[1] == (i[1] == 1 ? 8 : -1))
          break;
        if (js_board[indexY + step * i[0]][indexX + step * i[1]] != "empty")
          break;
        returned_value.push([indexY + step * i[0], indexX + step * i[1], false])
      }
      if(indexY + step * i[0] >= 1 && indexY + step * i[0] < 7 && indexX + step * i[1] >= 1 && indexX + step * i[1] < 7 &&
          turn[js_board[indexY + step * i[0]][indexX + step * i[1]]] != turn[js_board[indexY][indexX]]) {
        step1 = step;
        while (true) {
          step += 1;
          if (indexY + step * i[0] == (i[0] == 1 ? 8 : -1) || indexX + step * i[1] == (i[1] == 1 ? 8 : -1))
            break;
          if (js_board[indexY + step * i[0]][indexX + step * i[1]] != "empty")
            break;
          returned_value.push([indexY + step * i[0], indexX + step * i[1], true, indexY + step1 * i[0], indexX + step1 * i[1]])
        }
      }
    }
  }
  return returned_value;
}

function whereCanIMoveAfterFirstTurn(indexY, indexX) {
  let returned_value = [];
  if (js_board[indexY][indexX] == "white-pawn" || js_board[indexY][indexX] == "black-pawn") {
    for (i of [[1, 1], [-1, 1], [-1 , -1], [1, -1]]) {
      if (indexY == (i[0] == 1 ? 6 : 1) || indexX == (i[1] == 1 ? 6 : 1)) continue;
      if (indexY == (i[0] == 1 ? 7 : 0) || indexX == (i[1] == 1 ? 7 : 0)) continue;
      if (js_board[indexY + i[0]][indexX + i[1]] != "empty" &&
        turn[js_board[indexY][indexX]] != turn[js_board[indexY + i[0]][indexX + i[1]]] &&
        js_board[indexY + 2*i[0]][indexX + 2*i[1]] == "empty")
        returned_value.push([indexY + 2*i[0], indexX + 2*i[1], indexY + i[0], indexX + i[1]])
    }
  }
  else {
    let step, step1;
    for (i of [[1, 1], [-1, 1], [-1 , -1], [1, -1]]) {
      step = 0;
      while (true) {
        step += 1;
        if (indexY + step * i[0] == (i[0] == 1 ? 8 : -1) || indexX + step * i[1] == (i[1] == 1 ? 8 : -1))
          break;
        if (js_board[indexY + step * i[0]][indexX + step * i[1]] != "empty")
          break;
      }
      if(indexY + step * i[0] >= 1 && indexY + step * i[0] < 7 && indexX + step * i[1] >= 1 && indexX + step * i[1] < 7 &&
          turn[js_board[indexY + step * i[0]][indexX + step * i[1]]] != turn[js_board[indexY][indexX]]) {
        step1 = step;
        while (true) {
          step += 1;
          if (indexY + step * i[0] == (i[0] == 1 ? 8 : -1) || indexX + step * i[1] == (i[1] == 1 ? 8 : -1))
            break;
          if (js_board[indexY + step * i[0]][indexX + step * i[1]] != "empty")
            break;
          returned_value.push([indexY + step * i[0], indexX + step * i[1], indexY + step1 * i[0], indexX + step1 * i[1]])
        }
      }
    }
  }
  return returned_value;
}



// this code is absolute shit i couldve made it like 180 lines
