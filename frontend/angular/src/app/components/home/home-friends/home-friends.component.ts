import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { InviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'home-friends',
  templateUrl: './home-friends.component.html',
  styleUrls: ['./home-friends.component.css']
})
export class HomeFriendsComponent implements OnInit, OnDestroy {
  @Input() friends: string[];

  inviteWsSubjectSub: Subscription;
  inviteWsSub: Subscription;
  friendsOnlineStatusSub: Subscription;

  friendsOnlineStatus = new Map<string, string>();


  constructor(
    private userService: UserService,
    private gameService: GameService,
    private inviteService: InviteService
  ) {}

  ngOnInit(): void {
    this.friendsOnlineStatusSub = this.userService.friendsOnlineStatusSubject.subscribe({
      next: value => {
        this.friendsOnlineStatus = value;
      }
    })

    this.inviteWsSubjectSub = this.inviteService.inviteWsObservableReady.subscribe({
      next: () => {
        this.inviteWsSub = this.getInviteWsSub();
      }
    })

    this.inviteService.addNewFriend.subscribe({
      next: username => {
        this.friends.push(username)
      }
    })
  }

  ngOnDestroy(): void {
    const subs = [this.inviteWsSubjectSub, this.inviteWsSub, this.friendsOnlineStatusSub]
    for(let sub of subs) {
      if(sub){
        sub.unsubscribe();
      }
    }
  }

  removeFriend(friend_username: string) {
    this.userService.removeFriend(friend_username).subscribe();
    this.friends = this.friends.filter(e => e != friend_username);
  }

  sendGameInvite(username: string) {
    this.gameService.sendGameInvite.next(username)
  }

  getInviteWsSub(): Subscription {
    return this.inviteService.inviteWsObservable.subscribe({
      next: data => {
        if(data.type == 'add_friend') {
          this.friends.push(data.friend_username)
          
          if(data.is_online) {
            this.userService.setOnlineStatus.next({
              username: data.friend_username,
              status: 'online'
            })
          }
          else {
            this.userService.setOnlineStatus.next({
              username: data.friend_username,
              status: 'offline'
            })
          }
        }
        else if(data.type == 'remove_friend') {
          this.friends = this.friends.filter(username => username != data.friend_username);
        }
      }
    });
  }

}
