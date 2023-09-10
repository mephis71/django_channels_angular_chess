import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { GameInfo } from 'src/app/models/game-info';
import { GameInvite, GameInviteSettings } from 'src/app/models/ws-messages';
import { InviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-invites',
  templateUrl: './home-game-invites.component.html',
  styleUrls: ['./home-game-invites.component.scss']
})
export class HomeGameInvitesComponent implements OnInit, OnDestroy{
  @Input() userId: number;
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
          if(!this.invites.some(e => e.from_user_id == data.from_user_id)) {
            this.invites.push(data);
          }
          // if there is, switch it with the incoming one (e.g. different settings)
          else {
            this.invites = this.invites.filter(e => e.from_user_id != data.from_user_id)
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
    const players = [invite.from_user_id, invite.to_user_id]
    const settings = new GameInviteSettings(
      invite.settings.white_id, invite.settings.black_id, invite.settings.random_colors, invite.settings.duration
      )
    const gameInfo = new GameInfo(players, settings)
    this.gameService.acceptGameInvite(gameInfo).subscribe()
  }

  rejectGameInvite(invite: GameInvite) {
    this.invites = this.invites.filter(e => e.from_user_id != invite.from_user_id);
  }
}
