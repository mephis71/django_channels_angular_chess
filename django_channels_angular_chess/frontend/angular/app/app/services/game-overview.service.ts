import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Piece } from '../models/piece';
import { Game } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class GameOverviewService {
  pieces: Piece[] = [];

  time_white: string;
  time_black: string;
  
  game_positions: string[] = [];
  move_timestamps: string[] = [];
  game_positions_iterator: number;

  constructor(
    private http: HttpClient
  ) { }

  fenToPieces(fen: string) {
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

  scrollGame(event: KeyboardEvent) {
    let scrolling = false;

    switch(event.key) {
      case 'ArrowDown': {
        this.game_positions_iterator = 0;
        scrolling = true;
        break;
      }
      case 'ArrowUp': {
        this.game_positions_iterator = this.game_positions.length - 1;
        scrolling = true;
        break;
      }
      case 'ArrowLeft': {
        if(this.game_positions_iterator != 0) {
          this.game_positions_iterator -= 1;
          scrolling = true;
        }
        break;
      }
      case 'ArrowRight': {
        if(this.game_positions_iterator != this.game_positions.length - 1) {
          this.game_positions_iterator += 1;
          scrolling = true;
        }
        break;
      }
    }
    
    if(scrolling) {
      this.fenToPieces(this.game_positions[this.game_positions_iterator]);
      this.setTimers(this.move_timestamps[this.game_positions_iterator])
    }
  }

  getGame(id: number): Observable<Game> {
    return this.http.get<Game>(
      `http://localhost:8000/api/game/${id}`,
      {withCredentials: true}
    )
  }

  setGame(game: any) {
    this.game_positions = game.game_positions;
    this.move_timestamps = game.move_timestamps;
    this.game_positions_iterator = this.game_positions.length - 1;
    this.fenToPieces(this.game_positions[this.game_positions_iterator]);
    this.setTimers(this.move_timestamps[this.game_positions_iterator])
  }

  setTimers(pair: any) {
    this.time_white = pair[0]
    this.time_black = pair[1]
  }

  clearVariables() {
    this.pieces = [];

    this.time_white = '';
    this.time_black = '';
    
    this.game_positions = [];
    this.move_timestamps = [];
  }
}
