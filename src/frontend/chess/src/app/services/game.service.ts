import { Injectable } from '@angular/core';
import { Piece } from '../models/piece';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  ws: WebSocket;
  pieces: Piece[] = []
  time_white: string;
  time_black: string;

  constructor() { }

  public openWebSocket() {
    let path = window.location.pathname
    this.ws = new WebSocket(`ws://localhost:8000${path}`)

    this.ws.onopen = (event) => {
      console.log('open:', event);
    };

    this.ws.onmessage = (event) => {
      var data = JSON.parse(event.data)
      console.log(data)

      if(data.type == 'init') {
        this.fenToPieces(data.fen);
        this.time_white = data.time_white;
        this.time_black = data.time_black;
      }

      if(data.type == 'move') {
        this.fenToPieces(data.fen);
        this.time_white = data.time_white;
        this.time_black = data.time_black;
      }
      
      if(data.type == 'time') {
        if(data.color == 'white') {
          this.time_white = data.time;
        }
        if(data.color == 'black') {
          this.time_black = data.time;
        }
      }
    };

    this.ws.onclose = (event) => {
      console.log('close:', event);
    };
  }

  public closeWebSocket() {
    this.ws.close();
  }

  public sendMsg(msg: any) {
    this.ws.send(msg)
  }

  private fenToPieces(fen: string) {
    this.pieces = [];
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8];

    var fen_split = fen.split(" ");
    var fen_position = fen_split[0];

    for (var i = 0; i < fen_position.length; i++) {
      var letter = fen[i];

      if (letter == "/") {
        continue;
      }

      if (numbers.includes(Number(letter))) {
        for (let i = 0; i < Number(letter); i++) {
          this.pieces.push(new Piece('', '', true))
        }
        continue;
      }

      var color = String();
      var type = String();

      switch (letter) {
        case "p":
          color = "black";
          type = "pawn";
          break;
        case "n":
          color = "black";
          type = "knight";
          break;
        case "b":
          color = "black";
          type = "bishop";
          break;
        case "r":
          color = "black";
          type = "rook";
          break;
        case "k":
          color = "black";
          type = "king";
          break;
        case "q":
          color = "black";
          type = "queen";
          break;
        case "P":
          color = "white";
          type = "pawn";
          break;
        case "N":
          color = "white";
          type = "knight";
          break;
        case "B":
          color = "white";
          type = "bishop";
          break;
        case "R":
          color = "white";
          type = "rook";
          break;
        case "K":
          color = "white";
          type = "king";
          break;
        case "Q":
          color = "white";
          type = "queen";
          break;
      }
      this.pieces.push(new Piece(color, type, false));
    }
  }
}
