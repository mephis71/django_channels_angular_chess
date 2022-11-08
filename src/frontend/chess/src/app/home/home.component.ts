import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Emitters } from '../emitters/emitters';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  form: FormGroup;
  
  friend_requests = []
  friends = []

  friend_request_message = '';
  greet_message = 'You are not logged in';
  friend_request_accept_message = ''

  no_friends = false;
  no_friend_requests = false;
  authenticated = false;

  constructor(
    private http: HttpClient,
    private formBuilder: FormBuilder
  ) { }

  ngOnInit(): void {
    this.http.get('http://localhost:8000/api/user', {withCredentials:true}).subscribe({
      next:(res: any) => {
        this.greet_message = `Hi ${res.username}`;
        this.friend_requests = res.friend_requests
        if (this.friend_requests.length === 0) {
          this.no_friend_requests = true;
        }
        this.friends = res.friends
        if (this.friends.length === 0) {
          this.no_friends = true;
        }
        Emitters.authEmitter.emit(true);
        this.authenticated = true;
        console.log(res)
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

  accept(id: number): any {
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
          this.friend_request_accept_message = 'Friend request accepted'
        }
      },
      error: err => {
        if(err.status == 404) {
          this.friend_request_accept_message = 'Friend request could not be found'
        }
      }
    })
  }
}
