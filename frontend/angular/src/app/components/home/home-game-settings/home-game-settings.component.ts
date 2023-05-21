import { Component, Input, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
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

  minutes: number = 5;
  color_choice: string = 'random'

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
    let white, black, random_colors;
    switch(this.color_choice) {
      case 'white':
        white = this.user.username;
        black = username;
        random_colors = false;
        break;

      case 'black':
        white = username;
        black = this.user.username;
        random_colors = false;
        break;

      case 'random':
        white = null;
        black = null;
        random_colors = true;
        break;
    }
    var invite = {
      "type": "invite",
      "from_user": this.user.username,
      "to_user": username,
      "settings": {
        "white": white,
        "black": black,
        "random_colors": random_colors,
        "duration": this.minutes
      }
    }
    this.gameInviteService.sendMsg(invite);
  }

}
