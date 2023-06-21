import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CssService {

  public boardHeightBroadcast = new Subject<number>();

  constructor() { }
}
