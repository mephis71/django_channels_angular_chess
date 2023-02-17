import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { GameLiveService } from '../../services/game-live.service';
import { Emitters } from '../../emitters/emitters';
import { User } from 'app/app/models/user';
import { UserService } from 'app/app/services/user.service';
import { ActivatedRoute } from '@angular/router';
import { Game } from 'app/app/models/game';
import { forkJoin, Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-game-live',
  templateUrl: './game-live.component.html',
  styleUrls: ['./game-live.component.css']
})

export class GameLiveComponent implements OnInit, OnDestroy {
  user: User;
  game: Game;
  board_orientation: string = 'white';

  pick_id: number | null;
  drop_id: number | null;

  private ngUnsubscribe = new Subject<void>();

  constructor(
    private userService: UserService,
    public gameService: GameLiveService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.gameService.clearVariables()

    this.route.params.pipe(takeUntil(this.ngUnsubscribe))
    .subscribe(params => {
      forkJoin({
        user: this.userService.getUser(),
        game: this.gameService.getGame(params['id']) 
      }).pipe(takeUntil(this.ngUnsubscribe))
      .subscribe({
        next: value => {
          this.user = value.user;
          Emitters.usernameEmitter.emit(this.user.username);
          this.game = value.game;
          this.setBoardOrientation();
        },
        error: err => {
          Emitters.usernameEmitter.emit(null);
          console.log(err);
        }
      })
    })

    this.gameService.openWebSocket()
  }

  ngOnDestroy(): void {
    this.gameService.closeWebSocket()
    this.ngUnsubscribe.next()
    this.ngUnsubscribe.complete()
  }

  onPick(event: any) {
    this.pick_id = parseInt(event.event.target.id);
  }
 
  onDrop(event: any) {
    this.drop_id = parseInt(event.event.target.id);
    if((this.pick_id != null && this.drop_id != null) && (this.pick_id != this.drop_id) && (typeof this.pick_id == 'number' && typeof this.drop_id == 'number') && (!isNaN(this.pick_id) && !isNaN(this.drop_id))) {
      let msg = {
        "type": "move",
        "pick_id": this.pick_id,
        "drop_id": this.drop_id
      }
      this.gameService.sendMsg(msg)
    }
    this.drop_id = this.pick_id = null;
  }

  sendPromotionPick(piece_type: string) {
    let msg = {
      "type": "promotion",
      "piece_type": piece_type
    }
    this.gameService.sendMsg(msg);
    this.gameService.promoting = false;
  }

  sendDrawOffer() {
    let msg = {
      "type": "draw_offer"
    }
    this.gameService.sendMsg(msg);
    this.gameService.allow_draw_offer = false;
  }

  acceptDrawOffer() {
    let msg = {
      "type": "draw_accept"
    }
    this.gameService.sendMsg(msg);
    this.gameService.draw_offer_pending = false;
    this.gameService.allow_draw_offer = false;
  }

  rejectDrawOffer() {
    let msg = {
      "type": "draw_reject"
    }
    this.gameService.sendMsg(msg);
    this.gameService.draw_offer_pending = false;
    this.gameService.allow_draw_offer = true;
  }

  @HostListener("window:keydown", ['$event'])
  scrollGame(event: KeyboardEvent) {
    this.gameService.scrollGame(event);
  }

  getPlayer(color: string) {
    switch(color) {
      case 'white':
        return (this.game && this.game.player_white) ? this.game.player_white : null
      case 'black':
        return (this.game && this.game.player_black) ? this.game.player_black : null
      default:
        return null
    }
  }

  setBoardOrientation() {
    if (this.user.username == this.game.player_white) {
      this.board_orientation = 'white';
    }
    else if(this.user.username == this.game.player_black) {
      this.board_orientation = 'black';
    }
  }

  rotateBoard() {
    switch(this.board_orientation) {
      case 'black':
        this.board_orientation = 'white';
        break;
      case 'white':
        this.board_orientation = 'black';
        break;
    }
  }

  sendMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_request"
    }
    this.gameService.sendMsg(msg);
    this.gameService.allow_move_cancel_request = false;
  }

  acceptMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_accept"
    }
    this.gameService.sendMsg(msg);
    this.gameService.move_cancel_request_pending = false;
    this.gameService.allow_move_cancel_request = false;
  }

  rejectMoveCancelRequest() {
    let msg = {
      "type": "move_cancel_reject"
    }
    this.gameService.sendMsg(msg);
    this.gameService.move_cancel_request_pending = false;
    this.gameService.allow_move_cancel_request = true;
  }

  resign() {
    this.gameService.show_resign_button = false;
    this.gameService.show_resign_cancel_button = true;
    this.gameService.show_resign_confirm_button = true;
  }

  confirmResign() {
    let msg = {
      'type': 'resign'
    }
    this.gameService.sendMsg(msg);
    this.gameService.show_resign_button = false;
    this.gameService.show_resign_cancel_button = false;
    this.gameService.show_resign_confirm_button = false;
  }

  cancelResign() {
    this.gameService.show_resign_button = true;
    this.gameService.show_resign_cancel_button = false;
    this.gameService.show_resign_confirm_button = false;
  }

  sendRematch() {
    let msg = {
      'type': 'rematch'
    }
    this.gameService.sendMsg(msg)
    this.gameService.show_rematch_button = false;
  }

  acceptRematch() {
    let msg = {
      'type': 'rematch_accept'
    }
    this.gameService.sendMsg(msg)
    this.gameService.show_rematch_button = false;
    this.gameService.rematch_offer_pending = false;
  }

  rejectRematch() {
    let msg = {
      'type': 'rematch_reject'
    }
    this.gameService.sendMsg(msg)
    this.gameService.show_rematch_button = true;
    this.gameService.rematch_offer_pending = false;
  }
}
