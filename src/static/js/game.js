class Piece {
	constructor(color, type, moved) {
		this.color = color;
		this.type = type;
		this.moved = moved;
	}
}

const field_to_number = {
	'a8': 0,
	'b8': 1,
	'c8': 2,
	'd8': 3,
	'e8': 4,
	'f8': 5,
	'g8': 6,
	'h8': 7,

	'a7': 8,
	'b7': 9,
	'c7': 10,
	'd7': 11,
	'e7': 12,
	'f7': 13,
	'g7': 14,
	'h7': 15,

	'a6': 16,
	'b6': 17,
	'c6': 18,
	'd6': 19,
	'e6': 20,
	'f6': 21,
	'g6': 22,
	'h6': 23,

	'a5': 24,
	'b5': 25,
	'c5': 26,
	'd5': 27,
	'e5': 28,
	'f5': 29,
	'g5': 30,
	'h5': 31,

	'a4': 32,
	'b4': 33,
	'c4': 34,
	'd4': 35,
	'e4': 36,
	'f4': 37,
	'g4': 38,
	'h4': 39,

	'a3': 40,
	'b3': 41,
	'c3': 42,
	'd3': 43,
	'e3': 44,
	'f3': 45,
	'g3': 46,
	'h3': 47,

	'a2': 48,
	'b2': 49,
	'c2': 50,
	'd2': 51,
	'e2': 52,
	'f2': 53,
	'g2': 54,
	'h2': 55,

	'a1': 56,
	'b1': 57,
	'c1': 58,
	'd1': 59,
	'e1': 60,
	'f1': 61,
	'g1': 62,
	'h1': 63,
}

const number_to_field = {
	0: 'a8',
	1: 'b8',
	2: 'c8',
	3: 'd8',
	4: 'e8',
	5: 'f8',
	6: 'g8',
	7: 'h8',

	8: 'a7',
	9: 'b7',
	10: 'c7',
	11: 'd7',
	12: 'e7',
	13: 'f7',
	14: 'g7',
	15: 'h7',

	16: 'a6',
	17: 'b6',
	18: 'c6',
	19: 'd6',
	20: 'e6',
	21: 'f6',
	22: 'g6',
	23: 'h6',

	24: 'a5',
	25: 'b5',
	26: 'c5',
	27: 'd5',
	28: 'e5',
	29: 'f5',
	30: 'g5',
	31: 'h5',

	32: 'a4',
	33: 'b4',
	34: 'c4',
	35: 'd4',
	36: 'e4',
	37: 'f4',
	38: 'g4',
	39: 'h4',

	40: 'a3',
	41: 'b3',
	42: 'c3',
	43: 'd3',
	44: 'e3',
	45: 'f3',
	46: 'g3',
	47: 'h3',

	48: 'a2',
	49: 'b2',
	50: 'c2',
	51: 'd2',
	52: 'e2',
	53: 'f2',
	54: 'g2',
	55: 'h2',

	56: 'a1',
	57: 'b1',
	58: 'c1',
	59: 'd1',
	60: 'e1',
	61: 'f1',
	62: 'g1',
	63: 'h1',
}

const fen_dict = {
	'whitepawn': 'P',
	'whiteknight': 'N',
	'whitebishop': 'B',
	'whiterook': 'R',
	'whiteking': 'K',
	'whitequeen': 'Q',

	'blackpawn': 'p',
	'blackknight': 'n',
	'blackbishop': 'b',
	'blackrook': 'r',
	'blackking': 'k',
	'blackqueen': 'q',
}

var pieces = new Array(64);

var possible_moves = new Array(64);

var attacked_fields = new Array(64);

var player = 'white';

var moving = false;

var promoting = false;

var pickedId, pickedColor, pickedType, pickedMoved;

var targetId;

var prev_pickedId, prev_targetId;

var halfmoves = 0, fullmoves = 0, enpassant_sqr = '-';

function initPieces() {
	for (var i = 0; i < 64; i++) {
		$("#board").append('<div class="field" id="f' + i + '"></div>');
	}
}

function renderPieces() {
	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null) {
			var path = 'url(/static/img/game_img/' + pieces[i].color + pieces[i].type + '.png)';
			$('#f' + i).css('background-image', path);
		}
		else {
			$('#f' + i).css('background-image', 'none');
		}
	}
}

