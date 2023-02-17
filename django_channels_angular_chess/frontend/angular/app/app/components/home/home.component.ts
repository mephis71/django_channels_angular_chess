import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { User } from 'app/app/models/user';
import { UserService } from 'app/app/services/user.service';
import { Emitters } from '../../emitters/emitters';
import { GameInviteService } from '../../services/game-invite.service';
import { GameInvite } from 'app/app/models/game_invite';
import { takeUntil, Subject, switchMap } from 'rxjs';
import { Game } from 'app/app/models/game';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {
  friend_request_form: FormGroup;
  authenticated = false;
  user: User;

  friend_request_message = '';
  greet_message = 'You are not logged in';

  minutes: number = 5;
  color: string = 'random';

  running_games: Game[];

  private ngUnsubscribe = new Subject<void>();

  constructor(
    private userService: UserService,
    public gameInviteService: GameInviteService,
    private formBuilder: FormBuilder,
    private router: Router,
  ) { }
  

  ngOnInit(): void {
    this.userService.getUser().pipe(takeUntil(this.ngUnsubscribe)).subscribe({
      next:(res: any) => {
        this.user = res;
        this.greet_message = `Hi ${this.user.username}`;
        this.gameInviteService.clearVariables()
        this.gameInviteService.username = this.user.username;
        this.authenticated = true;
        Emitters.usernameEmitter.emit(this.user.username);
      },
      error:(err: any) => {
        Emitters.usernameEmitter.emit(null);
        console.log(err)
        this.greet_message = 'You are not logged in';
        this.authenticated = false;
      }
    })

    this.userService.getRunningGames().pipe(takeUntil(this.ngUnsubscribe)).subscribe({
      next: val => {
        console.log(val)
        this.running_games = val;
      },
      error: err => {
        console.log(err)
      }
    })

    this.friend_request_form = this.formBuilder.group({
      to_username: ''
    })

    this.gameInviteService.openWebSocket();
  }

  ngOnDestroy(): void {
    this.gameInviteService.closeWebSocket();
    this.ngUnsubscribe.next()
    this.ngUnsubscribe.complete()
  }

  submit(): any {
    this.userService.sendFriendRequest(this.friend_request_form).pipe(takeUntil(this.ngUnsubscribe))
    .subscribe({
      next: res => {
        if (res.status == 201) {
        this.friend_request_message = 'Friend request successfully sent';
        }
      },
      error: err => {
        if(err.status == 404) {
          this.friend_request_message = 'No user found'
        }
        if(err.status == 400) {
          this.friend_request_message = err.error.friend_request[0]
        }
      }
      })
  }

  acceptFriendRequest(id: number): any {
    this.userService.acceptFriendRequest(id).pipe(
      switchMap(() => this.userService.getUser()),
      takeUntil(this.ngUnsubscribe)
    ).subscribe({
      next: user => {
        this.user = user;
      },
      error: err => {
        console.log(err);
      }
    })
  }

  sendGameInvite(username: string) {
    let white, black, random_colors;

    switch(this.color) {
      case 'white':
        white = this.user.username;
        black = username;
        random_colors = false;
        break;

      case 'black':
        white = username;
        black = this.user.username;
        random_colors = false;
        break;

      case 'random':
        white = null;
        black = null;
        random_colors = true;
        break;
    }

    var invite = {
      "type": "invite",
      "from_user": this.user.username,
      "to_user": username,
      "settings": {
        "white": white,
        "black": black,
        "random_colors": random_colors,
        "duration": this.minutes
      }
    }
    this.gameInviteService.sendMsg(invite);
  }

  acceptGameInvite(invite: GameInvite) { 
    this.userService.acceptGameInvite(invite).pipe(takeUntil(this.ngUnsubscribe))
    .subscribe()
  }

  goToGame(game_id: number) {
    this.router.navigate([`/game/live/${game_id}`])
  }

  refreshUser() {
    this.userService.getUser().pipe(takeUntil(this.ngUnsubscribe))
    .subscribe({
      next: user => {
        this.user = user;
      },
      error: err => {
        console.log(err);
      }
    })
  }

  removeFriend(friend_username: any) {
    this.userService.removeFriend(friend_username).pipe(
      switchMap(() => this.userService.getUser()),
      takeUntil(this.ngUnsubscribe)
    ).subscribe({
      next: user => {
        this.user = user;
      },
      error: err => {
        console.log(err);
      }
    })

    this.userService.removeFriend(friend_username).pipe(takeUntil(this.ngUnsubscribe))
    .subscribe({
      next: res => {
        console.log(res);
      },
      error: err => {
        console.log(err);
      }
    })
  }

  rejectGameInvite(invite: any) {
    this.gameInviteService.invites = this.gameInviteService.invites.filter(e => e.from_user != invite.from_user);
  }

  rejectFriendRequest(friend_request_id: any) {
    this.userService.rejectFriendRequest(friend_request_id).pipe(
      switchMap(() => this.userService.getUser()),
      takeUntil(this.ngUnsubscribe)
    ).subscribe({
      next: user => {
        this.user = user;
      },
      error: err => {
        console.log(err);
      }
    })
  }  
}
