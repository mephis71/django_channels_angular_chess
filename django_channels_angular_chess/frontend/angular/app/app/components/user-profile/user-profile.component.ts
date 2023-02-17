import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Profile } from 'app/app/models/profile';
import { User } from 'app/app/models/user';
import { UserService } from 'app/app/services/user.service';
import { Emitters } from 'app/app/emitters/emitters';
import { forkJoin, Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent implements OnInit, OnDestroy {
  profile: Profile;
  user: User;

  private ngUnsubscribe = new Subject<void>();

  constructor(
    private route: ActivatedRoute, 
    private userService: UserService
  ) { }

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.ngUnsubscribe)).subscribe(params => {
      forkJoin({
        user: this.userService.getUser(),
        profile: this.userService.getProfile(params['username'])
      }).pipe(takeUntil(this.ngUnsubscribe))
      .subscribe({
        next: value => {
          this.user = value.user;
          this.profile = value.profile;
          Emitters.usernameEmitter.emit(this.user.username);
        },
        error: err => {
          Emitters.usernameEmitter.emit(null);
          console.log(err)
        }
      })
    })

  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  getProfile() {
    return this.profile ? this.profile : null
  }
}

