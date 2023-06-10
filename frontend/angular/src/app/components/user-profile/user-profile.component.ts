import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Profile } from 'src/app/models/profile';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent implements OnInit {
  profile: Profile;
  user: User;

  profileError: string;

  constructor(
    private route: ActivatedRoute, 
    private userService: UserService
  ) { }

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next: user => {
        this.setUser(new User(user));
        this.userService.refreshUser.next(this.user);
        this.route.params.subscribe(params => {
          this.userService.getProfile(params['username']).subscribe({
            next: profile => {
              this.setProfile(profile);
              this.profileError = '';
            },
            error: err => {
              if(err.status == 404) {
                this.profileError = 'The profile was not found';
              }
            }
          })
        })
      },
      error: err => {
        this.userService.refreshUser.next(null);
      }
    })
  }

  getProfile() {
    return this.profile ? this.profile : null
  }

  setUser(user: User) {
    this.user = user;
  }

  setProfile(profile: Profile) {
    this.profile = profile;
  }
}

