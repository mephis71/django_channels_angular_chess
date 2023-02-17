export interface GameInvite {
    type: string;
    from_user: string;
    to_user: string;
    settings: {
        white: string;
        black: string;
        random_colors: boolean;
        duration: number;
    }
}