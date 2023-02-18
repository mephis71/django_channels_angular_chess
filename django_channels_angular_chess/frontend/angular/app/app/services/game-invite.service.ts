import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { GameInvite } from '../models/game_invite';

@Injectable({
  providedIn: 'root'
})
export class GameInviteService {
  ws: WebSocket;
  invites: GameInvite[] = []
  username: string;
  
  constructor(
    private router: Router
    ) { }

  public openWebSocket() {
    this.ws = new WebSocket('ws://0.0.0.0:8000/game/invite/')

    this.ws.onopen = (event) => {
    };

    this.ws.onmessage = (event) => {
      var data = JSON.parse(event.data)
      
      if(data.type == 'invite' && data.to_user == this.username) {
        if(!this.invites.some(e => e.from_user == data.from_user)) {
          this.invites.push(data);
        }
        else {
          this.invites = this.invites.filter(e => e.from_user != data.from_user)
          this.invites.push(data)
        }
      }

      if(data.type == 'invite_accept' && data.usernames.includes(this.username)) {
        this.router.navigate([`/game/live/${data.game_id}`])
      }
    };

    this.ws.onclose = (event) => {
    };
  }

  public closeWebSocket() {
    this.ws.close();
  }

  public sendMsg(msg: any) {
    this.ws.send(JSON.stringify(msg))
  }

  clearVariables() {
    this.username = '';
    this.invites = [];
  }
}
