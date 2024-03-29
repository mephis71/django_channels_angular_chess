import { Component, OnInit, OnDestroy, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Subscription } from 'rxjs';
import { Color, PieceType } from 'src/app/enums/pieces';
import { GameService } from 'src/app/services/game.service';
import { Piece } from 'src/app/models/piece';
import { Game } from 'src/app/models/game';
import { PromotionPickMessage } from 'src/app/models/ws-messages';
import { GameInProgress } from 'src/app/models/game-in-progress';
import { User } from 'src/app/models/user';

@Component({
  selector: 'game-live-promotion',
  templateUrl: './../../templates/game-promotion.html',
  styleUrls: ['./../../css/game-promotion.scss']
})
export class GamePromotionComponent implements OnInit, OnDestroy, OnChanges {
  playerColor: Color;
  @Input() game: GameInProgress;
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
    if (this.game && this.user.id) {
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
    const subs = [this.gameWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  sendPromotionPick(pieceType: PieceType) {
    const msg = new PromotionPickMessage(pieceType);
    this.gameService.sendPromotionPickMsg(msg);
    this.promoting = false;
  }

  createPromotionPieces(): void {
    const piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT];
    for(let i=0; i<4; i++) {
      this.promotionPieces.push(new Piece(this.playerColor, piece_types[i], false))
    }
  }

  setPlayerColor() {
    if (this.user.id == this.game.player_white_id) {
      this.playerColor = Color.WHITE;
    }
    else if(this.user.id == this.game.player_black_id) {
      this.playerColor = Color.BLACK;
    }
  }
}
