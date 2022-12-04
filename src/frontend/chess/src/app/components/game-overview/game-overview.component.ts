import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GameOverviewService } from 'src/app/services/game-overview.service';
import { HostListener } from '@angular/core';
import { Game } from 'src/app/models/game';
import { UserService } from 'src/app/services/user.service';
import { User } from 'src/app/models/user';
import { Emitters } from 'src/app/emitters/emitters';

@Component({
  selector: 'app-game-overview',
  templateUrl: './game-overview.component.html',
  styleUrls: ['./game-overview.component.css']
})
export class GameOverviewComponent implements OnInit {
  game: Game;
  user: User;
  board_orientation: string = 'white';

  constructor(
    private userService: UserService,
    public gameService: GameOverviewService,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next:(res: any) => {
        this.user = res;
        Emitters.usernameEmitter.emit(this.user.username);
      },
      error:(err: any) => {
        Emitters.usernameEmitter.emit(null);
        console.log(err)
      }
    })

    this.route.params.subscribe(params => {
      this.gameService.getGame(params['id']).subscribe({
        next: game => {
          this.game = game;
          this.setBoardOrientation();
          this.gameService.clearVariables();
          this.gameService.setGame(this.game);
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

  getPlayer(color: string) {
    switch(color) {
      case 'white':
        return (this.game && this.game.player_white) ? this.game.player_white : null
      case 'black':
        return (this.game && this.game.player_black) ? this.game.player_black : null
      default:
        return null
    }
  }

  setBoardOrientation() {
    if (this.user.username == this.game.player_white) {
      this.board_orientation = 'white';
    }
    else if(this.user.username == this.game.player_black) {
      this.board_orientation = 'black';
    }
  }

  rotateBoard() {
    switch(this.board_orientation) {
      case 'black':
        this.board_orientation = 'white';
        break;
      case 'white':
        this.board_orientation = 'black';
        break;
    }
  }
}
