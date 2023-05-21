import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Game } from 'src/app/models/game';
import { GameInvite } from 'src/app/models/game_invite';
import { User } from 'src/app/models/user';
import { GameInviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-invites',
  templateUrl: './home-game-invites.component.html',
  styleUrls: ['./home-game-invites.component.css']
})
export class HomeGameInvitesComponent implements OnInit, OnDestroy{
  @Input() user: User;

  inviteWsSub: Subscription;
  inviteWsSubjectSub: Subscription;

  invites: GameInvite[] = []

  constructor(
    private gameInviteService: GameInviteService,
    private router: Router,
    private gameService: GameService,
    private route: ActivatedRoute,
  ){}

  ngOnInit(): void {
    this.inviteWsSubjectSub = this.gameInviteService.inviteWsObservableReady.subscribe({
      next: () => {
        this.inviteWsSub = this.getInviteWsSub();
      }
    })

    let path = 'game/invite';
    this.gameInviteService.openInviteWebSocket(path);
  }

  ngOnDestroy(): void {
    this.gameInviteService.closeWebSocket();
    let subs = [this.inviteWsSub, this.inviteWsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  getInviteWsSub(): Subscription {
    return this.gameInviteService.inviteWsObservable.subscribe({
      next: data => {
        if(data.type == 'invite' && data.to_user == this.user.username) {
          if(!this.invites.some(e => e.from_user == data.from_user)) {
            this.invites.push(data);
          }
          else {
            this.invites = this.invites.filter(e => e.from_user != data.from_user)
            this.invites.push(data)
          }
        }
  
        if(data.type == 'invite_accept' && data.usernames.includes(this.user.username)) {
          this.router.navigate([`/game/live/${data.game_id}`]).then(() => {
            window.location.reload()
          })
        }
      }
    });
  }

  acceptGameInvite(invite: GameInvite) { 
    this.gameService.acceptGameInvite(invite).subscribe()
  }

  rejectGameInvite(invite: any) {
    this.invites = this.invites.filter(e => e.from_user != invite.from_user);
  }
}
