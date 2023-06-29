import { Component } from '@angular/core';
import { Subscription } from 'rxjs';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-online-status',
  templateUrl: './online-status.component.html',
  styleUrls: ['./online-status.component.scss']
})

export class OnlineStatusComponent {
  userSub: Subscription;
  onlineStatusWsSub: Subscription;
  onlineStatusWsSubjectSub: Subscription;
  onlineStatusUpdateSub: Subscription;

  friendsOnlineStatus = new Map<string, string>();

  constructor(
    private userService: UserService
  ) {}

  ngOnInit(): void {
    
    this.onlineStatusWsSubjectSub = this.userService.onlineStatusWsObservableReady.subscribe({
      next: () => {
        this.onlineStatusWsSub = this.getOnlineStatusWsSub();
      }
    })

    this.onlineStatusUpdateSub = this.userService.setOnlineStatus.subscribe({
      next: data => {
        this.friendsOnlineStatus.set(data.username, data.status);
        this.userService.friendsOnlineStatusSubject.next(this.friendsOnlineStatus);
      }
    })


    this.userSub = this.userService.refreshUser.subscribe({
      next: user => {
        if(user) {
          this.userService.openStatusWebsocket()
        }
        else {
          this.userService.closeStatusWebSocket()
        }
      }
    })
  }

  getOnlineStatusWsSub(): Subscription {
    return this.userService.onlineStatusWsObservable.subscribe({
      next: data => {
        if(data.type == 'status') {
          this.friendsOnlineStatus.set(data.username, data.status)
        }
        else if(data.type == 'friends_online_status') {
          data.friends_online_status.forEach((friend: any) => {
            if(friend.is_online) {
              this.friendsOnlineStatus.set(friend.username, 'online')
            }
            else {
              this.friendsOnlineStatus.set(friend.username, 'offline')
            }
          });
        }

        this.userService.friendsOnlineStatusSubject.next(this.friendsOnlineStatus);
      }
    })
  }

  ngOnDestroy(): void {
    this.userService.closeStatusWebSocket()
    const subs = [this.userSub, this.onlineStatusUpdateSub, this.onlineStatusWsSubjectSub, this.onlineStatusWsSub]
    for(let sub of subs){
      if (sub) {
        sub.unsubscribe()
      }
    }
  }
}