function allowDragging() {
	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null && pieces[i].color != player) {
			$('#f' + i).draggable({
				disabled: true
			});
			$('#f' + i).attr('class', 'field');

		}
		if (pieces[i] != null && pieces[i].color == player) {
			$('#f' + i).draggable({
				disabled: false
			});
			$('#f' + i).attr('class', 'field ui-draggable ui-draggable-handle');
		}
	}
}

function addListeners() {
	$('#board').mousedown(function (e) {
		piecePick(e);
	});

	$('#board').mouseup(function (e) {
		pieceDrop(e);
	});

}

function removeListeners() {
	$('#board').unbind();
}


function disableDragging() { 
	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null) {
			$('#f' + i).draggable({
				disabled: true
			});
			$('#f' + i).attr('class', 'field ui-draggable ui-draggable-handle');
		}
	}
}

function startMove() {
	moving = true;
}

function endMove() {

	if (player == 'black') {
		fullmoves++;
	}
	prev_pickedId = pickedId;
	prev_targetId = targetId;
	renderPieces();

	var result = isCheckmate(oppositeColor(player))

	moving = false;
	// var player isn't changing but is loaded when the page loads for individual users respectively and it stays the same
	// changePlayer();
	allowDragging();
	var fen = getFEN()


	// if the game ends
	if(result != false) {
		var dict = {
			'type': 'endgame',
			'result': result,
			'fen': fen,
		}

		dict = JSON.stringify(dict);
		websocket.send(dict);
	}
	else {
		var dict = {
			'type': 'move',
			'fen': fen,
			'player': player
		}

		dict = JSON.stringify(dict);
		websocket.send(dict);
	}
}

function changePlayer() {
	if (player == 'white') {
		player = 'black';
	}
	else {
		player = 'white';
	}
}

function knightMoves(p) {
	var c = pieces[p].color;
	var patterns = [-10, 6, -17, 15, -15, 17, -6, 10];

	var start = 0;
	var end = 8;

	if (p % 8 == 0) {
		start = 4;
	}
	if (p % 8 == 1) {
		start = 2;
	}
	if (p % 8 == 6) {
		end = 6;
	}
	if (p % 8 == 7) {
		end = 4;
	}

	for (var i = start; i < end; i++) {
		var offset = patterns[i];
		if (p + offset >= 0 && p + offset < 64) {
			if (pieces[p + offset] == null || pieces[p + offset].color != c) {
				possible_moves[p + offset] = true;
			}
		}
	}
}

function pawnMoves(p) {

	var c = pieces[p].color;

	switch (c) {
		case 'white':
			next_white:
			{
				if (p - 8 >= 0) {
					if (pieces[p - 8] == null) {
						possible_moves[p - 8] = true;
						if (p - 16 >= 0) {
							if (pieces[p].moved == false && pieces[p - 16] == null) {
								possible_moves[p - 16] = true;
							}
						}
					}
				}
				if (p - 9 >= 0) {
					if (p % 8 == 0) {
						break next_white;
					}
					if (pieces[p - 9] != null && pieces[p - 9].color != c) {
						possible_moves[p - 9] = true;
					}
				}
			}
			if (p - 7 >= 0) {
				if (p % 8 == 7) {
					break;
				}
				if (pieces[p - 7] != null && pieces[p - 7].color != c) {
					possible_moves[p - 7] = true;
				}
			}
			break;
		case 'black':

			next_black:
			{
				if (p + 8 < 64) {
					if (pieces[p + 8] == null) {
						possible_moves[p + 8] = true;
						if (pieces[p].moved == false && pieces[p + 16] == null) {
							possible_moves[p + 16] = true;
						}
					}
				}
				if (p + 9 < 64) {
					if (p % 8 == 7) {
						break next_black;
					}
					if (pieces[p + 9] != null && pieces[p + 9].color != c) {
						possible_moves[p + 9] = true;
					}
				}
			}
			if (p + 7 < 64) {
				if (p % 8 == 0) {
					break;
				}
				if (pieces[p + 7] != null && pieces[p + 7].color != c) {
					possible_moves[p + 7] = true;
				}
			}
			break;
	}
}

