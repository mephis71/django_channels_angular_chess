import { PieceType } from "../enums/pieces";

// in-game messages

export class MoveMessage {
    type: string = 'move';
    pick_id: number;
    drop_id: number;
    
    constructor(pick_id: number, drop_id: number) {
        this.pick_id = pick_id;
        this.drop_id = drop_id;
    }
}


export class PromotionPickMessage {
    type: string = 'promotion';
    pieceType: PieceType;

    constructor(pieceType: PieceType) {
        this.pieceType = pieceType;
    }
}


export class GameResetMessage {
    type: string = 'reset';
}


export class MoveCancelMessage {
    type: string = 'move_cancel';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}

export class ResignMessage {
    type: string = 'resign';
}



export class DrawMessage {
    type: string = 'draw';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}


export class RematchMessage {
    type: string = 'rematch';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}

// chat messages

export class ChatMessage {
    username: string;
    text: string;

    constructor(username: string, text: string) {
        this.username = username;
        this.text = text;
    }
}

// game invites

export class GameInvite {
    type: string = 'game_invite'
    from_user_id: number;
    from_user_username: string;
    to_user_id: number;
    to_user_username: string;
    settings: {
        white_id: number | null;
        black_id: number | null;
        random_colors: boolean;
        duration: number;
    }

    constructor (from_user_id: number, from_user_username: string, to_user_id: number, to_user_username: string, settings: GameInviteSettings) {
        this.from_user_id = from_user_id;
        this.from_user_username = from_user_username;
        this.to_user_id = to_user_id;
        this.to_user_username = to_user_username;
        this.settings = settings;
    }
}


export class GameInviteSettings {
    white_id: number | null;
    black_id: number | null;
    random_colors: boolean;
    duration: number;
    constructor (white_id: number | null, black_id: number | null, random_colors: boolean, duration: number) {
        this.white_id = white_id;
        this.black_id = black_id;
        this.random_colors = random_colors;
        this.duration = duration;
    }
}

// stockfish messages

export class StockfishPositionMessage {
    type: string = 'position';
    fen: string;

    constructor(fen: string) {
        this.fen = fen;
    }
}

