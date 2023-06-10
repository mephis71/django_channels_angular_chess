import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Observable, share, Subject } from 'rxjs';
import { GameInvite } from '../models/ws-messages';

@Injectable({
  providedIn: 'root'
})
export class InviteService {
  inviteWs: WebSocket;
  inviteWsObservable: Observable<any>;

  public inviteWsObservableReady = new Subject<void>();
  public addNewFriend = new Subject<string>();
  
  private wsUrl = environment.wsUrl;
  
  constructor() { }

  public openInviteWebSocket(path: string) {
    this.inviteWs = new WebSocket(`${this.wsUrl}/${path}`)
    this.inviteWsObservable = this.createInviteWsObservable();
    this.inviteWsObservableReady.next()
  }

  public closeWebSocket() {
    if(this.inviteWs) {
      this.inviteWs.close();
    }
  }

  public sendGameInvite(msg: GameInvite) {
    this.inviteWs.send(JSON.stringify(msg))
  }

  createInviteWsObservable(): Observable<any> {
    return new Observable((observer) => {
      this.inviteWs.onmessage = (event) => {
        var data = JSON.parse(event.data);
        observer.next(data);
      };
    }).pipe(share())
  }
}
