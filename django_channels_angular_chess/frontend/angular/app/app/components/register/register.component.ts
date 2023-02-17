import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from 'app/app/services/user.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit, OnDestroy {
  form: FormGroup;

  username_error = '';
  password_error = '';
  email_error = '';

  private ngUnsubscribe = new Subject<void>();

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserService,
    private router: Router
    ) { }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: '',
      email: '',
      password: ''
    })
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
  
  submit(): void {
    this.userService.register(this.form.getRawValue()).pipe(takeUntil(this.ngUnsubscribe))
    .subscribe({
      next: () => {
        this.router.navigate(['/login'])
      },
      error: err => {
        this.username_error = this.password_error = this.email_error = ''
        for (const [k,v] of Object.entries(err.error)) {
          if (v instanceof Array) {
            if(k == 'username') {
              this.username_error = v[0]
            }
            if(k == 'password') {
              this.password_error = v[0]
            }
            if(k == 'email') {
              this.email_error = v[0]
            }
          }
        }
      }
    })
  }
}