function bishopMoves(p) {
	var c = pieces[p].color;
	var patterns = [9, 7, -9, -7];
	var pos = p;
	for (var i = 0; i < 4; i++) {
		p = pos;
		var offset = patterns[i];
		while (p >= 0 && p < 64) {
			if (p + offset < 0 || p + offset > 63 || (p % 8 == 0 && (offset == -9 || offset == 7)) ||
				(p % 8 == 7 && (offset == -7 || offset == 9))) {
				break;
			}
			if (pieces[p + offset] != null) {
				if (pieces[p + offset].color != c) {
					p = p + offset;
					possible_moves[p] = true;
					break;
				}
				break;
			}
			p = p + offset;
			possible_moves[p] = true;
		}
	}
}

function rookMoves(p) {
	var c = pieces[p].color;
	var patterns = [8, -8, 1, -1];

	var pos = p;
	for (var i = 0; i < 2; i++) {
		var offset = patterns[i];
		p = pos;
		while (p >= 0 && p < 64) {
			if (p + offset > 63 || p + offset < 0) {
				break;
			}
			if (pieces[p + offset] != null) {
				if (pieces[p + offset].color != c) {
					p = p + offset;
					possible_moves[p] = true;
					break;
				}
				break;
			}
			p = p + offset;
			possible_moves[p] = true;
		}
	}
	for (var i = 2; i < 4; i++) {
		var offset = patterns[i];
		p = pos;
		while (p >= 0 && p < 64) {
			if ((offset == -1 && p % 8 == 0) || (offset == 1 && p % 8 == 7)) {
				break;
			}
			if (pieces[p + offset] != null) {
				if (pieces[p + offset].color != c) {
					p = p + offset;
					possible_moves[p] = true;
					break;
				}
				break;
			}
			p = p + offset;
			possible_moves[p] = true;
		}
	}
}

function kingMoves(p) {
	var c = pieces[p].color;
	var start = 0;
	var end = 8;
	var patterns = [-9, -1, 7, -8, 8, -7, 1, 9];
	if (p % 8 == 0) {
		start = 3;
	}
	if (p % 8 == 7) {
		end = 5;
	}

	for (var i = start; i < end; i++) {
		var offset = patterns[i];
		if (p + offset >= 0 && p + offset < 64) {
			if (pieces[p + offset] == null || pieces[p + offset].color != c) {
				possible_moves[p + offset] = true;
			}
		}
	}
	castles(p);
}

function queenMoves(p) {
	bishopMoves(p);
	rookMoves(p);
}

function updatePossibleMoves(p) {

	for (var i = 0; i < 64; i++) {
		possible_moves[i] = false;
	}

	var t = pieces[p].type;

	switch (t) {
		case 'pawn':
			pawnMoves(p);
			break;
		case 'knight':
			knightMoves(p);
			break;
		case 'bishop':
			bishopMoves(p);
			break;
		case 'rook':
			rookMoves(p);
			break;
		case 'king':
			kingMoves(p);
			break;
		case 'queen':
			queenMoves(p);
			break;
	}
}

function isLegal(p1, p2) {
	var capture = false;
	var c1 = pieces[p1].color;
	var t1 = pieces[p1].type;
	var m1 = pieces[p1].moved;

	var c2, t2, m2;

	if (pieces[p2] != null) {
		c2 = pieces[p2].color;
		t2 = pieces[p2].type;
		m2 = pieces[p2].moved;
		capture = true;
	}

	pieces[p2] = new Piece(c1, t1, true);
	pieces[p1] = null;


	if (isCheck(c1) == false) {
		pieces[p1] = new Piece(c1, t1, m1);
		pieces[p2] = null;
		if (capture == true) {
			pieces[p2] = new Piece(c2, t2, m2);
		}
		return true;
	}
	else {
		pieces[p1] = new Piece(c1, t1, m1);
		pieces[p2] = null;
		if (capture == true) {
			pieces[p2] = new Piece(c2, t2, m2);
		}
		return false;
	}
}

function isCheck(c) {
	var king_pos;

	updateAttackedFields(oppositeColor(c));

	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null && pieces[i].color == c && pieces[i].type == 'king') {
			king_pos = i;
			break;
		}
	}
	if (attacked_fields[king_pos] == false) {
		return false;
	}
	else {
		return true;
	}
}

function oppositeColor(c) {
	if (c == 'white') return 'black';
	else return 'white';
}

