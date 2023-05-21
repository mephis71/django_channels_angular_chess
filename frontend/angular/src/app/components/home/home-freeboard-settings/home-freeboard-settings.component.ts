import { Component } from '@angular/core';
import { Router } from '@angular/router';
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
    let settings = {
      'fen': this.freeboardFen
    }
    if (!settings.fen) {
      settings.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    } 
    this.gameService.createFreeBoardGame(settings).subscribe({
      next: res => {
        this.router.navigate([`/freeboard/${res.id}`])
      },
      error: err => {
        this.freeboardMessage = err.error.fen[0]
      }
    })
  }
}
