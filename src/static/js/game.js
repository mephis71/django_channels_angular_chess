class Piece {
  constructor(color, type, moved) {
    this.color = color;
    this.type = type;
    this.moved = moved;
  }
}

const field_to_number = {
  a8: 0,
  b8: 1,
  c8: 2,
  d8: 3,
  e8: 4,
  f8: 5,
  g8: 6,
  h8: 7,

  a7: 8,
  b7: 9,
  c7: 10,
  d7: 11,
  e7: 12,
  f7: 13,
  g7: 14,
  h7: 15,

  a6: 16,
  b6: 17,
  c6: 18,
  d6: 19,
  e6: 20,
  f6: 21,
  g6: 22,
  h6: 23,

  a5: 24,
  b5: 25,
  c5: 26,
  d5: 27,
  e5: 28,
  f5: 29,
  g5: 30,
  h5: 31,

  a4: 32,
  b4: 33,
  c4: 34,
  d4: 35,
  e4: 36,
  f4: 37,
  g4: 38,
  h4: 39,

  a3: 40,
  b3: 41,
  c3: 42,
  d3: 43,
  e3: 44,
  f3: 45,
  g3: 46,
  h3: 47,

  a2: 48,
  b2: 49,
  c2: 50,
  d2: 51,
  e2: 52,
  f2: 53,
  g2: 54,
  h2: 55,

  a1: 56,
  b1: 57,
  c1: 58,
  d1: 59,
  e1: 60,
  f1: 61,
  g1: 62,
  h1: 63,
};

const number_to_field = {
  0: "a8",
  1: "b8",
  2: "c8",
  3: "d8",
  4: "e8",
  5: "f8",
  6: "g8",
  7: "h8",

  8: "a7",
  9: "b7",
  10: "c7",
  11: "d7",
  12: "e7",
  13: "f7",
  14: "g7",
  15: "h7",

  16: "a6",
  17: "b6",
  18: "c6",
  19: "d6",
  20: "e6",
  21: "f6",
  22: "g6",
  23: "h6",

  24: "a5",
  25: "b5",
  26: "c5",
  27: "d5",
  28: "e5",
  29: "f5",
  30: "g5",
  31: "h5",

  32: "a4",
  33: "b4",
  34: "c4",
  35: "d4",
  36: "e4",
  37: "f4",
  38: "g4",
  39: "h4",

  40: "a3",
  41: "b3",
  42: "c3",
  43: "d3",
  44: "e3",
  45: "f3",
  46: "g3",
  47: "h3",

  48: "a2",
  49: "b2",
  50: "c2",
  51: "d2",
  52: "e2",
  53: "f2",
  54: "g2",
  55: "h2",

  56: "a1",
  57: "b1",
  58: "c1",
  59: "d1",
  60: "e1",
  61: "f1",
  62: "g1",
  63: "h1",
};

const fen_dict = {
  whitepawn: "P",
  whiteknight: "N",
  whitebishop: "B",
  whiterook: "R",
  whiteking: "K",
  whitequeen: "Q",

  blackpawn: "p",
  blackknight: "n",
  blackbishop: "b",
  blackrook: "r",
  blackking: "k",
  blackqueen: "q",
};

var color = null;

var picked_id;

var target_id;

var prev_picked_id, prev_target_id;

var moving = false

var moves_list = ''

function init_fields() {
  for (var i = 0; i < 64; i++) {
    $("#board").append(
      '<div class="field" id="f' + i + '" color="none" type="none"></div>'
    );
  }
}

function render_with_fen(fen) {
  const numbers = ["1", "2", "3", "4", "5", "6", "7", "8"];

  var fen_split = fen.split(" ");
  var fen_position = fen_split[0];
  var fen_player = fen_split[1];
  var fen_castles = fen_split[2];
  var fen_enpassant = fen_split[3];
  var fen_halfmoves = fen_split[4];
  var fen_fullmoves = fen_split[5];

  for (var i = 0; i < 64; i++) {
    $("#f" + i).css("background-image", "none");
  }

  var render_pos = 0;
  for (var i = 0; i < fen_position.length; i++) {
    var letter = fen[i];

    if (letter == "/") {
      continue;
    }

    if (numbers.includes(letter)) {
      letter = new Number(letter);
      render_pos += letter;
      continue;
    }

    var color;
    var type;
    switch (letter) {
      case "p":
        color = "black";
        type = "pawn";
        break;
      case "n":
        color = "black";
        type = "knight";
        break;
      case "b":
        color = "black";
        type = "bishop";
        break;
      case "r":
        color = "black";
        type = "rook";
        break;
      case "k":
        color = "black";
        type = "king";
        break;
      case "q":
        color = "black";
        type = "queen";
        break;
      case "P":
        color = "white";
        type = "pawn";
        break;
      case "N":
        color = "white";
        type = "knight";
        break;
      case "B":
        color = "white";
        type = "bishop";
        break;
      case "R":
        color = "white";
        type = "rook";
        break;
      case "K":
        color = "white";
        type = "king";
        break;
      case "Q":
        color = "white";
        type = "queen";
        break;
    }
    var path = "url(/static/img/game_img/" + color + type + ".png)";
    $("#f" + render_pos).attr("color", color);
    $("#f" + render_pos).attr("type", type);
    $("#f" + render_pos).css("background-image", path);
    render_pos++;
  }
}

