import { HttpClient, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, share, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { GamePuzzle } from '../models/game-puzzle';
import { MoveMessage, PromotionPickMessage } from '../models/ws-messages';

@Injectable({
  providedIn: 'root'
})
export class PuzzleService {
  private wsUrl = environment.wsUrl;
  private apiUrl = environment.apiUrl;

  public puzzleWsObservableReady = new Subject<void>();
  public puzzleObjectReady = new Subject<GamePuzzle>();

  puzzleWs: WebSocket;
  puzzleWsObservable: Observable<any>;

  constructor(
    private http: HttpClient,
  ) { }

  public createGamePuzzle(settings: any): Observable<HttpResponse<any>> {
    return this.http.post<GamePuzzle>(
      `${this.apiUrl}/game/puzzle/`,
      {fen: settings.fen},
      {withCredentials: true,
        observe: 'response'}
    )
  }

  public getGamePuzzle(id: number): Observable<GamePuzzle> {
    return this.http.get<GamePuzzle>(
      `${this.apiUrl}/game/puzzle/${id}`,
      {withCredentials:true}
    )
  }

  public openGamePuzzleWebSocket(path: string) {
    this.puzzleWs = new WebSocket(`${this.wsUrl}/${path}`)
    this.puzzleWsObservable = this.createGamePuzzleWsObservable();
    this.puzzleWsObservableReady.next();
  }

  public closeGamePuzzleWebSocket() {
    if(this.puzzleWs) {
      this.puzzleWs.close();
    }
  }

  createGamePuzzleWsObservable(): Observable<any> {
    return new Observable((observer) => {
      this.puzzleWs.onmessage = (event) => {
        var data = JSON.parse(event.data);
        observer.next(data);
      };

      this.puzzleWs.onclose = (event) => {
      };
    }).pipe(share())
  }

  public sendGameMoveMsg(msg: MoveMessage) {
    this.puzzleWs.send(JSON.stringify(msg));
  }

  public sendPromotionPickMsg(msg: PromotionPickMessage) {
    this.puzzleWs.send(JSON.stringify(msg));
  }
}
