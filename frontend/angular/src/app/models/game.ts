export class Game {
    id: number;
    playerWhite: string;
    playerBlack: string;
    winner: string;
    fen: string;
    gamePositions: string[];
    moveTimestamps: string[][];

    constructor(id: number, player_white: string, player_black: string, winner: string, fen: string, game_postions: string[], move_timestamps: string[][]) {
        this.id = id;
        this.playerWhite = player_white;
        this.playerBlack = player_black;
        this.winner = winner;
        this.fen = fen;
        this.gamePositions = game_postions;
        this.moveTimestamps = move_timestamps;
    }
}

export interface Game {
    id: number,
    player_white: string,
    player_black: string,
    winner: string,
    fen: string;
    game_positions: string[],
    move_timestamps: string[][]
}