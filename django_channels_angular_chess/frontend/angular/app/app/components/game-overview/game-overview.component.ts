import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GameOverviewService } from 'app/app/services/game-overview.service';
import { HostListener } from '@angular/core';
import { Game } from 'app/app/models/game';
import { UserService } from 'app/app/services/user.service';
import { User } from 'app/app/models/user';
import { Emitters } from 'app/app/emitters/emitters';
import { forkJoin, Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-game-overview',
  templateUrl: './game-overview.component.html',
  styleUrls: ['./game-overview.component.css']
})
export class GameOverviewComponent implements OnInit, OnDestroy {
  game: Game;
  user: User;
  board_orientation: string = 'white';
  private ngUnsubscribe = new Subject<void>();

  constructor(
    private userService: UserService,
    public gameService: GameOverviewService,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.gameService.clearVariables();

    this.route.params.pipe(takeUntil(this.ngUnsubscribe)).subscribe(params => {
      forkJoin({
        user: this.userService.getUser(),
        game: this.gameService.getGame(params['id']) 
      }).pipe(takeUntil(this.ngUnsubscribe))
      .subscribe({
        next: value => {
          this.user = value.user;
          Emitters.usernameEmitter.emit(this.user.username);
          this.game = value.game;
          this.gameService.setGame(this.game);
          this.setBoardOrientation();
        },
        error: err => {
          Emitters.usernameEmitter.emit(null);
          console.log(err);
        }
      })
    })
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next()
    this.ngUnsubscribe.complete()
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
