import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Profile } from '../models/profile';
import { HttpResponse } from '@angular/common/http';
import { User } from '../models/user';

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

  send_friend_request(form: any): Observable<HttpResponse<any>> {
    return this.http.post('http://localhost:8000/api/user/send_friend_request/',
      form.getRawValue(),
      {
        withCredentials: true,
        observe: 'response'
      }
    )
  }

  accept_friend_request(id: number): Observable<HttpResponse<any>> {
    return this.http.post(
      `http://localhost:8000/api/user/accept_friend_request/${id}`,
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  accept_game_invite(invite_accept: any): Observable<Object> {
    return this.http.post(
      'http://localhost:8000/api/game/invite_accept/',
      {invite_accept},
      {withCredentials:true}
    )
  }
}
