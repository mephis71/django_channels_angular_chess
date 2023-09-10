import { Component, Input, OnChanges, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { Color, PieceType } from 'src/app/enums/pieces';
import { GamePuzzle } from 'src/app/models/game-puzzle';
import { Piece } from 'src/app/models/piece';
import { PromotionPickMessage } from 'src/app/models/ws-messages';
import { PuzzleService } from 'src/app/services/puzzle.service';

@Component({
  selector: 'game-puzzle-promotion',
  templateUrl: './../../templates/game-promotion.html',
  styleUrls: ['./../../css/game-promotion.scss']
})
export class GamePuzzlePromotionComponent implements OnInit, OnDestroy, OnChanges {
  @Input() puzzle: GamePuzzle;
  playerColor: Color;
  promoting: boolean = false;
  promotionPieces: Piece[] = [];
  puzzleWsSub: Subscription;
  wsSubjectSub: Subscription;

  constructor(
    private puzzleService: PuzzleService
  ) {}

  ngOnInit(): void {
    this.wsSubjectSub = this.puzzleService.puzzleWsObservableReady.subscribe({
      next: () => {
        this.puzzleWsSub = this.getPuzzleWsSub();
      }
    })
  }

  ngOnDestroy(): void {
    const subs = [this.puzzleWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  ngOnChanges(): void {
    if (this.puzzle) {
      this.setPlayerColor();
      this.createPromotionPieces();
    }
  }

  setPlayerColor(): void {
    this.playerColor = this.puzzle.playerColor == 'white' ? Color.WHITE : Color.BLACK
  }

  createPromotionPieces(): void {
    const piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT];
    for(let i=0; i<4; i++) {
      this.promotionPieces.push(new Piece(this.playerColor, piece_types[i], false))
    }
  }

  sendPromotionPick(pieceType: PieceType) {
    const msg = new PromotionPickMessage(pieceType);
    this.puzzleService.sendPromotionPickMsg(msg);
    this.promoting = false;
  }
  
  getPuzzleWsSub(): Subscription {
    return this.puzzleService.puzzleWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'promoting') {
            this.promoting = true;
          }
        }
      }
    });
  }
}
