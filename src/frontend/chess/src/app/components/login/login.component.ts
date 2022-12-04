import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { Emitters } from 'src/app/emitters/emitters';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  form: FormGroup;
  
  username_error = '';
  password_error = '';
  non_field_error = '';

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private userService: UserService,
  ) { }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: '',
      password: ''
    })
  }

  submit(): any {
    this.userService.login(this.form.getRawValue())
    .subscribe({
      next: res => {
        Emitters.usernameEmitter.emit(res.body!.username);
        this.router.navigate(['/'])
      },
      error: err => {
        Emitters.usernameEmitter.emit(null)
        this.username_error = this.password_error = this.non_field_error = ''
        for (const [k,v] of Object.entries(err.error)) {
          if (v instanceof Array) {
            if(k == 'username') {
              this.username_error = v[0]
            }
            if(k == 'password') {
              this.password_error = v[0]
            }
            if(k == 'non_field_errors') {
              this.non_field_error = v[0]
            }
          }
        }
      }
    })
  }

}
