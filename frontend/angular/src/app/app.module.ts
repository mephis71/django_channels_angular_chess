import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RegisterComponent } from './components/register/register.component';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './components/home/home.component';
import { NavComponent } from './components/nav/nav.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { GameComponent } from './components/game/game-live/game-live.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { UserProfileComponent } from './components/user-profile/user-profile.component';
import { GameOverviewComponent } from './components/game/game-overview/game-overview.component';

import { MatSliderModule } from '@angular/material/slider'; 
import { MatRadioModule } from '@angular/material/radio';
import { MatButtonModule } from '@angular/material/button'
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSnackBarModule } from '@angular/material/snack-bar'; 

import { GameChatComponent } from './components/game/game-live/game-live-chat/game-live-chat.component';
import { GamePiecesComponent } from './components/game/game-live/game-live-pieces/game-live-pieces.component';
import { GamePromotionComponent } from './components/game/game-live/game-live-promotion/game-live-promotion.component';
import { GameEndgameComponent } from './components/game/game-live/game-live-endgame/game-live-endgame.component';
import { GameButtonsComponent } from './components/game/game-live/game-live-buttons/game-live-buttons.component';
import { GameRotateBoardButtonComponent } from './components/game/game-rotate-board-button/game-rotate-board-button.component';
import { GameTimersComponent } from './components/game/game-live/game-live-timers/game-live-timers.component';
import { GameOverviewTimersComponent } from './components/game/game-overview/game-overview-timers/game-overview-timers.component';
import { GameOverviewPiecesComponent } from './components/game/game-overview/game-overview-pieces/game-overview-pieces.component';
import { GameFreeBoardComponent } from './components/game/game-freeboard/game-freeboard.component';
import { GameFreeBoardPiecesComponent } from './components/game/game-freeboard/game-freeboard-pieces/game-freeboard-pieces.component';
import { GameFreeBoardPromotionComponent } from './components/game/game-freeboard/game-freeboard-promotion/game-freeboard-promotion.component';
import { GameFreeBoardEndgameComponent } from './components/game/game-freeboard/game-freeboard-endgame/game-freeboard-endgame.component';
import { GameStockfishComponent } from './components/game/game-stockfish/game-stockfish.component';
import { HomeFriendsComponent } from './components/home/home-friends/home-friends.component';
import { HomeGameSettingsComponent } from './components/home/home-game-settings/home-game-settings.component';
import { HomeFreeboardSettingsComponent } from './components/home/home-freeboard-settings/home-freeboard-settings.component';
import { HomeGameInvitesComponent } from './components/home/home-game-invites/home-game-invites.component';
import { HomeRunningGamesComponent } from './components/home/home-running-games/home-running-games.component';
import { HomeAddFriendComponent } from './components/home/home-add-friend/home-add-friend.component';
import { HomeFriendRequestsComponent } from './components/home/home-friend-requests/home-friend-requests.component';
import { OnlineStatusComponent } from './components/online-status/online-status.component';
import { GameCreatePuzzleButtonComponent } from './components/game/game-create-puzzle-button/game-create-puzzle-button.component';
import { GamePuzzleComponent } from './components/game/game-puzzle/game-puzzle.component';
import { GamePuzzlePiecesComponent } from './components/game/game-puzzle/game-puzzle-pieces/game-puzzle-pieces.component';
import { GamePuzzlePromotionComponent } from './components/game/game-puzzle/game-puzzle-promotion/game-puzzle-promotion.component';

@NgModule({
  declarations: [
    AppComponent,
    RegisterComponent,
    LoginComponent,
    HomeComponent,
    NavComponent,
    GameRotateBoardButtonComponent,
    UserProfileComponent,
    GameOverviewComponent,
    GameOverviewTimersComponent,
    GameOverviewPiecesComponent,
    GameComponent,
    GameChatComponent,
    GamePiecesComponent,
    GameEndgameComponent,
    GamePromotionComponent,
    GameButtonsComponent,
    GameTimersComponent,
    GameFreeBoardComponent,
    GameFreeBoardPiecesComponent,
    GameFreeBoardPromotionComponent,
    GameFreeBoardEndgameComponent,
    GameStockfishComponent,
    HomeFriendsComponent,
    HomeGameSettingsComponent,
    HomeFreeboardSettingsComponent,
    HomeGameInvitesComponent,
    HomeRunningGamesComponent,
    HomeAddFriendComponent,
    HomeFriendRequestsComponent,
    OnlineStatusComponent,
    GameCreatePuzzleButtonComponent,
    GamePuzzleComponent,
    GamePuzzlePiecesComponent,
    GamePuzzlePromotionComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    DragDropModule,
    MatSliderModule,
    MatRadioModule,
    MatButtonModule,
    MatToolbarModule,
    MatSnackBarModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
