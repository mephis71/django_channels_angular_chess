import { Component, OnInit, Input, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { Emitters } from 'src/app/emitters/emitters';
import { Game } from 'src/app/models/game';
import { Color } from 'src/app/enums/pieces';

@Component({
  selector: 'game-overview-timers',
  templateUrl: './../../templates/game-timers.html',
  styleUrls: ['./../../css/game-timers.css']
})
export class GameOverviewTimersComponent implements OnInit, OnDestroy, OnChanges {
  public Color = Color;
  @Input() boardOrientation: Color;
  @Input() game: Game;

  gamePositionsIteratorSub: Subscription;

  moveTimestamps: string[][] = [];

  timeWhite: string;
  timeBlack: string;
  
  constructor() { }

  ngOnInit(): void {
    this.gamePositionsIteratorSub = Emitters.gamePositionsIteratorEmitter
    .subscribe(gamePositionsIterator => {
      this.setTimers(this.moveTimestamps[gamePositionsIterator])
    })
  }

  ngOnChanges(): void {
    if(this.game) {
      this.moveTimestamps = this.game.move_timestamps;
      this.setTimers(this.moveTimestamps[this.moveTimestamps.length - 1])
    }
  }

  ngOnDestroy(): void {
    let subs = [this.gamePositionsIteratorSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  setTimers(moveTimestamp: any) {
    this.timeWhite = moveTimestamp[0]
    this.timeBlack = moveTimestamp[1]
  }

  getPlayer(color: Color) {
    switch(color) {
      case Color.WHITE:
        return (this.game && this.game.player_white) ? this.game.player_white : null
      case Color.BLACK:
        return (this.game && this.game.player_black) ? this.game.player_black : null
      default:
        return null
    }
  }
}
