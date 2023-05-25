import { PieceType } from "../enums/pieces";

// in-game messages

export class MoveMessage implements IMoveMessage {
    type: string = 'move';
    pick_id: number;
    drop_id: number;
    
    constructor(pick_id: number, drop_id: number) {
        this.pick_id = pick_id;
        this.drop_id = drop_id;
    }
}

interface IMoveMessage {
    type: string;
    pick_id: number;
    drop_id: number;
}

export class PromotionPickMessage implements IPromotionPickMessage {
    type: string = 'promotion';
    piece_type: PieceType;

    constructor(piece_type: PieceType) {
        this.piece_type = piece_type;
    }
}

interface IPromotionPickMessage {
    type: string;
    piece_type: PieceType;
}

export class GameResetMessage implements IGameResetMessage {
    type: string = 'reset';
}

interface IGameResetMessage {
    type: string;
}

export class MoveCancelMessage implements IMoveCancelMessage {
    type: string = 'move_cancel';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}

interface IMoveCancelMessage {
    type: string;
    action: string;
}

export class ResignMessage implements IResignMessage {
    type: string = 'resign';
}

interface IResignMessage {
    type: string;
}

export class DrawMessage implements IDrawMessage {
    type: string = 'draw';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}

interface IDrawMessage {
    type: string;
    action: string;
}

export class RematchMessage implements IRematchMessage {
    type: string = 'rematch';
    action: string;

    constructor(action: string) {
        this.action = action;
    }
}

interface IRematchMessage {
    type: string;
    action: string;
}

// chat messages

export class ChatMessage implements IChatMessage {
    username: string;
    text: string;

    constructor(username: string, text: string) {
        this.username = username;
        this.text = text;
    }
}

interface IChatMessage {
    username: string;
    text: string;
}

// game invites

export class GameInvite implements IGameInvite {
    type: string = 'game_invite';
    from_user: string;
    to_user: string;
    settings: {
        white: string | null;
        black: string | null;
        random_colors: boolean;
        duration: number;
    }

    constructor (from_user: string, to_user: string, settings: IGameInviteSettings) {
        this.from_user = from_user;
        this.to_user = to_user;
        this.settings = settings;
    }
}

interface IGameInvite {
    type: string;
    from_user: string;
    to_user: string;
    settings: IGameInviteSettings
}

export interface IGameInviteSettings {
    white: string | null;
    black: string | null;
    random_colors: boolean;
    duration: number;
}

// stockfish messages

export class StockfishPositionMessage implements IStockfishPositionMessage {
    type: string = 'position';
    fen: string;

    constructor(fen: string) {
        this.fen = fen;
    }
}

interface IStockfishPositionMessage {
    type: string;
    fen: string;
}

