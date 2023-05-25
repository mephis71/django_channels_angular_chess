import { Component, OnInit, Input, OnChanges, SimpleChanges, OnDestroy  } from '@angular/core';
import { Color } from 'src/app/enums/pieces';
import { fenToPieces } from 'src/app/utils/utils';
import { Piece } from 'src/app/models/piece';
import { GameService } from 'src/app/services/game.service';
import { HostListener } from '@angular/core';
import { Emitters } from 'src/app/emitters/emitters';
import { Game } from 'src/app/models/game';
import { Subscription } from 'rxjs';
import { StockfishService } from 'src/app/services/stockfish.service';
import { StockfishPositionMessage } from 'src/app/models/ws-messages';

@Component({
  selector: 'game-overview-pieces',
  templateUrl: './game-overview-pieces.component.html',
  styleUrls: ['./../../css/game-pieces.css']
})
export class GameOverviewPiecesComponent implements OnChanges {
  public Color = Color;
  
  @Input() boardOrientation: Color;
  @Input() game: Game;

  pieces: Piece[] = [];
  gamePositions: string[] = [];
  gamePositionsIterator: number;

  constructor(
    private stockfishService: StockfishService,
  ) { }

  ngOnChanges(): void {
    if(this.game) {
      this.gamePositions = this.game.game_positions;
      this.gamePositionsIterator = this.gamePositions.length - 1;
      this.pieces = fenToPieces(this.gamePositions[this.gamePositionsIterator])
    }
  }

  @HostListener("window:keydown", ['$event'])
  scrollGame(event: KeyboardEvent) {
    let scrolling = false;

    if(event.key == 'ArrowDown') {
      if(this.gamePositionsIterator != 0) {
        this.gamePositionsIterator = 0;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowUp') {
      if(this.gamePositionsIterator != this.gamePositions.length - 1) {
        this.gamePositionsIterator = this.gamePositions.length - 1;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowLeft') {
      if(this.gamePositionsIterator != 0) {
        this.gamePositionsIterator -= 1;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowRight') {
      if(this.gamePositionsIterator != this.gamePositions.length - 1) {
        this.gamePositionsIterator += 1;
        scrolling = true;
      }
    }

    if(scrolling) {
      this.pieces = fenToPieces(this.gamePositions[this.gamePositionsIterator]);
      Emitters.gamePositionsIteratorEmitter.emit(this.gamePositionsIterator);
      const msg = new StockfishPositionMessage(this.gamePositions[this.gamePositionsIterator]);
      this.stockfishService.sendStockfishPositionMsg(msg)
    }
  }
}
