import { Component } from '@angular/core';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'home-add-friend',
  templateUrl: './home-add-friend.component.html',
  styleUrls: ['./home-add-friend.component.css']
})
export class HomeAddFriendComponent {
  friendRequestMessage = '';
  friendRequestUsername: string;

  constructor(
    private userService: UserService
  ) { }

  sendFriendRequest(): void {
    this.userService.sendFriendRequest(this.friendRequestUsername).subscribe({
      next: res => {
        if (res.status == 200) {
        this.friendRequestMessage = 'Friend request successfully sent';
        }
      },
      error: err => {
        if(err.status == 404) {
          this.friendRequestMessage = 'No user found'
        }
        if(err.status == 400) {
          this.friendRequestMessage = err.error.friend_request[0]
        }
      }
      })
  }
}
