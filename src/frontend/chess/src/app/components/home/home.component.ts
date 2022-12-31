import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from '../../emitters/emitters';
import { GameInviteService } from '../../services/game-invite.service';
import { GameInvite } from 'src/app/models/game_invite';

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
  friend_request_accept_message = '';

  minutes: number = 5;
  color: string = 'random';

  constructor(
    private userService: UserService,
    public gameInviteService: GameInviteService,
    private formBuilder: FormBuilder
  ) { }
  

  ngOnInit(): void {
    this.userService.getUser().subscribe({
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

    this.friend_request_form = this.formBuilder.group({
      to_username: ''
    })

    this.gameInviteService.openWebSocket();
  }

  ngOnDestroy(): void {
    this.gameInviteService.closeWebSocket();
  }

  submit(): any {
    this.userService.send_friend_request(this.friend_request_form)
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
    this.userService.accept_friend_request(id)
    .subscribe({
      next: res => {
        if(res.status == 202) {
          this.friend_request_accept_message = 'Friend request accepted';
        }
      },
      error: err => {
        if(err.status == 404) {
          this.friend_request_accept_message = 'Friend request could not be found';
        }
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
    this.gameInviteService.sendMsg(JSON.stringify(invite));
  }

  acceptGameInvite(invite: GameInvite) { 
    this.userService.accept_game_invite(invite)
    .subscribe()
  }
}
