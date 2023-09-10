import { GameInviteSettings } from "./ws-messages";


export class GameInfo {
    players: number[];
    settings: GameInviteSettings;

    constructor(players: number[], settings: GameInviteSettings) {
        this.players = players;
        this.settings = settings;
    }
}