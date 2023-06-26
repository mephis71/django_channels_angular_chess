import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { RegisterInfo } from 'src/app/models/register-info';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  registerInfo: RegisterInfo

  usernameError = '';
  passwordError = '';
  emailError = '';

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserService,
    private router: Router
    ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      username: '',
      email: '',
      password: ''
    })
  }
  
  sendRegisterInfo(): void {
    this.registerInfo = this.registerForm.getRawValue()
    this.userService.register(this.registerInfo)
    .subscribe({
      next: () => {
        this.router.navigate(['/login'])
      },
      error: err => {
        this.clearErrors();
        for (const [k,v] of Object.entries(err.error)) {
          if (v instanceof Array) {
            if(k == 'username') {
              this.usernameError = v[0]
            }
            if(k == 'password') {
              this.passwordError = v[0]
            }
            if(k == 'email') {
              this.emailError = v[0]
            }
          }
        }
      }
    })
  }

  clearErrors(): void {
    this.usernameError = this.passwordError = this.emailError = ''
  }
}
