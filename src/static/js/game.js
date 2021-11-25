class Piece {
	constructor(color, type, moved) {
		this.color = color;
		this.type = type;
		this.moved = moved;
	}
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

function initPieces() {
	for (var i = 0; i < 64; i++) {
		$("#board").append('<div class="field" id="f' + i + '"></div>');
	}

	pieces[0] = new Piece('black', 'rook', false);
	pieces[1] = new Piece('black', 'knight', false);
	pieces[2] = new Piece('black', 'bishop', false);
	pieces[3] = new Piece('black', 'queen', false);
	pieces[4] = new Piece('black', 'king', false);
	pieces[5] = new Piece('black', 'bishop', false);
	pieces[6] = new Piece('black', 'knight', false);
	pieces[7] = new Piece('black', 'rook', false);

	for (var i = 8; i < 16; i++) {
		pieces[i] = new Piece('black', 'pawn', false);
	}

	for (var i = 16; i < 48; i++) {
		pieces[i] = null;
	}

	for (var i = 48; i < 56; i++) {
		pieces[i] = new Piece('white', 'pawn', false);
	}

	pieces[56] = new Piece('white', 'rook', false);
	pieces[57] = new Piece('white', 'knight', false);
	pieces[58] = new Piece('white', 'bishop', false);
	pieces[59] = new Piece('white', 'queen', false);
	pieces[60] = new Piece('white', 'king', false);
	pieces[61] = new Piece('white', 'bishop', false);
	pieces[62] = new Piece('white', 'knight', false);
	pieces[63] = new Piece('white', 'rook', false);
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
			$('#f' + i).attr('class','field');
		
		}
		if (pieces[i] != null && pieces[i].color == player) {
			$('#f' + i).draggable({
				disabled: false
			});
			$('#f' + i).attr('class','field ui-draggable ui-draggable-handle');
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

function startMove() {
	moving = true;
}

function endMove() {
	prev_pickedId = pickedId;
	prev_targetId = targetId;
	renderPieces();

	// information about piece position change

	isCheckmate(oppositeColor(player))

	moving = false;
	changePlayer();
	allowDragging();
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
	if (isCheck(c)) {
		switch (c) {
			case 'white':
				$('#board').append('<div id="endgamebox"><p>BLACK WINS</p></div>');
				break;
			case 'black':
				$('#board').append('<div id="endgamebox"><p>WHITE WINS</p></div>');
				break;
		}
	}
	else {
		$('#board').append('<div id="endgamebox"><p>DRAW</p></div>');
	}
	return true;
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
		endMove();
		addListeners();
	});


}

function piecePick(e)
{
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

function pieceDrop(e)
{
	//console.log('**PIECE DROP** e.which= ' + e.which + ' moving=' + moving + ' promoting=' +promoting);
	switch (e.which) {
		case 1:
			if (moving == false || promoting == true) { return; }
			else {
				//console.log('mouseup start');

				

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


				endMove();
				return;
			}
	}
}