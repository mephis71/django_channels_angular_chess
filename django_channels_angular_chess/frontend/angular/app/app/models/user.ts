export interface User {
    username: string,
    email: string,
    friends: string[],
    friend_requests: Array<{username:string, id: number}>,   
}