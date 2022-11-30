import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class GameInviteService {
  ws: WebSocket;
  invites: string[] = []
  username: string;
  
  constructor(
    private router: Router
    ) { }

  public openWebSocket() {
    this.ws = new WebSocket('ws://localhost:8000/game/invite/')
    this.ws.onopen = (event) => {
      console.log('open:', event);
    };

    this.ws.onmessage = (event) => {
      var data = JSON.parse(event.data)
      if(data.type == 'invite'){
        if(data.to == this.username) {
          if(!this.invites.includes(data.from)) {
            this.invites.push(data.from)
          }
        }
      }

      if(data.type == 'invite_accept') {
        this.router.navigate([`/game/live/${data.game_id}`])
      }
    };

    this.ws.onclose = (event) => {
      console.log('close:', event);
    };
  }

  public closeWebSocket() {
    this.ws.close();
  }

  public sendMsg(msg: any) {
    this.ws.send(msg)
  }
}
