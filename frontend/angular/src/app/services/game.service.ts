import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Game } from '../models/game';
import { Observable, share, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private wsUrl = environment.wsUrl;
  private apiUrl = environment.apiUrl;

  public gameWsObservableReady = new Subject<void>();
  public gameObjectReady = new Subject<Game>();
  public sendGameInvite = new Subject<string>();
  

  gameWs: WebSocket;
  gameWsObservable: Observable<any>;

  constructor(
    private http: HttpClient,
  ) {}

  public openGameWebsocket(path: string) {
    this.gameWs = new WebSocket(`${this.wsUrl}/${path}`)
    this.gameWsObservable = this.createGameWsObservable();
    this.gameWsObservableReady.next();
  }

  public sendGameMsg(msg: any) {
    this.gameWs.send(JSON.stringify(msg))
  }

  public closeGameWebSocket() {
    if(this.gameWs) {
      this.gameWs.close();
    }
  }

  getGame(id: number): Observable<Game>  {
    return this.http.get<Game>(
      `${this.apiUrl}/game/${id}`,
      {withCredentials: true}
    )
  }

  getFreeBoardGame(id: number): Observable<Game>  {
    return this.http.get<Game>(
      `${this.apiUrl}/game/freeboard/${id}`,
      {withCredentials: true}
    )
  }

  createFreeBoardGame(settings: any): Observable<Game>  {
    return this.http.post<Game>(
      `${this.apiUrl}/game/freeboard/`,
      {settings},
      {withCredentials: true}
    )
  }

  createGameWsObservable(): Observable<any> {
    return new Observable((observer) => {
      this.gameWs.onmessage = (event) => {
        var data = JSON.parse(event.data);
        observer.next(data);
      };

      this.gameWs.onclose = (event) => {
        if (event.code == 4000){
          observer.next(event);
        }
      };
    }).pipe(share())
  }

  acceptGameInvite(invite: any): Observable<Object> {
    return this.http.post(
      `${this.apiUrl}/game/invite_accept/`,
      {invite},
      {withCredentials:true}
    )
  }

  getRunningGames(): Observable<Game[]> {
    return this.http.get<Game[]>(
      `${this.apiUrl}/user/running_games`,
      {withCredentials:true}
    )
  }
}
