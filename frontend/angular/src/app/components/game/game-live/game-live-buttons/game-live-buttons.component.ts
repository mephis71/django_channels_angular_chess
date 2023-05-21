import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'game-live-buttons',
  templateUrl: './game-live-buttons.component.html',
  styleUrls: ['./game-live-buttons.component.css']
})
export class GameLiveButtonsComponent implements OnInit, OnDestroy {
  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  moveCancelError: string;

  allowDrawOffer = true;
  drawOfferPending = false;

  allowMoveCancelRequest = true;
  moveCancelRequestPending = false;

  showResignButton = true;
  showResignConfirmButton = false;
  showResignCancelButton = false;

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
    let subs = [this.gameWsSub, this.wsSubjectSub]
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
          if(data.type == 'endgame') {
            this.drawOfferPending = false;
            this.allowDrawOffer = false;
            this.allowMoveCancelRequest = false;
            this.moveCancelRequestPending = false;
            this.showResignButton = false;
            this.showResignConfirmButton = false;
            this.showResignCancelButton = false;
            
          }
          else if(data.type == 'draw_offer') {
            this.allowDrawOffer = false;
            this.drawOfferPending = true;
          }

          else if(data.type == 'draw_reject') {
            this.allowDrawOffer = true;
            this.drawOfferPending = false;
          }

          else if(data.type == 'move_cancel_request') {
            this.allowMoveCancelRequest = false;
            this.moveCancelRequestPending = true;
          }

          else if(['move_cancel_reject', 'move_cancel_accept'].includes(data.type)) {
            this.allowMoveCancelRequest = true;
            this.moveCancelRequestPending = false;
          }

          else if(data.type == 'move_cancel_error') {
            this.moveCancelError = "You can't do that now";
            this.allowMoveCancelRequest = true;
            this.moveCancelRequestPending = false;
          }
        }
      }
    });
  }

  


  sendMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_request"
    }
    this.gameService.sendGameMsg(msg);
    this.allowMoveCancelRequest = false;
  }

  acceptMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_accept"
    }
    this.gameService.sendGameMsg(msg);
    this.moveCancelRequestPending = false;
    this.allowMoveCancelRequest = false;
  }

  rejectMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_reject"
    }
    this.gameService.sendGameMsg(msg);
    this.moveCancelRequestPending = false;
    this.allowMoveCancelRequest = true;
  }

  resign() {
    this.showResignButton = false;
    this.showResignCancelButton = true;
    this.showResignConfirmButton = true;
  }

  confirmResign() {
    let msg = {
      'type': 'resign'
    }
    this.gameService.sendGameMsg(msg);
    this.showResignButton = false;
    this.showResignCancelButton = false;
    this.showResignConfirmButton = false;
  }

  cancelResign() {
    this.showResignButton = true;
    this.showResignCancelButton = false;
    this.showResignConfirmButton = false;
  }

  sendDrawOffer() {
    let msg = {
      "type": "draw_offer"
    }
    this.gameService.sendGameMsg(msg);
    this.allowDrawOffer = false;
  }

  acceptDrawOffer() {
    let msg = {
      "type": "draw_accept"
    }
    this.gameService.sendGameMsg(msg);
    this.drawOfferPending = false;
    this.allowDrawOffer = false;
  }

  rejectDrawOffer() {
    let msg = {
      "type": "draw_reject"
    }
    this.gameService.sendGameMsg(msg);
    this.drawOfferPending = false;
    this.allowDrawOffer = true;
  }
}
