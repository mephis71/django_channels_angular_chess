import { PieceType, Color } from '../enums/pieces';
import { Piece } from '../models/piece';

export function fenToPieces(fen: string): Piece[] {
    var pieces = [];
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8];

    var fen_split = fen.split(" ");
    var fen_position = fen_split[0];

    for (var i = 0; i < fen_position.length; i++) {
      var letter = fen[i];

      if (letter == "/") {
        continue;
      }

      if (numbers.includes(Number(letter))) {
        for (let i = 0; i < Number(letter); i++) {
          pieces.push(new Piece(Color.NONE, PieceType.NONE, true))
        }
        continue;
      }
      let pieceInfo = letterToColorPieceType(letter);
      pieces.push(new Piece(pieceInfo[0], pieceInfo[1], false));
    }
    return pieces;
  }

function letterToColorPieceType(letter: string): [Color, PieceType] {
    var color = letterToColor(letter)
    var type = letterToPieceType(letter)

    return [color, type]
}

function letterToColor(letter: string): Color {
    const isUpperCase = (letter: string) => /^[A-Z]*$/.test(letter)
    if (isUpperCase(letter)) {
        var color = Color.WHITE
    }
    else {
        var color = Color.BLACK
    }
    return color
}

function letterToPieceType(letter: string): PieceType {
    switch (letter.toLowerCase()) {
        case 'p':
        return PieceType.PAWN
        case 'n':
        return PieceType.KNIGHT
        case 'b':
        return PieceType.BISHOP
        case 'r':
        return PieceType.ROOK
        case 'k':
        return PieceType.KING
        case 'q':
        return PieceType.QUEEN
    }
    return PieceType.NONE
}