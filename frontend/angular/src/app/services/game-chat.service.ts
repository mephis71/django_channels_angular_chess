import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Observable, Subject } from 'rxjs';
import { share } from 'rxjs';
import { ChatMessage } from '../models/ws-messages';

@Injectable({
  providedIn: 'root'
})
export class GameChatService {
  chatWs: WebSocket;
  chatWsObservable: Observable<any>;

  public chatWsObservableReady = new Subject<void>();

  private wsUrl = environment.wsUrl;

  constructor() { }

  public openChatWebSocket(path: string) {
    this.chatWs = new WebSocket(`${this.wsUrl}/${path}`)
    this.chatWsObservable = this.createChatWsObservable();
    this.chatWsObservableReady.next()
  }

  public closeWebSocket() {
    if(this.chatWs) {
      this.chatWs.close();
    }
  }

  public sendChatMsg(msg: ChatMessage) {
    this.chatWs.send(JSON.stringify(msg))
  }

  createChatWsObservable(): Observable<any> {
    return new Observable((observer) => {
      this.chatWs.onmessage = (event) => {
        var data = JSON.parse(event.data);
        observer.next(data);
      };
    }).pipe(share()) 
  }
}
