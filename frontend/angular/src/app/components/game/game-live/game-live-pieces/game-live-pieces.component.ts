import { Component, Input, OnInit, OnDestroy, AfterViewInit, numberAttribute } from '@angular/core';
import { Color } from 'src/app/enums/pieces';
import { Piece } from 'src/app/models/piece';
import { GameService } from 'src/app/services/game.service';
import { HostListener } from '@angular/core';
import { fenToPieces } from 'src/app/utils/utils';
import { Subscription } from 'rxjs';
import { MoveMessage } from 'src/app/models/ws-messages';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { Renderer2, ElementRef } from '@angular/core';
import { CssService } from 'src/app/services/css.service';

@Component({
  selector: 'game-live-pieces',
  templateUrl: './game-live-pieces.component.html',
  styleUrls: ['./../../css/game-pieces.scss']
})
export class GameLivePiecesComponent implements OnInit, OnDestroy, AfterViewInit {
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
    private renderer: Renderer2,
    private el: ElementRef,
    private cssService: CssService
  ) {}

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.broadcastBoardHeight();
    }, 400)
    this.renderer.listen(window, 'resize', event => {
      this.broadcastBoardHeight();
    })
  }

  broadcastBoardHeight(): void {
    this.cssService.boardHeightBroadcast.next(this.el.nativeElement.offsetHeight)
  }

  ngOnInit(): void {
    this.wsSubjectSub = this.gameService.gameWsObservableReady.subscribe({
      next: () => {
        this.gameWsSub = this.getGameWsSub();
      }
    })
  }

  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(['init', 'move', 'game_end', 'move_cancel_accept'].includes(data.type)) {
            this.gamePositions = data.game_positions;
            this.gamePositionsIterator = this.gamePositions.length - 1;
            this.pieces = fenToPieces(this.gamePositions[this.gamePositionsIterator]);
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

  onPick(event: MouseEvent | TouchEvent) {
    const pick_id = (event.target as HTMLInputElement)?.id;
    this.pick_id = pick_id ? parseInt(pick_id) : null;
  }
 
  onDrop(event: CdkDragDrop<any>) {
    const drop_id = document.elementFromPoint(event.dropPoint.x, event.dropPoint.y)?.id;
    this.drop_id = drop_id ? parseInt(drop_id) : null;
    if((
      typeof this.pick_id == 'number' && 
      typeof this.drop_id == 'number' && 
      !isNaN(this.pick_id) && !isNaN(this.drop_id) && 
      this.pick_id != this.drop_id 
      )) {
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
    }
  }
}
