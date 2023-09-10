import { Game } from "./game";

export interface Profile {
    gameHistory: Game[],
    username: string
}