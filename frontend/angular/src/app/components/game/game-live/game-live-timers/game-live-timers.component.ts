import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import { Game } from 'src/app/models/game';
import { GameService } from 'src/app/services/game.service';
import { Color } from 'src/app/enums/pieces';
import { Subscription } from 'rxjs';

@Component({
  selector: 'game-live-timers',
  templateUrl: './../../templates/game-timers.html',
  styleUrls: ['./../../css/game-timers.css']
})
export class GameLiveTimersComponent implements OnInit, OnDestroy {
  public Color = Color;
  
  @Input() boardOrientation: Color;
  @Input() game: Game;

  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  timeWhite: string;
  timeBlack: string;

  constructor(
    private gameService: GameService
  ) {}

  ngOnInit(): void {
    this.wsSubjectSub = this.gameService.gameWsObservableReady.subscribe({
      next: () => {
        this.gameWsSub = this.getGameWsSub();
      }
    })
  }

  ngOnDestroy(): void {
    let subs = [this.wsSubjectSub, this.gameWsSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(['init', 'move', 'endgame', 'move_cancel_accept'].includes(data.type)) {
            this.timeWhite = data.time_white;
            this.timeBlack = data.time_black;
          }

          else if(data.type == 'time') {
            if(data.color == 'white') {
              this.timeWhite = data.time;
            }
            else if(data.color == 'black') {
              this.timeBlack = data.time;
            }
          }
        }
      }
    });
  }

  getPlayer(color: Color) {
    switch(color) {
      case Color.WHITE:
        return (this.game && this.game.player_white) ? this.game.player_white : null
      case Color.BLACK:
        return (this.game && this.game.player_black) ? this.game.player_black : null
      default:
        return null
    }
  }

}
