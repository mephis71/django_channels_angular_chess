import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { Color } from 'src/app/enums/pieces';
import { Piece } from 'src/app/models/piece';
import { GameService } from 'src/app/services/game.service';
import { HostListener } from '@angular/core';
import { fenToPieces } from 'src/app/utils/utils';
import { Subscription } from 'rxjs';

@Component({
  selector: 'game-live-pieces',
  templateUrl: './game-live-pieces.component.html',
  styleUrls: ['./../../css/game-pieces.css']
})
export class GameLivePiecesComponent implements OnInit, OnDestroy {
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
    private gameService: GameService
  ) {}

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
          if(['init', 'move', 'endgame', 'move_cancel_accept'].includes(data.type)) {
            this.gamePositions = data.game_positions;
            this.gamePositionsIterator = this.gamePositions.length - 1;
            this.pieces = fenToPieces(this.gamePositions[this.gamePositionsIterator]);
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
      this.gameService.sendGameMsg(msg)
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
