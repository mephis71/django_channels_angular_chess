import { Component, Input, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { User } from 'src/app/models/user';
import { GameService } from 'src/app/services/game.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'home-friends',
  templateUrl: './home-friends.component.html',
  styleUrls: ['./home-friends.component.css']
})
export class HomeFriendsComponent implements OnInit {
  @Input() user: User | null;
  friendRequestUsername: string;
  friendRequestMessage = '';
  

  refreshUserSubjectSub: Subscription;

  constructor(
    private userService: UserService,
    private gameService: GameService
  ) {}

  ngOnInit(): void {
    this.refreshUserSubjectSub = this.userService.refreshUser.subscribe({
      next: user => {
        this.user = user;
      }
    })
  }

  sendFriendRequest(): any {
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

  acceptFriendRequest(id: number): any {
    this.userService.acceptFriendRequest(id).subscribe(() => {
      this.refreshUser();
    })
  }

  rejectFriendRequest(friend_request_id: any) {
    this.userService.rejectFriendRequest(friend_request_id).subscribe(() => {
      this.refreshUser();
    })
  }

  refreshUser() {
    this.userService.getUser().subscribe(user => {
      this.userService.refreshUser.next(user)
    })
  }

  removeFriend(friend_username: any) {
    this.userService.removeFriend(friend_username).subscribe(() => {
      this.refreshUser();
    })
  }

  sendGameInvite(username: string) {
    this.gameService.sendGameInvite.next(username)
  }
}
