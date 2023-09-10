export class GamePuzzle {
    id: number;
    fen: string;
    url: string;
    playerColor: string;

    constructor(fen: string, url: string, player_color: string) {
        this.fen = fen;
        this.url = url;
        this.playerColor = player_color;
    }
}

export interface IGamePuzzle {
    id: number;
    fen: string;
    url: string;
    player_color: string;
}