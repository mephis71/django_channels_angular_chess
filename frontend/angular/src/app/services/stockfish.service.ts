import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, share, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Game } from '../models/game';
import { StockfishPositionMessage } from '../models/ws-messages';

@Injectable({
  providedIn: 'root'
})
export class StockfishService {
  private wsUrl = environment.wsUrl;
  private apiUrl = environment.apiUrl;

  public stockfishWsObservableReady = new Subject<void>();

  stockfishWs: WebSocket;
  stockfishWsObservable: Observable<any>;

  constructor(
    private http: HttpClient,
  ) {}

  public openStockfishWebsocket(path: string, game: Game) {
    this.stockfishWs = new WebSocket(`${this.wsUrl}/${path}`);
    this.stockfishWsObservable = this.createStockfishWsObservable(game);
    this.stockfishWsObservableReady.next();
  }

  public sendStockfishPositionMsg(msg: StockfishPositionMessage) {
    this.stockfishWs.send(JSON.stringify(msg))
  }

  public closeStockfishWebSocket() {
    if(this.stockfishWs) {
      this.stockfishWs.close();
    }
  }

  createStockfishWsObservable(game: Game): Observable<any> {
    return new Observable((observer) => {
      this.stockfishWs.onopen = (event) => {
        const msg = new StockfishPositionMessage(game.game_positions[game.game_positions.length - 1])
        this.sendStockfishPositionMsg(msg)
      }
      this.stockfishWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        observer.next(data);
      };

      this.stockfishWs.onclose = (event) => {
      };
    }).pipe(share())
  }
}
