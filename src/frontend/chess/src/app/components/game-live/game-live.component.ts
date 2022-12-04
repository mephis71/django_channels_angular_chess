import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { GameLiveService } from '../../services/game-live.service';
import { Emitters } from '../../emitters/emitters';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { ActivatedRoute } from '@angular/router';
import { Game } from 'src/app/models/game';

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
  

  constructor(
    private userService: UserService,
    public gameService: GameLiveService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next:(res: any) => {
        this.user = res;
        Emitters.usernameEmitter.emit(this.user.username);
      },
      error:(err: any) => {
        Emitters.usernameEmitter.emit(null);
        console.log(err)
      }
    })


    this.route.params.subscribe(params => {
      this.gameService.getGame(params['id']).subscribe({
        next: game => {
          this.game = game;
          this.setBoardOrientation();
        },
        error: err => {
          console.log(err)
        }
      })
    })
    this.gameService.clearVariables()
    this.gameService.openWebSocket()
  }

  ngOnDestroy(): void {
    this.gameService.closeWebSocket()
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
      this.gameService.sendMsg(JSON.stringify(msg))
    }
    this.drop_id = this.pick_id = null;
  }

  sendPromotionPick(piece_type: string) {
    let msg = {
      "type": "promotion",
      "piece_type": piece_type
    }
    this.gameService.sendMsg(JSON.stringify(msg));
    this.gameService.promoting = false;
  }

  sendDrawOffer() {
    let msg = {
      "type": "draw_offer"
    }
    this.gameService.sendMsg(JSON.stringify(msg));
    this.gameService.allow_draw_offer = false;
  }

  acceptDrawOffer() {
    let msg = {
      "type": "draw_accept"
    }
    this.gameService.sendMsg(JSON.stringify(msg));
    this.gameService.draw_offer_pending = false;

  }

  rejectDrawOffer() {
    let msg = {
      "type": "draw_reject"
    }
    this.gameService.sendMsg(JSON.stringify(msg));
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
}
