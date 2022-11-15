export class Piece {
    color: string;
    type: string;
    empty: boolean;
    img_url: string;

    constructor(color: string, type: string, empty: boolean) {
        this.color = color;
        this.type = type;
        this.empty = empty;
        this.img_url = "assets/img/game_img/" + this.color + this.type + ".png";
    }
}