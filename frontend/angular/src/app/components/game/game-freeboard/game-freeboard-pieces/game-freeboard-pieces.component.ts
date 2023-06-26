import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { Color } from 'src/app/enums/pieces';
import { Piece } from 'src/app/models/piece';
import { HostListener } from '@angular/core';
import { fenToPieces } from 'src/app/utils/utils';
import { Subscription } from 'rxjs';
import { GameService } from 'src/app/services/game.service';
import { StockfishService } from 'src/app/services/stockfish.service';
import { MoveMessage, StockfishPositionMessage } from 'src/app/models/ws-messages';
import { CdkDragDrop, CdkDragStart } from '@angular/cdk/drag-drop';

@Component({
  selector: 'game-freeboard-pieces',
  templateUrl: './game-freeboard-pieces.component.html',
  styleUrls: ['./../../css/game-pieces.scss']
})
export class GameFreeBoardPiecesComponent implements OnInit, OnDestroy {
  public Color = Color;

  @Input() boardOrientation: Color;
  
  gameWsSub: Subscription;
  wsSubjectSub: Subscription;

  pick_id: number | null;
  drop_id: number | null;

  pieces: Piece[] = [];

  gamePositions: string[] = [];
  gamePositionsIterator: number;

  constructor(
    private gameService: GameService,
    private stockfishService: StockfishService
  ) {}

  ngOnInit(): void {
    this.wsSubjectSub = this.gameService.gameWsObservableReady.subscribe({
      next: () => {
        this.gameWsSub = this.getGameWsSub()
      }
    })
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(['init', 'move', 'endgame', 'move_cancel_accept', 'reset'].includes(data.type)) {
            this.gamePositions = data.game_positions;
            this.gamePositionsIterator = this.gamePositions.length - 1;
            this.pieces = fenToPieces(this.gamePositions[this.gamePositionsIterator]);
          }
          
          if(data.type == 'move') {
            const msg = new StockfishPositionMessage(data.game_positions[data.game_positions.length - 1])
            this.stockfishService.sendStockfishPositionMsg(msg)
          }
        }
      }
    });
  }
  

  ngOnDestroy(): void {
    const subs = [this.gameWsSub, this.wsSubjectSub]
    for(let sub of subs) {
      if (sub) {
        sub.unsubscribe()
      }
    }
  }

  onPick(event: MouseEvent | TouchEvent) {
    const pick_id = (event.target as HTMLInputElement)?.id;
    this.pick_id = pick_id ? parseInt(pick_id) : null;
  }
 
  onDrop(event: CdkDragDrop<any>) {
    const drop_id = document.elementFromPoint(event.dropPoint.x, event.dropPoint.y)?.id;
    this.drop_id = drop_id ? parseInt(drop_id) : null;
    if((this.pick_id !== null && this.drop_id !== null) && (this.pick_id != this.drop_id)) {
      const msg = new MoveMessage(this.pick_id, this.drop_id);
      this.gameService.sendGameMoveMsg(msg)
    }
    this.drop_id = this.pick_id = null;
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
      const msg = new StockfishPositionMessage(this.gamePositions[this.gamePositionsIterator]);
      this.stockfishService.sendStockfishPositionMsg(msg);
    }
  }
}
