import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Profile } from '../models/profile';
import { HttpResponse } from '@angular/common/http';
import { User } from '../models/user';
import { Game } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(
    private http: HttpClient
    ) { } 

  getUser(): Observable<User> {
    return this.http.get<User>(
      'http://localhost:8000/api/user',
      {withCredentials:true}
    )
  }

  getProfile(username: string): Observable<Profile> {
    return this.http.get<Profile>(
      `http://localhost:8000/api/user/profile/${username}`,
      {withCredentials:true}
    )
  }

  register(form: any) {
      return this.http.post(
      'http://localhost:8000/api/user/register/',
      {user: form},
      {observe: 'response'}
    )
  }

  login(form: any): Observable<HttpResponse<User>> {
    return this.http.post<User>(
      'http://localhost:8000/api/user/login/',
      {user: form},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  logout(): Observable<HttpResponse<any>> {
    return this.http.post(
      'http://localhost:8000/api/user/logout/',
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  sendFriendRequest(form: any): Observable<HttpResponse<any>> {
    return this.http.post('http://localhost:8000/api/user/send_friend_request/',
      form.getRawValue(),
      {
        withCredentials: true,
        observe: 'response'
      }
    )
  }

  acceptFriendRequest(id: number): Observable<HttpResponse<any>> {
    return this.http.post(
      `http://localhost:8000/api/user/accept_friend_request/${id}`,
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  acceptGameInvite(invite: any): Observable<Object> {
    return this.http.post(
      'http://localhost:8000/api/game/invite_accept/',
      {invite},
      {withCredentials:true}
    )
  }

  getRunningGames(): Observable<Game[]> {
    return this.http.get<Game[]>(
      'http://localhost:8000/api/user/running_games',
      {withCredentials:true}
    )
  }

  removeFriend(friend_username: string): Observable<Object> {
    return this.http.post(
      `http://localhost:8000/api/user/remove_friend/${friend_username}`,
      {},
      {withCredentials:true,
      observe: 'response'}
    )
  }

  rejectFriendRequest(friend_request_id: number) {
    return this.http.post(
      `http://localhost:8000/api/user/reject_friend_request/${friend_request_id}`,
      {},
      {withCredentials: true,
      observe: 'response'}
    )
  }
}
