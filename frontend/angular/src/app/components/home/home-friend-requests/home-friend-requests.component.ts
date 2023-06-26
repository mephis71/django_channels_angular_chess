import { Component, Input, OnChanges, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { FriendRequest, IUser, User } from 'src/app/models/user';
import { InviteService } from 'src/app/services/game-invite.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'home-friend-requests',
  templateUrl: './home-friend-requests.component.html',
  styleUrls: ['./home-friend-requests.component.scss']
})
export class HomeFriendRequestsComponent implements OnInit, OnDestroy {
  @Input() friendRequests: FriendRequest[];

  inviteWsSubjectSub: Subscription;
  inviteWsSub: Subscription;

  constructor(
    private userService: UserService,
    private inviteService: InviteService
  ) {}

  ngOnInit(): void {
    this.inviteWsSubjectSub = this.inviteService.inviteWsObservableReady.subscribe({
      next: () => {
        this.inviteWsSub = this.getInviteWsSub();
      }
    })
  }

  ngOnDestroy(): void {
    const subs = [this.inviteWsSub, this.inviteWsSubjectSub]
    for(let sub of subs) {
      if(sub){
        sub.unsubscribe();
      }
    }
  }

  acceptFriendRequest(id: number): void {
    this.userService.acceptFriendRequest(id).subscribe({
      next: data => {
        const friendUsername = data.body.friend_username;
        this.inviteService.addNewFriend.next(friendUsername)
        if(data.body.is_online) {
          this.userService.setOnlineStatus.next({
            username: friendUsername,
            status: 'online'
          })
        }
        else {
          this.userService.setOnlineStatus.next({
            username: friendUsername,
            status: 'offline'
          })
        }
      }
    })
    this.friendRequests = this.friendRequests.filter(e => e.id != id);
  }

  rejectFriendRequest(id: number) {
    this.userService.rejectFriendRequest(id).subscribe()
    this.friendRequests = this.friendRequests.filter(e => e.id != id);
  }

  getInviteWsSub(): Subscription {
    return this.inviteService.inviteWsObservable.subscribe({
      next: data => {
        if(data.type == 'friend_request') {
          this.friendRequests.push(new FriendRequest(data.id, data.username));
        }
      }
    });
  }
}
