import { Component, OnDestroy, OnInit } from '@angular/core';
import { FriendRequest, IUser, User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
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
      next:(user: IUser) => {
        this.user = new User(user);
        this.greetMessage = `Hi ${this.user.username}`;
        this.authenticated = true;
        this.userService.refreshUser.next(this.user)
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
