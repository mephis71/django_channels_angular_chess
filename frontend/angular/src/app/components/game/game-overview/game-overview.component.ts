import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GameService } from 'src/app/services/game.service';
import { Game } from 'src/app/models/game';
import { UserService } from 'src/app/services/user.service';
import { IUser, User } from 'src/app/models/user';
import { Color } from 'src/app/enums/pieces';

@Component({
  selector: 'app-game-overview',
  templateUrl: './game-overview.component.html',
  styleUrls: ['./game-overview.component.css']
})
export class GameOverviewComponent implements OnInit {
  game: Game;
  user: User;

  boardOrientation: Color;

  gameError: string;

  constructor(
    private userService: UserService,
    private gameService: GameService,
    private route: ActivatedRoute,
  ) { }

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next: (user: IUser) => {
        this.user = new User(user)
        this.userService.refreshUser.next(this.user);
        this.route.params.subscribe(params => {
          this.gameService.getGame(params['id']).subscribe({
            next: game => {
              this.setGame(game);
              this.gameService.gameObjectReady.next(game);
              this.gameError = '';
            },
            error: err =>{
              if(err.status == 404) {
                this.gameError = 'The game was not found';
              }
            }
          })
        })
      },
      error: err => {
        this.userService.refreshUser.next(null);
      }
    })
  }

  setGame(game: Game) {
    this.game = game;
    this.setBoardOrientation();
  }

  setBoardOrientation() {
    if (this.user.username == this.game.player_white) {
      this.boardOrientation = Color.WHITE;
    }
    else if(this.user.username == this.game.player_black) {
      this.boardOrientation = Color.BLACK;
    }
  }

  rotateBoard(color: Color) {
    this.boardOrientation = color;
  }
}
