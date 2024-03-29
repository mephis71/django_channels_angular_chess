import { Component, OnInit, OnDestroy } from '@angular/core';
import { IUser, User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { Game } from 'src/app/models/game';
import { Color } from 'src/app/enums/pieces';
import { GameService } from 'src/app/services/game.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'game-freeboard',
  templateUrl: './game-freeboard.component.html',
  styleUrls: ['./game-freeboard.component.scss']
})

export class GameFreeBoardComponent implements OnInit, OnDestroy {
  user: User;
  game: Game;

  boardOrientation: Color;

  gameError: string;
  
  constructor(
    private userService: UserService,
    private gameService: GameService,
  ) {}

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next: (user: IUser) => {
        this.user = new User(user)
        this.userService.refreshUser.next(this.user);
        this.gameService.getFreeBoardGame().subscribe({
          next: game => {
            this.setGame(game);
            this.gameService.gameObjectReady.next(game);
            const path = `game/freeboard`
            this.gameService.openGameWebsocket(path);
            this.gameError = '';
          },
          error: err =>{
            if(err.status == 404) {
              this.gameError = 'The game was not found';
            }
          }
        })
      },
      error: err => {
          this.userService.refreshUser.next(null);
      }
    })

  }

  ngOnDestroy(): void {
    this.gameService.closeGameWebSocket();
  }

  setGame(game: Game) {
    this.game = game;
    this.setBoardOrientation();
  }

  setBoardOrientation() {
    this.boardOrientation = Color.WHITE;
  }

  rotateBoard(color: Color) {
    this.boardOrientation = color;
  }
}
