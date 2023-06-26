import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Game } from 'src/app/models/game';
import { GameService } from 'src/app/services/game.service';
import { StockfishService } from 'src/app/services/stockfish.service';

@Component({
  selector: 'game-stockfish',
  templateUrl: './game-stockfish.component.html',
  styleUrls: ['./game-stockfish.component.scss']
})
export class GameStockfishComponent implements OnInit{
  game: Game;
  showStockfish = true;
  stockfishEval: number;

  stockfishWsSub: Subscription;
  gameObjectSubjectSub: Subscription;
  stockfishWsSubjectSub: Subscription;

  constructor(
    private stockfishService: StockfishService,
    private gameService: GameService
  ) {}

  ngOnInit(): void {
    this.stockfishWsSubjectSub = this.stockfishService.stockfishWsObservableReady.subscribe({
      next: () => {
        this.stockfishWsSub = this.getStockfishWsSub()
      }
    })

    this.gameObjectSubjectSub = this.gameService.gameObjectReady.subscribe({
      next: game => {
        this.game = game;
        const path = `game/stockfish`
        this.stockfishService.openStockfishWebsocket(path, game);
        }
    })
  }


  ngOnDestroy(): void {
    this.stockfishService.closeStockfishWebSocket();
    const subs = [this.stockfishWsSub, this.gameObjectSubjectSub, this.stockfishWsSubjectSub]
    for(let sub of subs) {
      if (sub) {
        sub.unsubscribe()
      }
    }
  }

  getStockfishWsSub(): Subscription {
    return this.stockfishService.stockfishWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'stockfish_position') {
            this.stockfishEval = data.eval.value;
          }
        }
      }
    });
  }

  stockfishSwitch() {
    if (this.showStockfish == false) {
      this.showStockfish = true;
    }
    else {
      this.showStockfish = false;
    }
  }

  showStockfishEval(cp: number) {
    if(!cp) {
      return 0;
    }
    let p = String(cp / 100);
    if (Number(p) > 0) {
      p = '+' + p;
    }
    return p;
  }
}
