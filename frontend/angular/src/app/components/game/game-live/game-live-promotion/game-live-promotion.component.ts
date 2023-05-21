import { Component, OnInit, OnDestroy, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Subscription } from 'rxjs';
import { Color, PieceType } from 'src/app/enums/pieces';
import { GameService } from 'src/app/services/game.service';
import { Piece } from 'src/app/models/piece';
import { Game } from 'src/app/models/game';
import { User } from 'src/app/models/user';

@Component({
  selector: 'game-live-promotion',
  templateUrl: './../../templates/game-promotion.html',
  styleUrls: ['./../../css/game-promotion.css']
})
export class GameLivePromotionComponent implements OnInit, OnDestroy, OnChanges {
  playerColor: Color;
  @Input() game: Game;
  @Input() user: User;

  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  promotionPieces: Piece[] = [];
  promoting: boolean;

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

  ngOnChanges(): void {
    if (this.game && this.user) {
      this.setPlayerColor()
      this.createPromotionPieces()
    }
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'promoting') {
            this.promoting = true;
          }
        }
      }
    });
  }

  ngOnDestroy(): void {
    let subs = [this.gameWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  sendPromotionPick(pieceType: PieceType) {
    let msg = {
      "type": "promotion",
      "piece_type": pieceType
    }
    this.gameService.sendGameMsg(msg);
    this.promoting = false;
  }

  createPromotionPieces(): void {
    let piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT];
    for(let i=0; i<4; i++) {
      this.promotionPieces.push(new Piece(this.playerColor, piece_types[i], false))
    }
  }

  setPlayerColor() {
    if (this.user.username == this.game.player_white) {
      this.playerColor = Color.WHITE;
    }
    else if(this.user.username == this.game.player_black) {
      this.playerColor = Color.BLACK;
    }
  }
}