function pawnFields(p) {
	var c = pieces[p].color;
	switch (c) {
		case 'white':

			if (p - 9 >= 0 && p % 8 != 0) {
				attacked_fields[p - 9] = true;
			}
			if (p - 7 >= 0 && p % 8 != 7) {
				attacked_fields[p - 7] = true;
			}
			break;
		case 'black':
			if (p + 9 < 63 && p % 8 != 7) {
				attacked_fields[p + 9] = true;
			}
			if (p + 7 < 63 && p % 8 != 0) {
				attacked_fields[p + 7] = true;
			}
			break;
	}
}

function knightFields(p) {
	var patterns = [-10, 6, -17, 15, -15, 17, -6, 10];
	var start = 0;
	var end = 8;

	if (p % 8 == 0) {
		start = 4;
	}
	if (p % 8 == 1) {
		start = 2;
	}
	if (p % 8 == 6) {
		end = 6;
	}
	if (p % 8 == 7) {
		end = 4;
	}

	for (var i = start; i < end; i++) {
		var offset = patterns[i];
		if (p + offset >= 0 && p + offset < 64) {
			attacked_fields[p + offset] = true;
		}
	}
}

function bishopFields(p) {
	var patterns = [9, 7, -9, -7];
	var c = pieces[p].color;
	var pos = p;
	for (var i = 0; i < 4; i++) {
		p = pos;
		var offset = patterns[i];
		while (p >= 0 && p < 64) {
			if (p + offset < 0 || p + offset > 63 || (p % 8 == 0 && (offset == -9 || offset == 7)) ||
				(p % 8 == 7 && (offset == -7 || offset == 9))) {
				break;
			}
			if (pieces[p + offset] != null) {
				p = p + offset;
				attacked_fields[p] = true;
				break;
			}
			p = p + offset;
			attacked_fields[p] = true;
		}
	}
}

function rookFields(p) {
	var patterns = [8, -8, 1, -1];
	var c = pieces[p].color;
	var pos = p;
	for (var i = 0; i < 2; i++) {
		var offset = patterns[i];
		p = pos;
		while (p >= 0 && p < 64) {
			if (p + offset > 63 || p + offset < 0) {
				break;
			}
			if (pieces[p + offset] != null) {
				p = p + offset;
				attacked_fields[p] = true;
				break;
			}
			p = p + offset;
			attacked_fields[p] = true;
		}
	}
	for (var i = 2; i < 4; i++) {
		var offset = patterns[i];
		p = pos;
		while (p >= 0 && p < 64) {
			if (p + offset > 63 || p + offset < 0 || (offset == -1 && p % 8 == 0) || (offset == 1 && p % 8 == 7)) {
				break;
			}
			if (pieces[p + offset] != null) {
				p = p + offset;
				attacked_fields[p] = true;
				break;
			}
			p = p + offset;
			attacked_fields[p] = true;
		}
	}
}

function kingFields(p) {
	var start = 0;
	var end = 8;
	var patterns = [-9, -1, 7, -8, 8, -7, 1, 9];
	if (p % 8 == 0) {
		start = 4;
	}
	if (p % 8 == 7) {
		end = 5;
	}

	for (var i = start; i < end; i++) {
		var offset = patterns[i];
		if (p + offset >= 0 && p + offset < 64) {
			attacked_fields[p + offset] = true;
		}
	}
}

function queenFields(p) {
	bishopFields(p);
	rookFields(p);
}


function updateAttackedFields(c) {
	for (var i = 0; i < 64; i++) {
		attacked_fields[i] = false;
	}

	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null && pieces[i].color == c) {
			var p = i;

			switch (pieces[i].type) {
				case 'pawn':
					pawnFields(p);
					break;
				case 'knight':
					knightFields(p);
					break;
				case 'bishop':
					bishopFields(p);
					break;
				case 'rook':
					rookFields(p);
					break;
				case 'king':
					kingFields(p);
					break;
				case 'queen':
					queenFields(p);
					break;
			}
		}
	}
}



