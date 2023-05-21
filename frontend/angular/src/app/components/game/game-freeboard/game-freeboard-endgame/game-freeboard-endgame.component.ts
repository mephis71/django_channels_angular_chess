import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'game-freeboard-endgame',
  templateUrl: './game-freeboard-endgame.html',
  styleUrls: ['./../../css/game-endgame.css']
})
export class GameFreeBoardEndgameComponent implements OnInit, OnDestroy {
  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  showResetButton = false;
  endgameInfo: string;
  
  constructor(
    private gameService: GameService
  ) {}

  resetGame() {
    let msg = {
      'type': 'reset'
    }
    this.endgameInfo = ''
    this.gameService.sendGameMsg(msg)
  }

  ngOnInit(): void {
    this.wsSubjectSub = this.gameService.gameWsObservableReady.subscribe({
      next: () => {
        this.gameWsSub = this.getGameWsSub();
      }
    })
  }

  ngOnDestroy(): void {
    let subs = [this.gameWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if (sub) {
        sub.unsubscribe()
      }
    }
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'reset') {
            this.showResetButton = false;
          }
          if(data.type == 'endgame') {
            this.showResetButton = true;
            if(data.game_result == 'blackwins') {
              this.endgameInfo = 'Black wins by checkmate';
            }
            else if(data.game_result == 'whitewins') {
              this.endgameInfo = 'White wins by checkmate';
            }
            else if(data.game_result == 'draw-stalemate') {
              this.endgameInfo = 'Draw - stalemate';
            }
            else if(data.game_result == 'draw-50m') {
              this.endgameInfo = 'Draw - 50 moves rule';
            }
            else if(data.game_result == 'draw-3r') {
              this.endgameInfo = 'Draw - threefold repetition';
            }
            else if(data.game_result == 'draw-mutual') {
              this.endgameInfo = 'Draw - mutual agreement';
            }
            else if(data.game_result == 'whitewins-oot') {
              this.endgameInfo = 'White wins - out of time';
            }
            else if(data.game_result == 'blackwins-oot') {
              this.endgameInfo = 'Black wins - out of time';
            }
            else if(data.game_result == 'blackwins-abandonment') {
              this.endgameInfo = 'Black wins - White abandoned the game';
            }
            else if(data.game_result == 'whitewins-abandonment') {
              this.endgameInfo = 'White wins - Black abandoned the game';
            }
            else if(data.game_result == 'whitewins-resignment') {
              this.endgameInfo = 'White wins - Black resigned';
            }
            else if(data.game_result == 'blackwins-resignment') {
              this.endgameInfo = 'Black wins - White resigned';
            }
            if(data.game_result == 'draw-abandonment') {
              this.endgameInfo = 'The game was abandoned';
            }
          }
        }
      }
    });
  }
}
