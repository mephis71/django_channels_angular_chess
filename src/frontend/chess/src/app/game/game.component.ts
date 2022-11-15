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
    if(this.pick_id && this.drop_id) {
      let msg = {
        "type": "move",
        "pick_id": this.pick_id,
        "drop_id": this.drop_id
      }
      this.wsService.sendMsg(JSON.stringify(msg))
    }
  }
}
