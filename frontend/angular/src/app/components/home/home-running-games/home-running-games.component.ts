import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Game } from 'src/app/models/game';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-running-games',
  templateUrl: './home-running-games.component.html',
  styleUrls: ['./home-running-games.component.scss']
})
export class HomeRunningGamesComponent implements OnInit{
  running_games: Game[];

  constructor(
    private gameService: GameService,
    private router: Router
  ) {
    
  }

  ngOnInit(): void {
    // this.gameService.getRunningGames().subscribe({
    //   next: val => {
    //     this.running_games = val;
    //   },
    //   error: err => {
    //   }
    // })
  }

  runningGames() {
    return this.running_games ? true : false
  }

  goToGame(game_id: number) {
    this.router.navigate([`/game/live/${game_id}`])
  }
  
}
