import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from '../../emitters/emitters';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit {
  authenticated: boolean;
  username: string | null;

  constructor(
    private userService: UserService
    ) { }

  ngOnInit(): void {
    Emitters.authEmitter.subscribe(auth => {
      this.authenticated = auth;
    })

    Emitters.usernameEmitter.subscribe(username => {
      this.username = username;
      localStorage.setItem('username', username)
    })

    this.username = localStorage.getItem('username');
    if(this.username) {
      this.authenticated = true;
    }
    else {
      this.authenticated = false;
      this.username = null;
    }
  } 

  logout(): void {
    this.userService.logout()
    .subscribe({
      next: res => {
        if (res.status == 200) {
          localStorage.removeItem('username')
          this.authenticated = false;
          this.username = null;
        }
      },
      error: err => {
        console.log(err)
      }
    })
  }

}