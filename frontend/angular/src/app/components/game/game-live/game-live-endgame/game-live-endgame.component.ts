import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { DrawMessage, RematchMessage } from 'src/app/models/ws-messages';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'game-live-endgame',
  templateUrl: './../../templates/game-endgame.html',
  styleUrls: ['./../../css/game-endgame.css']
})
export class GameLiveEndgameComponent implements OnInit, OnDestroy {
  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  endgameInfo: string;
  
  showRematchButton = true;
  rematchOfferPending = false;

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
    const subs = [this.gameWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  sendRematch() {
    const msg = new RematchMessage('offer');
    this.gameService.sendRematchMsg(msg)
    this.showRematchButton = false;
  }

  acceptRematch() {
    const msg = new RematchMessage('accept');
    this.gameService.sendRematchMsg(msg)
    this.showRematchButton = false;
    this.rematchOfferPending = false;
  }

  rejectRematch() {
    const msg = new RematchMessage('reject');
    this.gameService.sendRematchMsg(msg)
    this.showRematchButton = true;
    this.rematchOfferPending = false;
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'endgame') {
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
    
          else if(data.type == 'rematch') {
            this.rematchOfferPending = true;
          }
    
          else if(data.type == 'rematch_reject') {
            this.showRematchButton = true;
          }
        }
      }
    });
  }

}