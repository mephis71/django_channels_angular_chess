import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { GameInvite } from 'src/app/models/ws-messages';
import { InviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-invites',
  templateUrl: './home-game-invites.component.html',
  styleUrls: ['./home-game-invites.component.css']
})
export class HomeGameInvitesComponent implements OnInit, OnDestroy{
  @Input() username: string;
  inviteWsSub: Subscription;
  inviteWsSubjectSub: Subscription;

  invites: GameInvite[] = []

  constructor(
    private inviteService: InviteService,
    private router: Router,
    private gameService: GameService,
  ){}

  ngOnInit(): void {
    this.inviteWsSubjectSub = this.inviteService.inviteWsObservableReady.subscribe({
      next: () => {
        this.inviteWsSub = this.getInviteWsSub();
      }
    })

    const path = 'invites';
    this.inviteService.openInviteWebSocket(path);
  }

  ngOnDestroy(): void {
    this.inviteService.closeWebSocket();
    const subs = [this.inviteWsSub, this.inviteWsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  getInviteWsSub(): Subscription {
    return this.inviteService.inviteWsObservable.subscribe({
      next: data => {
        if(data.type == 'game_invite') {
          // if there is no invite from that user, add it
          if(!this.invites.some(e => e.from_user == data.from_user)) {
            this.invites.push(data);
          }
          // if there is, switch it with the incoming one (e.g. different settings)
          else {
            this.invites = this.invites.filter(e => e.from_user != data.from_user)
            this.invites.push(data)
          }
        }
  
        else if(data.type == 'game_invite_accept') {
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

  rejectGameInvite(invite: GameInvite) {
    this.invites = this.invites.filter(e => e.from_user != invite.from_user);
  }
}
