import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginInfo } from 'src/app/models/login-info';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loginInfo: LoginInfo

  usernameError = '';
  passwordError = '';
  nonFieldError = '';

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private userService: UserService,
  ) { }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      username: '',
      password: ''
    })
  }

  sendLoginForm(): void {
    this.loginInfo = this.loginForm.getRawValue();
    this.userService.login(this.loginInfo)
    .subscribe({
      next: () => {
        this.router.navigate(['/'])
      },
      error: err => {
        this.userService.refreshUser.next(null)
        this.clearErrors();
        for (const [k,v] of Object.entries(err.error)) {
          if (v instanceof Array) {
            if(k == 'username') {
              this.usernameError = v[0]
            }
            if(k == 'password') {
              this.passwordError = v[0]
            }
            if(k == 'non_field_errors') {
              this.nonFieldError = v[0]
            }
          }
        }
      }
    }) 
  }

  clearErrors(): void {
    this.usernameError = this.passwordError = this.nonFieldError = ''
  }
}
