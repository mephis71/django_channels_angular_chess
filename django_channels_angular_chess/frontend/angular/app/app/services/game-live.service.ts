import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Piece } from '../models/piece';
import { Game } from '../models/game';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class GameLiveService {
  ws: WebSocket;

  pieces: Piece[] = [];
  promotion_pieces: Piece[] = [];

  time_white: string;
  time_black: string;

  endgame_info: string;
  player_color: string;
  promoting: boolean;

  allow_draw_offer = true;
  draw_offer_pending = false;

  allow_move_cancel_request = true;
  move_cancel_request_pending = false;
  move_cancel_error: string;

  show_resign_button = true;
  show_resign_confirm_button = false;
  show_resign_cancel_button = false;

  show_rematch_button = true;
  rematch_offer_pending = false;
  
  game_positions: string[] = [];
  game_positions_iterator: number;

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  public openWebSocket() {
    let path = window.location.pathname
    
    this.ws = new WebSocket(`ws://0.0.0.0:8000${path}`)

    this.ws.onopen = (event) => {
    };

    this.ws.onmessage = (event) => {
      var data = JSON.parse(event.data)

      if(data.type != 'time') {
        console.log(data);
      }

      if(data.type == 'init') {
        this.game_positions = data.game_positions;
        this.game_positions_iterator = this.game_positions.length - 1;
        this.fenToPieces(this.game_positions[this.game_positions_iterator]);
        this.time_white = data.time_white;
        this.time_black = data.time_black;
        this.player_color = data.player_color;
      }

      if(data.type == 'move') {
        this.game_positions = data.game_positions;
        this.game_positions_iterator = this.game_positions.length - 1;
        this.fenToPieces(this.game_positions[this.game_positions_iterator]);
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

      if(data.type == 'promoting') {
        this.promoting = true;
        this.createPromotionPieces()
      }

      if(data.type == 'endgame') {
        this.game_positions = data.game_positions;
        this.game_positions_iterator = this.game_positions.length - 1;
        this.fenToPieces(this.game_positions[this.game_positions_iterator]);
        this.time_white = data.time_white;
        this.time_black = data.time_black;

        this.draw_offer_pending = false;
        this.allow_draw_offer = false;
        this.allow_move_cancel_request = false;
        this.move_cancel_request_pending = false;
        this.show_resign_button = false;
        this.show_resign_confirm_button = false;
        this.show_resign_cancel_button = false;
        
        if(data.game_result == 'blackwins') {
          this.endgame_info = 'Black wins by checkmate';
        }
        if(data.game_result == 'whitewins') {
          this.endgame_info = 'White wins by checkmate';
        }
        if(data.game_result == 'draw-stalemate') {
          this.endgame_info = 'Draw - stalemate';
        }
        if(data.game_result == 'draw-50m') {
          this.endgame_info = 'Draw - 50 moves rule';
        }
        if(data.game_result == 'draw-3r') {
          this.endgame_info = 'Draw - threefold repetition';
        }
        if(data.game_result == 'draw-mutual') {
          this.endgame_info = 'Draw - mutual agreement';
        }
        if(data.game_result == 'whitewins-oot') {
          this.endgame_info = 'White wins - out of time';
        }
        if(data.game_result == 'blackwins-oot') {
          this.endgame_info = 'Black wins - out of time';
        }
        if(data.game_result == 'blackwins-abandonment') {
          this.endgame_info = 'Black wins - White abandoned the game';
        }
        if(data.game_result == 'whitewins-abandonment') {
          this.endgame_info = 'White wins - Black abandoned the game';
        }
        if(data.game_result == 'whitewins-resignment') {
          this.endgame_info = 'White wins - Black resigned';
        }
        if(data.game_result == 'blackwins-resignment') {
          this.endgame_info = 'Black wins - White resigned';
        }
        if(data.game_result == 'draw-abandonment') {
          this.endgame_info = 'The game was abandoned';
        }
        
      }

      if(data.type == 'draw_offer') {
        this.allow_draw_offer = false;
        this.draw_offer_pending = true;
      }

      if(data.type == 'draw_reject') {
        this.allow_draw_offer = true;
        this.draw_offer_pending = false;
      }

      if(data.type == 'move_cancel_request') {
        this.allow_move_cancel_request = false;
        this.move_cancel_request_pending = true;
      }

      if(data.type == 'move_cancel_reject') {
        this.allow_move_cancel_request = true;
        this.move_cancel_request_pending = false;
      }

      if(data.type == 'move_cancel_accept') {
        this.allow_move_cancel_request = true;
        this.move_cancel_request_pending = false;
        this.game_positions = data.game_positions;
        this.game_positions_iterator = this.game_positions.length - 1;
        this.fenToPieces(this.game_positions[this.game_positions_iterator]);
        this.time_white = data.time_white;
        this.time_black = data.time_black;
      }

      if(data.type == 'move_cancel_error') {
        this.move_cancel_error = "You can't do that now";
        this.allow_move_cancel_request = true;
        this.move_cancel_request_pending = false;
      }

      if(data.type == 'rematch') {
        this.rematch_offer_pending = true;
      }

      if(data.type == 'rematch_accept') {
        this.clearVariables()
        this.router.navigate([`/game/live/${data.game_id}`])
        .then(() => {
          window.location.reload()
        })
        
      }

      if(data.type == 'rematch_reject') {
        this.show_rematch_button = true;
      }
    };

    this.ws.onclose = (event) => {
      if (event.code == 4000){
        this.show_rematch_button = false;
      }
    };
  }

  public closeWebSocket() {
    this.ws.close();
  }

  public sendMsg(msg: any) {
    this.ws.send(JSON.stringify(msg))
  }

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

  createPromotionPieces() {
    let piece_types = ['queen', 'rook', 'bishop', 'knight'];
    for(let i=0; i<4; i++) {
      this.promotion_pieces.push(new Piece(this.player_color, piece_types[i], false))
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
    }
  }

  getGame(id: number): Observable<Game>  {
    return this.http.get<Game>(
      `http://0.0.0.0:8000/api/game/${id}`,
      {withCredentials: true}
    )
  }

  clearVariables() {
    this.pieces = [];
    this.promotion_pieces = [];

    this.time_white = '';
    this.time_black = '';

    this.endgame_info = '';
    this.player_color = '';

    this.allow_draw_offer = true;
    this.draw_offer_pending = false;

    this.allow_move_cancel_request = true;
    this.move_cancel_request_pending = false;
    this.move_cancel_error = '';
    
    this.game_positions = [];

    this.show_resign_button = true;
    this.show_resign_confirm_button = false;
    this.show_resign_cancel_button = false;

    this.show_rematch_button = true;
    this.rematch_offer_pending = false;
  }
}
