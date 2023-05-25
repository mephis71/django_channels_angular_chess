import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { DrawMessage, MoveCancelMessage, ResignMessage } from 'src/app/models/ws-messages';
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
    const subs = [this.gameWsSub, this.wsSubjectSub]
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
    const msg = new MoveCancelMessage('request');
    this.gameService.sendMoveCancelMsg(msg);
    this.allowMoveCancelRequest = false;
  }

  acceptMoveCancelRequest() {
    const msg = new MoveCancelMessage('accept');
    this.gameService.sendMoveCancelMsg(msg);
    this.moveCancelRequestPending = false;
    this.allowMoveCancelRequest = false;
  }

  rejectMoveCancelRequest() {
    const msg = new MoveCancelMessage('reject');
    this.gameService.sendMoveCancelMsg(msg);
    this.moveCancelRequestPending = false;
    this.allowMoveCancelRequest = true;
  }

  resign() {
    this.showResignButton = false;
    this.showResignCancelButton = true;
    this.showResignConfirmButton = true;
  }

  confirmResign() {
    const msg = new ResignMessage();
    this.gameService.sendResignMsg(msg);
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
    const msg = new DrawMessage('offer');
    this.gameService.sendDrawMsg(msg);
    this.allowDrawOffer = false;
  }

  acceptDrawOffer() {
    const msg = new DrawMessage('accept');
    this.gameService.sendDrawMsg(msg);
    this.drawOfferPending = false;
    this.allowDrawOffer = false;
  }

  rejectDrawOffer() {
    const msg = new DrawMessage('offer');
    this.gameService.sendDrawMsg(msg);
    this.drawOfferPending = false;
    this.allowDrawOffer = true;
  }
}
