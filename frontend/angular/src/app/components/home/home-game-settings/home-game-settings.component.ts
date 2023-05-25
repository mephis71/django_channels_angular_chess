import { Component, Input, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { GameInvite, IGameInviteSettings } from 'src/app/models/ws-messages';
import { User } from 'src/app/models/user';
import { GameInviteService } from 'src/app/services/game-invite.service';
import { GameService } from 'src/app/services/game.service';

@Component({
  selector: 'home-game-settings',
  templateUrl: './home-game-settings.component.html',
  styleUrls: ['./home-game-settings.component.css']
})

export class HomeGameSettingsComponent implements OnInit {
  @Input() user: User;
  gameInviteSubjectSub: Subscription;

  colorChoice: string = 'random'
  white_player: string | null;
  black_player: string | null;
  randomColors: boolean
  minutes: number = 5;

  constructor(
    private gameService: GameService,
    private gameInviteService: GameInviteService
  ) {}

  ngOnInit(): void {
    this.gameInviteSubjectSub = this.gameService.sendGameInvite.subscribe({
      next: username => {
        this.sendGameInvite(username)
      }
    })
  }

  sendGameInvite(username: string) {
    switch(this.colorChoice) {
      case 'white':
        this.white_player = this.user.username;
        this.black_player = username;
        this.randomColors = false;
        break;

      case 'black':
        this.white_player = username;
        this.black_player = this.user.username;
        this.randomColors = false;
        break;

      case 'random':
        this.white_player, this.black_player = null;
        this.randomColors = true;
        break;
    }

    const settings: IGameInviteSettings = {
      white: this.white_player,
      black: this.black_player,
      random_colors: this.randomColors,
      duration: this.minutes
    }

    const invite = new GameInvite(this.user.username, username, settings)

    this.gameInviteService.sendGameInvite(invite);
  }
}