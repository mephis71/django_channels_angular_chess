import { Component, OnInit, OnDestroy, AfterViewInit, NgZone } from '@angular/core';
import { GameService } from 'src/app/services/game.service';
import { IUser, User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Game } from 'src/app/models/game';
import { Subscription, take } from 'rxjs';
import { Color } from 'src/app/enums/pieces';
import { GameInProgress } from 'src/app/models/game-in-progress';

@Component({
  selector: 'app-game-live',
  templateUrl: './game-live.component.html',
  styleUrls: ['./game-live.component.scss']
})

export class GameLiveComponent implements OnInit, OnDestroy {
  gameWsSub: Subscription;
  gameWsSubjectSub: Subscription
  gameError: string;
  
  user: User;
  game: GameInProgress;

  boardOrientation: Color;
  
  constructor(
    private userService: UserService,
    private gameService: GameService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

    
  ngOnInit(): void {
    this.gameWsSubjectSub = this.gameService.gameWsObservableReady.subscribe({
      next: () => {
        this.gameWsSub = this.getGameWsSub()
      }
    })

    this.userService.getUser().subscribe({
      next: (user: IUser) => {
        this.user = new User(user);
        this.userService.refreshUser.next(this.user);
        this.route.params.subscribe(params => {
          this.gameService.getGameInProgress(params['id']).subscribe({
            next: game => {
              this.setGame(game);
              // this.gameService.gameObjectReady.next(game);
              const path = `game_in_progress/${this.game.id}`
              this.gameService.openGameWebsocket(path);
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

  ngOnDestroy(): void {
    this.gameService.closeGameWebSocket();
    const subs = [this.gameWsSub, this.gameWsSubjectSub]
    for(let sub of subs) {
      if (sub) {
        sub.unsubscribe()
      }
    }
  }

  setGame(game: GameInProgress) {
    this.game = game;
    this.setBoardOrientation();
  }

  setBoardOrientation() {
    if (this.user.id == this.game.player_white_id) {
      this.boardOrientation = Color.WHITE;
    }
    else if(this.user.id == this.game.player_black_id) {
      this.boardOrientation = Color.BLACK;
    }
  }

  rotateBoard(color: Color) {
    this.boardOrientation = color;
  }
  
  getGameWsSub(): Subscription {
    return this.gameService.gameWsObservable.subscribe({
      next: data => {
        if('type' in data) {
          if(data.type == 'rematch_accept') {
            this.router.navigate([`/game/live/${data.game_id}`])
            .then(() => {
              window.location.reload()
            })
          }
        }
      }
    });
  }
}
