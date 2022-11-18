import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { GameService } from '../services/game.service';
import { Emitters } from '../emitters/emitters';

@Component({
  selector: 'app-game',
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})

export class GameComponent implements OnInit, OnDestroy {

  pick_id: number;
  drop_id: number;

  player_white: string;
  player_black: string;

  constructor(
    public wsService: GameService,
    private http: HttpClient,
  ) {}

  ngOnInit(): void {
    this.http.get('http://localhost:8000/api/user', {withCredentials:true}).subscribe({
      next:(res: any) => {
        Emitters.authEmitter.emit(true);
        Emitters.usernameEmitter.emit(res.username);
      },
      error:(err: any) => {
        Emitters.authEmitter.emit(false);
      }
    })

    let path = window.location.pathname.split('/')
    let game_id = path[path.length-1]
    console.log(path)
    this.http.get(
      `http://localhost:8000/api/game/${game_id}`, {withCredentials: true}).subscribe({
        next:(res: any) => {
          console.log(res)
          this.player_black = res.player_black
          this.player_white = res.player_white
        },
        error:(err: any) => {
          console.log(err)
        }
      })

    this.wsService.openWebSocket()
  }

  ngOnDestroy(): void {
    this.wsService.closeWebSocket()
  }

  onPick(event: any) {
    this.pick_id = event.event.target.id;
  }

  onDrop(event: any) {
    this.drop_id = event.event.target.id;
    if(this.pick_id && this.drop_id && (this.pick_id != this.drop_id)) {
      let msg = {
        "type": "move",
        "pick_id": this.pick_id,
        "drop_id": this.drop_id
      }
      this.wsService.sendMsg(JSON.stringify(msg))
    }
  }

  sendPromotionPick(piece_type: string) {
    let msg = {
      "type": "promotion",
      "piece_type": piece_type
    }
    this.wsService.sendMsg(JSON.stringify(msg));
    this.wsService.promoting = false;
  }

  sendDrawOffer() {
    let msg = {
      "type": "draw_offer"
    }
    this.wsService.sendMsg(JSON.stringify(msg));
    this.wsService.allow_draw_offer = false;
  }

  acceptDrawOffer() {
    let msg = {
      "type": "draw_accept"
    }
    this.wsService.sendMsg(JSON.stringify(msg));
    this.wsService.draw_offer_pending = false;

  }

  rejectDrawOffer() {
    let msg = {
      "type": "draw_reject"
    }
    this.wsService.sendMsg(JSON.stringify(msg));
    this.wsService.draw_offer_pending = false;
    this.wsService.allow_draw_offer = true;
  }
}
