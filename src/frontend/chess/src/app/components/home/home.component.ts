import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from '../../emitters/emitters';
import { GameInviteService } from '../../services/game-invite.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {
  form: FormGroup;
  authenticated = false;
  user: User;

  friend_request_message = '';
  greet_message = 'You are not logged in';
  friend_request_accept_message = '';

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

    this.form = this.formBuilder.group({
      to_username: ''
    })

    this.gameInviteService.openWebSocket();
  }

  ngOnDestroy(): void {
    this.gameInviteService.closeWebSocket();
  }

  submit(): any {
    this.userService.send_friend_request(this.form)
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
    var invite = {
      "type": "invite",
      "from": this.user.username,
      "to": username
    }
    this.gameInviteService.sendMsg(JSON.stringify(invite));
  }

  acceptGameInvite(username: string) { 
    var invite_accept = {
      "p1": this.user.username,
      "p2": username 
    }
    this.userService.accept_game_invite(invite_accept)
    .subscribe()
  }
}