function isCheckmate(c) {
	for (var i = 0; i < 64; i++) {
		if (pieces[i] != null && pieces[i].color == c) {
			updatePossibleMoves(i);
			for (var j = 0; j < 64; j++) {
				if (possible_moves[j] == true && isLegal(i, j) == true) {
					return false;
				}
			}
		}
	}

	var output;
	if (isCheck(c)) {
		switch (c) {
			case 'white':
				// $('#board').append('<div id="endgamebox"><p>BLACK WINS</p></div>');
				output = 'blackwins';
				break;
			case 'black':
				// $('#board').append('<div id="endgamebox"><p>WHITE WINS</p></div>');
				output = 'whitewins';
				break;
		}
	}
	else {
		// $('#board').append('<div id="endgamebox"><p>DRAW</p></div>');
		output = 'draw';
	}
	return output;
	// lines that are commented out are handled in the 'game_against_html' now
}

function castles(p) {
	if (pieces[p].moved == false) {
		var c = pieces[p].color;
		updateAttackedFields(oppositeColor(player));
		switch (c) {
			case 'white':
				right:
				{
					for (var i = 57; i < 60; i++) {
						if (pieces[i] != null) {
							break right;
						}
					}
					for (var i = 58; i < 60; i++) {
						if (attacked_fields[i] == true) {
							break right;
						}
					}
					if (pieces[56] != null && pieces[56].color == c && pieces[56].moved == false) {
						possible_moves[58] = true;
					}
				}
				for (var i = 61; i < 63; i++) {
					if (pieces[i] != null || attacked_fields[i] == true) {
						return;
					}
				}
				if (pieces[63] != null && pieces[63].color == c && pieces[63].moved == false) {
					possible_moves[62] = true;
				}
				break;
			case 'black':
				right2:
				{
					for (var i = 1; i < 4; i++) {
						if (pieces[i] != null) {
							break right2;
						}
					}
					for (var i = 2; i < 4; i++) {
						if (attacked_fields[i] == true) {
							break right2;
						}
					}
					if (pieces[0] != null && pieces[0].color == c && pieces[0].moved == false) {
						possible_moves[2] = true;
					}
				}
				for (var i = 5; i < 7; i++) {
					if (pieces[i] != null || attacked_fields[i] == true) {
						return;
					}
				}
				if (pieces[7] != null && pieces[7].color == c && pieces[7].moved == false) {
					possible_moves[6] = true;
				}
				break;
		}
	}

}

function pawnPromotion() {
	$('#board').unbind();
	promoting = true;
	var temp = ['queen', 'rook', 'bishop', 'knight'];
	$('#board').append('<div id="promotionbox"></div>');
	for (var i = 0; i < 4; i++) {
		$('#promotionbox').append('<div class="pickbox" id="p' + i + '"></div>');
		var path = 'url(img/' + player + temp[i] + '.png)';
		$('#p' + i).css('background', path);
	}
	addPromotionListeners();

}

function addPromotionListeners() {
	$('.pickbox').click(function (e) {
		var id = e.target.id;
		var spawn_piece;
		switch (id) {
			case 'p0':
				spawn_piece = 'queen';
				break;
			case 'p1':
				spawn_piece = 'rook';
				break;
			case 'p2':
				spawn_piece = 'bishop';
				break;
			case 'p3':
				spawn_piece = 'knight';
				break;
		}
		console.log("targetId=" + targetId);
		pieces[targetId] = new Piece(player, spawn_piece, true);
		$('#promotionbox').remove();
		promoting = false;

	
		halfmoves = 0;
		enpassant_sqr = '-';
		

		endMove();
		addListeners();
	});


}

function piecePick(e) {
	//console.log('**PIECE PICK** e.which= ' + e.which + ' moving=' + moving + ' promoting=' +promoting);
	if (moving == true || promoting == true) { return; }
	//console.log('mousedown start');

	switch (e.which) {
		case 1:
			if (e.target && e.target.className == 'field ui-draggable ui-draggable-handle') {
				pickedId = new Number(e.target.id.replace('f', ""));
				pickedColor = pieces[pickedId].color;
				pickedType = pieces[pickedId].type;
				updatePossibleMoves(pickedId);
				startMove();
			}
			break;
	}
}

