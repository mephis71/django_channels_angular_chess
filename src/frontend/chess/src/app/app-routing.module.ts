import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GameLiveComponent } from './components/game-live/game-live.component';
import { GameOverviewComponent } from './components/game-overview/game-overview.component';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { UserProfileComponent } from './components/user-profile/user-profile.component';

const routes: Routes = [
  {path: '', component:HomeComponent},
  {path: 'login', component:LoginComponent},
  {path: 'register', component:RegisterComponent},
  {path: 'game/:id', component:GameOverviewComponent},
  {path: 'game/live/:id', component:GameLiveComponent},
  {path: 'user/:username', component:UserProfileComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
