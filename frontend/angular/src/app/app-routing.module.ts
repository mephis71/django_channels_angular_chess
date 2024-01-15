import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GameFreeBoardComponent } from './components/game/game-freeboard/game-freeboard.component';
import { GameComponent } from './components/game/game-live/game-live.component';
import { GameOverviewComponent } from './components/game/game-overview/game-overview.component';
import { GamePuzzleComponent } from './components/game/game-puzzle/game-puzzle.component';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { UserProfileComponent } from './components/user-profile/user-profile.component';

const routes: Routes = [
  {path: '', component:HomeComponent},
  {path: 'login', component:LoginComponent},
  {path: 'register', component:RegisterComponent},
  {path: 'game/:id', component:GameOverviewComponent},
  {path: 'game/live/:id', component:GameComponent},
  {path: 'game/puzzle/:id', component:GamePuzzleComponent},
  {path: 'user/:username', component:UserProfileComponent},
  {path: 'freeboard', component:GameFreeBoardComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
