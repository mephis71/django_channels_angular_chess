import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Emitters } from '../emitters/emitters';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit {
  authenticated = false;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    Emitters.authEmitter.subscribe(
      (auth: boolean) => {
        this.authenticated = auth;
      }
    )
  } 

  logout(): void {
    this.http.post('http://localhost:8000/api/user/logout/',
    {},
    {
      withCredentials:true,
      observe: 'response'
    })
    .subscribe({
      next: res => {
        if (res.status == 200) {
          this.authenticated = false;
        }
      }
    })
  }

}