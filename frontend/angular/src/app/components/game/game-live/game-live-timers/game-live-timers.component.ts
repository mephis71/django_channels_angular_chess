import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import { Game } from 'src/app/models/game';
import { GameService } from 'src/app/services/game.service';
import { Color } from 'src/app/enums/pieces';
import { Subscription } from 'rxjs';
import { GameInProgress } from 'src/app/models/game-in-progress';

@Component({
  selector: 'game-live-timers',
  templateUrl: './../../templates/game-timers.html',
  styleUrls: ['./../../css/game-timers.scss']
})
export class GameLiveTimersComponent implements OnInit, OnDestroy {
  public Color = Color;
  
  @Input() boardOrientation: Color;
  @Input() game: GameInProgress;

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
    const subs = [this.wsSubjectSub, this.gameWsSub]
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
          if(['init', 'move', 'game_end', 'move_cancel_accept'].includes(data.type)) {
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
        return (this.game && this.game.player_white_id) ? this.game.player_white_id : null
      case Color.BLACK:
        return (this.game && this.game.player_black_id) ? this.game.player_black_id : null
      default:
        return null
    }
  }

}
