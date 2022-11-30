import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GameOverviewService } from 'src/app/services/game-overview.service';
import { HostListener } from '@angular/core';
import { Game } from 'src/app/models/game';

@Component({
  selector: 'app-game-overview',
  templateUrl: './game-overview.component.html',
  styleUrls: ['./game-overview.component.css']
})
export class GameOverviewComponent implements OnInit {
  game: Game;

  constructor(
    public gameService: GameOverviewService,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.gameService.getGame(params['id']).subscribe({
        next: game => {
          this.game = game;
        },
        error: err => {
          console.log(err)
        }
      })
    })
  }

  @HostListener("window:keydown", ['$event'])
  scrollGame(event: KeyboardEvent) {
    this.gameService.scrollGame(event);
  }
}
