import { HttpClient } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Emitters } from '../emitters/emitters';
import { InviteService } from '../services/invite.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {
  form: FormGroup;
  
  friend_requests = [];
  friends = [];

  friend_request_message = '';
  greet_message = 'You are not logged in';
  friend_request_accept_message = '';

  authenticated = false;

  username: string;

  constructor(
    public wsService: InviteService,
    private http: HttpClient,
    private formBuilder: FormBuilder
  ) { }
  

  ngOnInit(): void {
    this.http.get('http://localhost:8000/api/user', {withCredentials:true}).subscribe({
      next:(res: any) => {
        this.greet_message = `Hi ${res.username}`;
        this.username = res.username;
        this.wsService.username = this.username;
        this.friend_requests = res.friend_requests;
        this.friends = res.friends;
        Emitters.authEmitter.emit(true);
        Emitters.usernameEmitter.emit(res.username);
        this.authenticated = true;
      },
      error:(err: any) => {
        this.greet_message = 'You are not logged in';
        Emitters.authEmitter.emit(false);
        this.authenticated = false;
      }
    })

    this.form = this.formBuilder.group({
      to_username: ''
    })

    this.wsService.openWebSocket();
  }

  ngOnDestroy(): void {
    this.wsService.closeWebSocket();
  }

  submit(): any {
    this.http.post(
      'http://localhost:8000/api/user/send_friend_request/',
      this.form.getRawValue(),
      {
        withCredentials: true,
        observe: 'response'
      }
      )
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
    this.http.post(
      `http://localhost:8000/api/user/accept_friend_request/${id}`,
      {},
      {
        withCredentials:true,
        observe: 'response'
      }
    )
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

  sendInvite(username: string) {
    var invite = {
      "type": "invite",
      "from": this.username,
      "to": username
    }
    this.wsService.sendMsg(JSON.stringify(invite));
  }

  acceptInvite(username: string) { 
    var invite_accept = {
      "p1": this.username,
      "p2": username 
    }
    this.http.post(
      'http://localhost:8000/api/game/invite_accept',
      {invite_accept},
      {withCredentials:true}
      ).subscribe()
  }
}
