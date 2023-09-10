export class GameInProgress {
    id: number;
    player_white_id: number;
    player_black_id: number;

    constructor(id: number, player_white_id: number, player_black_id: number) {
        this.id = id;
        this.player_white_id = player_white_id;
        this.player_black_id = player_black_id;
    }
}