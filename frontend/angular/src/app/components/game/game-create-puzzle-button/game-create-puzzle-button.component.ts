import { Component, OnInit } from '@angular/core';
import { GameService } from 'src/app/services/game.service';
import { PuzzleService } from 'src/app/services/puzzle.service';
import { Clipboard } from '@angular/cdk/clipboard';
import { MatSnackBar } from '@angular/material/snack-bar';
import { config } from 'rxjs';


@Component({
  selector: 'game-create-puzzle-button',
  templateUrl: './game-create-puzzle-button.component.html',
  styleUrls: ['./game-create-puzzle-button.component.scss']
})
export class GameCreatePuzzleButtonComponent implements OnInit {
  fen: string;

  constructor(
    private puzzleService: PuzzleService,
    private gameService: GameService,
    private clipboard: Clipboard,
    private _snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.gameService.passCurrentPosition.subscribe({
      next: currentPosition => {
        this.fen = currentPosition;
      }
    })
  }

  createPuzzle(): void {
    const settings = {
      'fen': this.fen,
    }
    this.puzzleService.createGamePuzzle(settings).subscribe({
      next: res => {
        const puzzleUrl = window.location.origin + res.body.url;
        this.clipboard.copy(puzzleUrl)
        this._snackBar.open('Puzzle link was copied to your clipboard.', undefined, {
          duration: 5000
        })
      }
    })
  }
}
