import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Game } from '../models/game';
import { Observable, share, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { DrawMessage, GameInvite, MoveMessage, GameResetMessage, MoveCancelMessage, PromotionPickMessage, RematchMessage, ResignMessage } from '../models/ws-messages';
import { FreeBoardGameSettings } from '../models/freeboard-game';
import { GameInProgress } from '../models/game-in-progress';
import { GameInfo } from '../models/game-info';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private wsUrl = environment.wsUrl;
  private apiUrl = environment.apiUrl;

  public gameWsObservableReady = new Subject<void>();
  public gameObjectReady = new Subject<Game>();
  public sendGameInvite = new Subject<any>();
  public passCurrentPosition = new Subject<string>();

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

  public sendGameResetMsg(msg: GameResetMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendGameMoveMsg(msg: MoveMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendPromotionPickMsg(msg: PromotionPickMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendMoveCancelMsg(msg: MoveCancelMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendResignMsg(msg: ResignMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendDrawMsg(msg: DrawMessage) {
    this.gameWs.send(JSON.stringify(msg));
  }

  public sendRematchMsg(msg: RematchMessage) {
    this.gameWs.send(JSON.stringify(msg));
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

  getGameInProgress(id: number): Observable<GameInProgress>  {
    return this.http.get<GameInProgress>(
      `${this.apiUrl}/game/game_in_progress/${id}`,
      {withCredentials: true}
    )
  }

  getFreeBoardGame(): Observable<Game>  {
    return this.http.get<Game>(
      `${this.apiUrl}/game/freeboard`,
      {withCredentials: true}
    )
  }

  createFreeBoardGame(settings: FreeBoardGameSettings): Observable<Game>  {
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
      };
    }).pipe(share())
  }

  acceptGameInvite(gameInfo: GameInfo): Observable<Object> {
    return this.http.post(
      `${this.apiUrl}/game/invite_accept/`,
      {gameInfo},
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
