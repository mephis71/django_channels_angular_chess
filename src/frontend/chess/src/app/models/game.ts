export interface Game {
    id: number,
    player_white: string,
    player_black: string,
    winner: string,
    game_positions: Array<string>,
    move_timestamps: Array<Array<string>>
}