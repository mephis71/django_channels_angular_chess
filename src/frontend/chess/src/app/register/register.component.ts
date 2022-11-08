import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  form: FormGroup;

  username_error = '';
  password_error = '';
  email_error = '';

  constructor(
    private formBuilder: FormBuilder,
    private http: HttpClient,
    private router: Router
    ) { }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: '',
      email: '',
      password: ''
    })
  }
  submit(): void {
    this.http.post(
      'http://localhost:8000/api/user/register/',
      {user: this.form.getRawValue()},
      {observe: 'response'}
      )
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
