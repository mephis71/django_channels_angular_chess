import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Color } from 'src/app/enums/pieces';
import { GamePuzzle } from 'src/app/models/game-puzzle';
import { IUser, User } from 'src/app/models/user';
import { PuzzleService } from 'src/app/services/puzzle.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'src-game-puzzle',
  templateUrl: './game-puzzle.component.html',
  styleUrls: ['./game-puzzle.component.scss']
})
export class GamePuzzleComponent implements OnInit{
  puzzle: GamePuzzle;
  user: User;
  
  boardOrientation: Color;
  
  puzzleError: string = '';

  constructor(
    private userService: UserService,
    private route: ActivatedRoute,
    private puzzleService: PuzzleService
  ) {}

  ngOnInit(): void {
    this.userService.getUser().subscribe({
      next: (user: IUser) => {
        this.user = new User(user);
        this.userService.refreshUser.next(this.user);
        this.route.params.subscribe(params => {
          this.puzzleService.getGamePuzzle(params['id']).subscribe({
            next: puzzle => {
              this.setPuzzle(puzzle);
              this.puzzleService.puzzleObjectReady.next(puzzle);
              const path = `game/puzzle/${this.puzzle.id}`
              this.puzzleService.openGamePuzzleWebSocket(path);
              this.puzzleError = '';
            },
            error: err => {
              if(err.status == 404) {
                this.puzzleError = 'The puzzle was not found';
              }
            }
          })
        })
      },
      error: err => {
          this.userService.refreshUser.next(null);
      }
    })
  }

  ngOnDestroy(): void {
    this.puzzleService.closeGamePuzzleWebSocket();
  }

  rotateBoard(color: Color) {
    this.boardOrientation = color;
  }

  setPuzzle(puzzle: GamePuzzle) {
    this.puzzle = puzzle;
    this.setBoardOrientation();
  }
  
  setBoardOrientation() {
    this.boardOrientation = this.puzzle.playerColor == 'white' ? Color.WHITE : Color.BLACK
  }
}
