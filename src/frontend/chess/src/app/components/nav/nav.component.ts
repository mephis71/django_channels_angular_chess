import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from '../../emitters/emitters';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit {
  username: string | null;

  constructor(
    private userService: UserService
    ) { }

  ngOnInit(): void {
    Emitters.usernameEmitter.subscribe(username => {
      this.username = username;
    })
  } 

  logout(): void {
    this.userService.logout()
    .subscribe({
      next: res => {
        if (res.status == 200) {
          this.username = null;
        }
      },
      error: err => {
        console.log(err)
      }
    })
  }

}