import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { GameInvite, IGameInviteSettings } from 'src/app/models/ws-messages';
import { InviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-settings',
  templateUrl: './home-game-settings.component.html',
  styleUrls: ['./home-game-settings.component.scss']
})

export class HomeGameSettingsComponent implements OnInit, OnDestroy {
  @Input() username: string;
  gameInviteSubjectSub: Subscription;

  colorChoice: string = 'random'
  whitePlayer: string | null;
  blackPlayer: string | null;
  randomColors: boolean
  minutes: number = 5;

  constructor(
    private gameService: GameService,
    private inviteService: InviteService
  ) {}

  ngOnInit(): void {
    this.gameInviteSubjectSub = this.gameService.sendGameInvite.subscribe({
      next: username => {
        this.sendGameInvite(username)
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

  sendGameInvite(username: string) {
    switch(this.colorChoice) {
      case 'white':
        this.whitePlayer = this.username;
        this.blackPlayer = username;
        this.randomColors = false;
        break;

      case 'black':
        this.whitePlayer = username;
        this.blackPlayer = this.username;
        this.randomColors = false;
        break;

      case 'random':
        this.whitePlayer, this.blackPlayer = null;
        this.randomColors = true;
        break;
    }

    const settings: IGameInviteSettings = {
      white: this.whitePlayer,
      black: this.blackPlayer,
      random_colors: this.randomColors,
      duration: this.minutes
    }

    const invite = new GameInvite(this.username, username, settings)

    this.inviteService.sendGameInvite(invite);
  }
}