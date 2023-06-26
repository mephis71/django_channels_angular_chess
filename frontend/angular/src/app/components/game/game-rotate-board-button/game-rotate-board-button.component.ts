import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Color } from 'src/app/enums/pieces';

@Component({
  selector: 'game-rotate-board-button',
  templateUrl: './game-rotate-board-button.component.html',
  styleUrls: ['./game-rotate-board-button.component.scss']
})

export class GameRotateBoardButtonComponent implements OnInit {
  @Input() boardOrientation: Color;
  @Output() rotateBoardEvent = new EventEmitter<Color>();
  
  constructor() { }

  ngOnInit(): void {
  }

  rotateBoard() {
    if(this.boardOrientation == Color.WHITE) {
      this.rotateBoardEvent.emit(Color.BLACK);
    }
    else if(this.boardOrientation == Color.BLACK) {
      this.rotateBoardEvent.emit(Color.WHITE);
    }
  }
}