function allow_dragging() {
  for (var i = 0; i < 64; i++) {
    var piece = $("#f" + i);
    if (piece.attr("color") == color) {
      piece.draggable({
        disabled: false,
      });
      piece.attr("class", "field ui-draggable ui-draggable-handle");
    } else if (piece.attr("color") != color) {
      piece.draggable({
        disabled: true,
      });
      piece.attr("class", "field");
    }
  }
}

function add_listeners() {
  $("#board").mousedown(function (e) {
    piece_pick(e);
  });

  $("#board").mouseup(function (e) {
    piece_drop(e);
  });
}

function add_arrow_listeners() {
  document.onkeydown = function (e) {
    switch (e.key) {
      case "ArrowLeft":
		if (scrolling_iterator - 1 < 0) {break;} 
		else {
        scrolling_iterator -= 1;
        render_with_fen(game_positions[scrolling_iterator]);
		}
        break;

      case "ArrowRight":
        if (scrolling_iterator + 1 > game_positions.length) {break;} 
		else {
        scrolling_iterator += 1;
        render_with_fen(game_positions[scrolling_iterator]);
        }
        break;

      case "ArrowUp":
        scrolling_iterator = game_positions.length;
        render_with_fen(game_positions[scrolling_iterator]);
        break;

      case "ArrowDown":
        scrolling_iterator = 0;
        render_with_fen(game_positions[scrolling_iterator]);
        break;

      default:
        return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
  };
}

function remove_listeners() {
  $("#board").unbind();
}

function disable_dragging() {
  for (var i = 0; i < 64; i++) {
    var piece = $("#f" + i);
    piece.draggable({
      disabled: true,
    });
    piece.attr("class", "field ui-draggable ui-draggable-handle");
  }
}

function opposite_color(c) {
  if (c == "white") return "black";
  else return "white";
}

function pawn_promotion(p, t, turn) {
  $("#board").unbind();
  var temp = ["queen", "rook", "bishop", "knight"];
  $("#board").append('<div id="promotionbox"></div>');
  for (var i = 0; i < 4; i++) {
    $("#promotionbox").append('<div class="pickbox" id="p' + i + '"></div>');
    var path = "url(img/" + turn + temp[i] + ".png)";
    $("#p" + i).css("background", path);
  }
  add_promotion_listeners(p, t, turn);
}

function add_promotion_listeners(p, t, turn) {
  $(".pickbox").click(function (e) {
    var id = e.target.id;
    var picked_piece;
    switch (id) {
      case "p0":
        picked_piece = "queen";
        break;
      case "p1":
        picked_piece = "rook";
        break;
      case "p2":
        picked_piece = "bishop";
        break;
      case "p3":
        picked_piece = "knight";
        break;
    }
    $("#promotionbox").remove();
    send_promotion_pick(p, t, picked_piece, turn);
  });
}

function piece_pick(e) {
  console.log('moving:',moving)
  switch (e.which) {
    case 1:
      if (e.target.getAttribute("color") == color) {
        picked_id = Number(e.target.id.slice(1));
        moving = true;
      }
      break;
  }
}

function piece_drop(e) {
  console.log('moving:',moving)
  if (moving == true) {
    switch (e.which) {
      case 1:
        var offset = $(e.target).position();

        offset.left = offset.left - $("#board").offset().left + 50;
        offset.top = offset.top - $("#board").offset().top + 50;

        var x = Math.floor(offset.left / 100);
        var y = Math.floor(offset.top / 100);
        target_id = x + y * 8;

        $("#f" + picked_id).css("left", 0);
        $("#f" + picked_id).css("top", 0);

        console.log(picked_id, target_id);

        if (target_id == picked_id) {
          return;
        }
        send_move(picked_id, target_id);
        var move = '(' + picked_id + ', ' + target_id + '), '
        moves_list += move
        moving = false;
    }
  }
}

function send_move(picked_id, target_id) {
  msg = {
    'color': color,
    'type': "move",
    'picked_id': picked_id,
    'target_id': target_id,
  };
  msg = JSON.stringify(msg);
  websocket_game.send(msg);
}

function send_promotion_pick(p, t, piece, turn) {
  msg = {
    'type': "promotion",
    'p': p,
    't': t,
    'piece': piece,
    'turn': turn,
  };
  msg = JSON.stringify(msg);
  websocket_game.send(msg);
}
