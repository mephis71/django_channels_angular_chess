import { Component, OnDestroy, OnInit } from '@angular/core';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from '../../emitters/emitters';
import { Color } from 'src/app/enums/pieces';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {
  authenticated = false;
  user: User;
  
  greetMessage = 'You are not logged in';

  constructor(
    private userService: UserService,
  ) { }
  
  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next:(user: User) => {
        this.user = user;
        this.greetMessage = `Hi ${this.user.username}`;
        this.authenticated = true;
        this.userService.refreshUser.next(user)
      },
      error:(err: any) => {
        this.userService.refreshUser.next(null)
        this.greetMessage = 'You are not logged in';
        this.authenticated = false;
      }
    })
  }

  ngOnDestroy(): void {
  }
}
