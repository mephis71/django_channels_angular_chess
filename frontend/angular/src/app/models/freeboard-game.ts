export class FreeBoardGameSettings implements IFreeBoardGameSettings {
    fen: string;

    constructor(fen: string) {
        this.fen = fen;
    }
}

interface IFreeBoardGameSettings {
    fen: string;
}