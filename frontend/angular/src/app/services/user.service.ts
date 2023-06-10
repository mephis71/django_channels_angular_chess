import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { Profile } from '../models/profile';
import { HttpResponse } from '@angular/common/http';
import { IUser, User } from '../models/user';
import { environment } from 'src/environments/environment';
import { LoginInfo } from '../models/login-info';
import { RegisterInfo } from '../models/register-info';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl;
  private wsUrl = environment.wsUrl;
  public refreshUser = new Subject<User | null>();

  public onlineStatusWsObservableReady = new Subject<void>();
  onlineStatusWs: WebSocket;
  onlineStatusWsObservable: Observable<any>;

  public friendsOnlineStatusSubject = new Subject<Map<string, string>>();
  public setOnlineStatus = new Subject<{username: string, status: string}>();

  constructor(
    private http: HttpClient
    ) { } 

  public openStatusWebsocket() {
    this.onlineStatusWs = new WebSocket(`${this.wsUrl}/online_status`);
    this.onlineStatusWsObservable = this.createOnlineStatusWsObservable();
    this.onlineStatusWsObservableReady.next();
  }

  public closeStatusWebSocket() {
    if(this.onlineStatusWs) {
      this.onlineStatusWs.close();
    }
  }

  public sendOnlineStatus(status: string) {
    const data = {
      status: status
    }
    this.onlineStatusWs.send(JSON.stringify(data));
  }

  createOnlineStatusWsObservable(): Observable<any> {
    return new Observable((observer) => {
      this.onlineStatusWs.onopen = (event) => {
        this.sendOnlineStatus('online')
      }
      this.onlineStatusWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        observer.next(data);
      }
      this.onlineStatusWs.onclose = (event) => {
      }
    })
  }
  getUser(): Observable<IUser> {
    return this.http.get<IUser>(
      `${this.apiUrl}/user`,
      {withCredentials:true}
    )
  }

  getProfile(username: string): Observable<Profile> {
    return this.http.get<Profile>(
      `${this.apiUrl}/user/profile/${username}`,
      {withCredentials:true}
    )
  }

  register(registerInfo: RegisterInfo) {
      return this.http.post(
      `${this.apiUrl}/user/register/`,
      {register_info: registerInfo},
      {observe: 'response'}
    )
  }

  login(loginInfo: LoginInfo): Observable<HttpResponse<User>> {
    return this.http.post<User>(
      `${this.apiUrl}/user/login/`,
      {login_info: loginInfo},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  logout(): Observable<HttpResponse<any>> {
    return this.http.post(
      `${this.apiUrl}/user/logout/`,
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  sendFriendRequest(username: string): Observable<HttpResponse<any>> {
    return this.http.post(`${this.apiUrl}/user/send_friend_request/`,
      {to_username: username},
      {
        withCredentials: true,
        observe: 'response'
      }
    )
  }

  acceptFriendRequest(id: number): Observable<HttpResponse<any>> {
    return this.http.post(
      `${this.apiUrl}/user/accept_friend_request/${id}`,
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
  }

  removeFriend(friend_username: string): Observable<Object> {
    return this.http.post(
      `${this.apiUrl}/user/remove_friend/${friend_username}`,
      {},
      {withCredentials:true,
      observe: 'response'}
    )
  }

  rejectFriendRequest(friend_request_id: number) {
    return this.http.post(
      `${this.apiUrl}/user/reject_friend_request/${friend_request_id}`,
      {},
      {withCredentials: true,
      observe: 'response'}
    )
  }
}