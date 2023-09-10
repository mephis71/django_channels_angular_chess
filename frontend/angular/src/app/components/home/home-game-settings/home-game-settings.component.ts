import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { User } from 'src/app/models/user';
import { GameInvite, GameInviteSettings } from 'src/app/models/ws-messages';
import { InviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-settings',
  templateUrl: './home-game-settings.component.html',
  styleUrls: ['./home-game-settings.component.scss']
})

export class HomeGameSettingsComponent implements OnInit, OnDestroy {
  @Input() user: User;
  gameInviteSubjectSub: Subscription;

  colorChoice: string = 'random'
  minutes: number = 5;

  constructor(
    private gameService: GameService,
    private inviteService: InviteService
  ) {}

  ngOnInit(): void {
    this.gameInviteSubjectSub = this.gameService.sendGameInvite.subscribe({
      next: opponent => {
        this.sendGameInvite(opponent)
      }
    })
  }

  ngOnDestroy(): void {
    const subs = [this.gameInviteSubjectSub]
    for(let sub of subs) {
      if(sub){
        sub.unsubscribe();
      }
    }
  }

  sendGameInvite(opponent: any) {
    let whitePlayerId: number | null = 0
    let blackPlayerId: number | null = 0
    let randomColors = false;

    switch(this.colorChoice) {
      case 'white':
        whitePlayerId = this.user.id;
        blackPlayerId = opponent.id;
        randomColors = false;
        break;

      case 'black':
        whitePlayerId = opponent.id;
        blackPlayerId = this.user.id;
        randomColors = false;
        break;

      case 'random':
        whitePlayerId = null;
        blackPlayerId = null;
        randomColors = true;
        break;
    }

    const settings = new GameInviteSettings(whitePlayerId, blackPlayerId, randomColors, this.minutes) 
    const invite = new GameInvite(this.user.id, this.user.username, opponent.id, opponent.username, settings)

    this.inviteService.sendGameInvite(invite);
  }
}