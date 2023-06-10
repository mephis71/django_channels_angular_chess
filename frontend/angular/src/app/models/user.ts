export class User {
    username: string;
    email: string;
    friends: string[];
    friendRequests: IFriendRequest[];

    constructor(user: IUser) {
        this.username = user.username;
        this.email = user.email;
        this.friends = user.friends;
        this.friendRequests = user.friend_requests;
    }
}

export interface IUser {
    username: string,
    email: string,
    friends: string[],
    friend_requests: IFriendRequest[],   
} 

export class FriendRequest implements IFriendRequest {
    id: number;
    username: string;

    constructor(id: number, username: string) {
        this.id = id;
        this.username = username;
    }
}

export interface IFriendRequest {
    id: number;
    username: string;
}