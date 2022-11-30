import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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

  pick_id: number;
  drop_id: number;

  constructor(
    public gameService: GameLiveService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.gameService.getGame(params['id']).subscribe({
        next: game => {
          this.game = game;
        },
        error: err => {
          console.log(err)
        }
      })
    })
    
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
}