function pieceDrop(e) {
	//console.log('**PIECE DROP** e.which= ' + e.which + ' moving=' + moving + ' promoting=' +promoting);
	switch (e.which) {
		case 1:
			if (moving == false || promoting == true) { return; }
			else {
				//console.log('mouseup start');
				// send a message to the server to get the actual fen (production)
				// websocket.send('get_fen');


				var offset = $(e.target).position();

				offset.left = offset.left - $('#board').offset().left + 50;
				offset.top = offset.top - $('#board').offset().top + 50;

				var x = Math.floor(offset.left / 100);
				var y = Math.floor(offset.top / 100);
				targetId = x + (y * 8);



				$('#f' + pickedId).css('left', 0);
				$('#f' + pickedId).css('top', 0);

				// en passant

				if (pieces[prev_targetId] != null && pieces[prev_targetId].type == 'pawn' && pickedType == 'pawn' &&
					Math.abs(pickedId - prev_targetId) == 1 && Math.abs(prev_pickedId - prev_targetId) == 16 && Math.abs(prev_targetId - targetId) == 8) {
					var c2 = pieces[prev_targetId].color;
					var t2 = pieces[prev_targetId].type;
					var m2 = pieces[prev_targetId].moved;

					pieces[targetId] = new Piece(pickedColor, pickedType, true);
					pieces[pickedId] = null;
					pieces[prev_targetId] = null;

					if (isCheck(player) == true) {
						pieces[pickedId] = new Piece(pickedColor, pickedType, pickedMoved);
						pieces[prev_targetId] = new Piece(c2, t2, m2);
						pieces[targetId] = null;
						moving = false;
						return;
					}
					else {
						enpassant_sqr = '-';
						halfmoves = 0;

						endMove();
						return;
					}
				}

				//if placed on the initial field

				if (targetId == pickedId) {
					moving = false;
					return;
				}


				//if against moving pattern

				if (possible_moves[targetId] == false) {
					moving = false;
					return;
				}

				//check if the player is being check after the move

				if (isLegal(pickedId, targetId) == false) {
					moving = false;
					return;
				}


				if (pieces[targetId] != null || pieces[pickedId].type == 'pawn') {
					halfmoves = 0;
				}
				else {
					halfmoves++;
				}

				// castles

				if (pickedType == 'king' && Math.abs(targetId - pickedId) == 2) {
					pieces[pickedId] = null;

					switch (targetId) {
						case 2:
							pieces[targetId] = new Piece(player, 'king', true);
							pieces[0] = null;
							pieces[3] = new Piece(player, 'rook', true);
							break;
						case 6:
							pieces[targetId] = new Piece(player, 'king', true);
							pieces[7] = null;
							pieces[5] = new Piece(player, 'rook', true);
							break;
						case 58:
							pieces[targetId] = new Piece(player, 'king', true);
							pieces[56] = null;
							pieces[59] = new Piece(player, 'rook', true);
							break;
						case 62:
							pieces[targetId] = new Piece(player, 'king', true);
							pieces[63] = null;
							pieces[61] = new Piece(player, 'rook', true);
							break;
					}
					fen_enpassant = '-';
					halfmoves++;

					endMove();
					return;
				}



				//if legal
				pieces[pickedId] = null;
				pieces[targetId] = new Piece(pickedColor, pickedType, true);

				//not necessary anymore cause allowDragging() function handles that
				//$('#f' + pickedId).attr('class', 'field'); 


				if ((targetId < 8 || targetId >= 56) && pieces[targetId].type == 'pawn') {
					renderPieces();
					pawnPromotion();
					return;
				}

				if (Math.abs(targetId - pickedId) == 16 && pieces[targetId].type == 'pawn') {
					switch (player) {
						case 'white':
							enpassant_sqr = targetId + 8;
							break;
						case 'black':
							enpassant_sqr = targetId - 8;
							break;
					}
				}
				else {
					enpassant_sqr = "-";
				}

				endMove();
				return;
			}
	}
}


