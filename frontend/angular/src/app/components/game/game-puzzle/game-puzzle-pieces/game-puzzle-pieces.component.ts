import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { Component, HostListener, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { Color } from 'src/app/enums/pieces';
import { Piece } from 'src/app/models/piece';
import { MoveMessage } from 'src/app/models/ws-messages';
import { PuzzleService } from 'src/app/services/puzzle.service';
import { fenToPieces } from 'src/app/utils/utils';

@Component({
  selector: 'game-puzzle-pieces',
  templateUrl: './game-puzzle-pieces.component.html',
  styleUrls: ['./../../css/game-pieces.scss']
})
export class GamePuzzlePiecesComponent implements OnInit, OnDestroy {
  public Color = Color;
  @Input() boardOrientation: Color;

  puzzleWsSub: Subscription;
  wsSubjectSub: Subscription;
  
  pick_id: number | null;
  drop_id: number | null;

  pieces: Piece[] = [];

  puzzlePositions: string[] = [];
  puzzlePositionsIterator: number;

  constructor(
    private puzzleService: PuzzleService,
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

  onPick(event: MouseEvent | TouchEvent) {
    const pick_id = (event.target as HTMLInputElement)?.id;
    this.pick_id = pick_id ? parseInt(pick_id) : null;
  }
 
  onDrop(event: CdkDragDrop<any>) {
    const drop_id = document.elementFromPoint(event.dropPoint.x, event.dropPoint.y)?.id;
    this.drop_id = drop_id ? parseInt(drop_id) : null;
    if((this.pick_id !== null && this.drop_id !== null) && (this.pick_id != this.drop_id)) {
      const msg = new MoveMessage(this.pick_id, this.drop_id);
      this.puzzleService.sendGameMoveMsg(msg)
    }
    this.drop_id = this.pick_id = null;
  }

  getPuzzleWsSub(): Subscription {
    return this.puzzleService.puzzleWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(['init', 'move'].includes(data.type)) {
            this.puzzlePositions.push(data.fen)
            this.puzzlePositionsIterator = this.puzzlePositions.length - 1;
            this.pieces = fenToPieces(this.puzzlePositions[this.puzzlePositionsIterator]);
          }
        }
      }
    });
  }

  @HostListener("window:keydown", ['$event'])
  scrollGame(event: KeyboardEvent) {
    let scrolling = false;

    if(event.key == 'ArrowDown') {
      if(this.puzzlePositionsIterator != 0) {
        this.puzzlePositionsIterator = 0;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowUp') {
      if(this.puzzlePositionsIterator != this.puzzlePositions.length - 1) {
        this.puzzlePositionsIterator = this.puzzlePositions.length - 1;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowLeft') {
      if(this.puzzlePositionsIterator != 0) {
        this.puzzlePositionsIterator -= 1;
        scrolling = true;
      }
    }

    else if(event.key == 'ArrowRight') {
      if(this.puzzlePositionsIterator != this.puzzlePositions.length - 1) {
        this.puzzlePositionsIterator += 1;
        scrolling = true;
      }
    }

    if(scrolling) {
      this.pieces = fenToPieces(this.puzzlePositions[this.puzzlePositionsIterator]);
    }
  }
}
