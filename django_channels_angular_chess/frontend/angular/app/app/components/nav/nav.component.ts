import { Component, OnDestroy, OnInit } from '@angular/core';
import { UserService } from 'app/app/services/user.service';
import { Emitters } from '../../emitters/emitters';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit, OnDestroy {
  username: string | null;

  private ngUnsubscribe = new Subject<void>();

  constructor(
    private userService: UserService
    ) { }

  ngOnInit(): void {
    Emitters.usernameEmitter.pipe(takeUntil(this.ngUnsubscribe)).subscribe(username => {
      this.username = username;
    })
  } 

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
  
  logout(): void {
    this.userService.logout().pipe(takeUntil(this.ngUnsubscribe))
    .subscribe({
      next: res => {
        if (res.status == 200) {
          this.username = null;
        }
      },
      error: err => {
        console.log(err)
      }
    })
  }

}