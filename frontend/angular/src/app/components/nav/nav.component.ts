import { Component, OnDestroy, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user.service';
import { Subscription } from 'rxjs';
import { User } from 'src/app/models/user';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit, OnDestroy {
  user: User | null;
  userSub: Subscription;

  constructor(
    private userService: UserService
    ) { }

  ngOnInit(): void {
    this.userSub = this.userService.refreshUser.subscribe(user => {
      this.user = user;
    })
  } 

  ngOnDestroy(): void {
    let subs = [this.userSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }
  
  logout(): void {
    this.userService.logout().subscribe({
      next: res => {
        if (res.status == 200) {
          this.user = null;
          this.userService.refreshUser.next(null)
        }
      },
      error: err => {
      }
    })
  }
}