function renderWithFEN(fen) {
	const numbers = ['1', '2', '3', '4', '5', '6', '7', '8']

	var fen_split = fen.split(' ');
	var fen_position = fen_split[0];
	var fen_player = fen_split[1];
	var fen_castles = fen_split[2];
	var fen_enpassant = fen_split[3];
	var fen_halfmoves = fen_split[4];
	var fen_fullmoves = fen_split[5];

	for (var i = 0; i < 64; i++) {
		pieces[i] = null;
		$('#f' + i).css('background-image', 'none');
	}

	var render_pos = 0;
	for (var i = 0; i < fen_position.length; i++) {

		var letter = fen[i];

		if (letter == '/') {
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
			case 'p':
				color = 'black';
				type = 'pawn';
				break;
			case 'n':
				color = 'black';
				type = 'knight';
				break;
			case 'b':
				color = 'black';
				type = 'bishop';
				break;
			case 'r':
				color = 'black';
				type = 'rook';
				break;
			case 'k':
				color = 'black';
				type = 'king';
				break;
			case 'q':
				color = 'black';
				type = 'queen';
				break;
			case 'P':
				color = 'white';
				type = 'pawn';
				break;
			case 'N':
				color = 'white';
				type = 'knight';
				break;
			case 'B':
				color = 'white';
				type = 'bishop';
				break;
			case 'R':
				color = 'white';
				type = 'rook';
				break;
			case 'K':
				color = 'white';
				type = 'king';
				break;
			case 'Q':
				color = 'white';
				type = 'queen';
				break;
		}
		pieces[render_pos] = new Piece(color, type, false);
		var path = 'url(/static/img/game_img/' + color + type + '.png)';
		$('#f' + render_pos).css('background-image', path);
		render_pos++;
	}

	/*

	now the 'player' variable stays the same throughout the game

	switch (fen_player) {
		case 'w':
			player = 'white';
			break;
		case 'b':
			player = 'black';
			break;
	}
	*/

	if (fen_castles != '-') {

		for (var i = 0; i < fen_castles.length; i++) {

			switch (fen_castles) {
				case 'K':
					pieces[60] = new Piece('white', 'king', false);
					pieces[63] = new Piece('white', 'rook', false);
					break;
				case 'Q':
					pieces[60] = new Piece('white', 'king', false);
					pieces[56] = new Piece('white', 'rook', false);
					break;
				case 'q':
					pieces[4] = new Piece('black', 'king', false);
					pieces[0] = new Piece('black', 'rook', false);
					break;
				case 'k':
					pieces[4] = new Piece('black', 'king', false);
					pieces[7] = new Piece('black', 'rook', false);
					break;
			}
		}
	}


	if (fen_enpassant != '-') {
		var target_pos = field_to_number[fen_enpassant];

		switch (player) {
			case 'white':
				prev_pickedId = target_pos - 8;
				prev_targetId = target_pos + 8;
				break;
			case 'black':
				prev_pickedId = target_pos + 8;
				prev_targetId = target_pos - 8;
				break;
		}
	}

	halfmoves = new Number(fen_halfmoves);
	fullmoves = new Number(fen_fullmoves);

}


function getFEN() {
	var output = '';
	var empty_spaces = 0;
	for (var i = 0; i < 64; i++) {
		if (pieces[i] == null) {
			empty_spaces++;
		}
		else {
			if (empty_spaces != 0) {
				var temp = empty_spaces.toString();
				output += temp;
				empty_spaces = 0;
			}
			var c = pieces[i].color;
			var t = pieces[i].type;
			var key = new String(c + t);

			output += fen_dict[key];
		}
		if (i % 8 == 7) {
			if (empty_spaces != 0) {
				output += empty_spaces.toString();
				empty_spaces = 0;
			}
			if (i != 63) {
				output += '/';
			}
		}
	}
	output += ' ';

	if (player == 'white') {
		output += 'w';
	}
	else {
		output += 'b';
	}

	output += ' ';

	var castling = false;

	if (pieces[60] != null && pieces[60].type == 'king' && pieces[60].moved == false) {
		if (pieces[63] != null && pieces[63].type == 'rook' && pieces[63].moved == false) {
			output += 'K';
			castling = true;
		}
		if (pieces[56] != null && pieces[56].type == 'rook' && pieces[56].moved == false) {
			output += 'Q';
			castling = true;
		}
	}

	if (pieces[4] != null && pieces[4].type == 'king' && pieces[4].moved == false) {
		if (pieces[7] != null && pieces[7].type == 'rook' && pieces[7].moved == false) {
			output += 'k';
			castling = true;
		}
		if (pieces[0] != null && pieces[0].type == 'rook' && pieces[0].moved == false) {
			output += 'q';
			castling = true;
		}
	}

	if (castling == false) {
		output += "- ";
	}
	else {
		output += " ";
	}

	var enpassant = '-';
	if (enpassant_sqr != '-') {
		enpassant = number_to_field[enpassant_sqr];
	}

	output += enpassant + ' ' + String(halfmoves) + ' ' + String(fullmoves);

	return output;
}

