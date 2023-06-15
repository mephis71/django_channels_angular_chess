import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FreeBoardGameSettings } from 'src/app/models/freeboard-game';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-freeboard-settings',
  templateUrl: './home-freeboard-settings.component.html',
  styleUrls: ['./home-freeboard-settings.component.css']
})
export class HomeFreeboardSettingsComponent {
  freeboardFen: string;
  freeboardMessage = '';

  constructor(
    private gameService: GameService,
    private router: Router
  ) {}

  goToFreeBoard() {
    if(!this.freeboardFen) {
      this.freeboardFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    }
    
    const settings = new FreeBoardGameSettings(this.freeboardFen);

    this.gameService.createFreeBoardGame(settings).subscribe({
      next: res => {
        this.router.navigate([`/freeboard`])
      },
      error: err => {
        this.freeboardMessage = err.error.fen[0]
      }
    })
  }
}
