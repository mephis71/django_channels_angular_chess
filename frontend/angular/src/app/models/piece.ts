import { Color } from "../enums/pieces";
import { PieceType } from "../enums/pieces";

export class Piece {
    color: Color;
    type: PieceType;
    empty: boolean;
    imgUrl: string | null;

    constructor(color: Color, type: PieceType, empty: boolean) {
        this.color = color;
        this.type = type;
        this.empty = empty;
        if(([Color.WHITE, Color.BLACK].includes(this.color)) && (this.type != PieceType.NONE)) { 
            this.imgUrl = "assets/img/game_img/" + this.color + this.type + ".png";
        }
        else {
            this.imgUrl = null
        }
    }
}