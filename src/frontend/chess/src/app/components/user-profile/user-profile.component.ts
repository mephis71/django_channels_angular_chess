import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Profile } from 'src/app/models/profile';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { Emitters } from 'src/app/emitters/emitters';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent implements OnInit {
  profile: Profile;
  user: User;

  constructor(
    private route: ActivatedRoute, 
    private userService: UserService
  ) { }

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next:(res: any) => {
        this.user = res;
        Emitters.usernameEmitter.emit(this.user.username);
      },
      error:(err: any) => {
        Emitters.usernameEmitter.emit(null);
        console.log(err)
      }
    })

    this.route.params.subscribe(params => {
      this.userService.getProfile(params['username']).subscribe({
        next: res => {
          this.profile = res;
          console.log(this.profile)
        },
        error: err => {
          console.log(err)
        }
      })
    })
  }

  getProfile() {
    return this.profile ? this.profile : null
  }
}

