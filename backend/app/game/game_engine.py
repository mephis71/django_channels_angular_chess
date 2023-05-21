import re


class Piece:
    def __init__(self, color, type):
        self.color = color
        self.type = type

class GameEngine:
    def __init__(self, game_obj):
        self.fen = game_obj.fen
        self.game_positions = game_obj.get_game_positions()
        self.halfmoves = 0
        self.fullmoves = 0
        self.enpassant_sqr = '-'
        self.prev_p = None
        self.prev_t = None
        self.pieces = [None] * 64
        self.possible_moves = [False] * 64
        self.attacked_fields = [False] * 64
        self.init_game_with_fen(self.fen)
        self.update_pieces_with_fen(self.fen)

    def is_legal(self, p, t):
        # print('if the field is empty')
        if self.pieces[p] == None:
            return {
                'is_legal_flag': False,
                'game_result': False,
                'new_fen': None,
                'castles': None
            }

        # print("if wrong color of the piece")
        # if the moving piece is not the player's color
        if self.pieces[p].color != self.get_turn():
            return {
                'is_legal_flag': False,
                'game_result': False,
                'new_fen': None,
                'castles': None
            }

        # print('if the move is enpassant')
        # if the move is enpassant
        if self.prev_t != None and self.prev_p != None and self.pieces[self.prev_t] != None and self.pieces[self.prev_t].type == 'pawn' and self.pieces[p].type == 'pawn' and \
        abs(p - self.prev_t) == 1 and abs(self.prev_p - self.prev_t) == 16 and abs(self.prev_t - t) == 8:
            moving_pawn = self.pieces[p]
            captured_pawn = self.pieces[self.prev_t]

            self.pieces[t] = Piece(moving_pawn.color, moving_pawn.type)
            self.pieces[p]= None
            self.pieces[self.prev_t] = None

            if self.is_checked(moving_pawn.color) == True:
                self.pieces[p] = moving_pawn
                self.pieces[self.prev_t] = captured_pawn
                self.pieces[t] = None
                return {
                    'is_legal_flag': False,
                    'game_result': False,
                    'new_fen': None,
                    'castles': None
                }
            else:
                self.enpassant_sqr = '-'
                self.halfmoves = 0

                game_result, new_fen = self.end_move(p, t)
                return True, game_result, new_fen

        self.update_possible_moves(p)
        
        # print("if the move is against the moving pattern of the piece")
        # if the move is against the moving pattern of the piece return False
        if self.possible_moves[t] == False:
            return {
                'is_legal_flag': False,
                'game_result': False,
                'new_fen': None,
                'castles': None
            }

        # print("if the player is being checked after the move")
        # if the player is being checked after the move return False
        if self.is_checked_nextmove(p, t) == True:
            return {
                    'is_legal_flag': False,
                    'game_result': False,
                    'new_fen': None,
                    'castles': None
                }
    
        # if there's capture or pawn has been moved reset halfmoves else increment it
        castles = ''
        if self.pieces[t] != None or self.pieces[p].type == 'pawn':
            self.halfmoves = 0
        else:
            self.halfmoves += 1

        if self.pieces[t] != None and self.pieces[t].type == 'rook':
            if t == 0:
                castles += 'q'
            if t == 7:
                castles += 'k'
            if t == 56:
                castles += 'Q'
            if t == 63:
                castles += 'K'
        
        moving_piece = self.pieces[p]

        # save the pieces position so it can be restored later in case the player is being checked after castles (rare)
        origin_pieces = self.pieces.copy()
        origin_attacked_fields = self.attacked_fields.copy() # <- probably not necessary

        # if the move is castles
        if moving_piece.type == 'king' and abs(t - p) == 2:
            self.pieces[p] = None
            if t == 2:
                self.pieces[t] = Piece(moving_piece.color, 'king')
                self.pieces[0] = None
                self.pieces[3] = Piece(moving_piece.color, 'rook')
            elif t == 6:
                self.pieces[t] = Piece(moving_piece.color, 'king')
                self.pieces[7] = None
                self.pieces[5] = Piece(moving_piece.color, 'rook')
            elif t == 58:
                self.pieces[t] = Piece(moving_piece.color, 'king')
                self.pieces[56] = None
                self.pieces[59] = Piece(moving_piece.color, 'rook')
            elif t == 62:
                self.pieces[t] = Piece(moving_piece.color, 'king')
                self.pieces[63] = None
                self.pieces[61] = Piece(moving_piece.color, 'rook')


            # print('if the player is checked after castles')
            if self.is_checked(moving_piece.color) == True:
                self.pieces = origin_pieces
                self.attacked_fields = origin_attacked_fields # <- probably not necessary
                return {
                    'is_legal_flag': False,
                    'game_result': False,
                    'new_fen': None,
                    'castles': None
                }
            else:
                self.enpassant_sqr = '-'
                self.halfmoves += 1

                if self.get_turn() == 'white':
                    castles += 'QK'
                elif self.get_turn() == 'black':
                    castles += 'qk'

                game_result, new_fen = self.end_move(p, t, castles)
                return {
                    'is_legal_flag': True,
                    'game_result': game_result,
                    'new_fen': new_fen,
                    'castles': None
                }

        # print("at that point the move is legal")  
        # at that point the move is legal
        self.pieces[p] = None
        self.pieces[t] = Piece(moving_piece.color, moving_piece.type)
        
        # pawn promotion here
        if (t < 8 or t >= 56) and self.pieces[t].type == 'pawn':
            return {
                    'is_legal_flag': True,
                    'game_result': 'promoting',
                    'new_fen': None,
                    'castles': castles
                }
            
        if abs(t - p) == 16 and self.pieces[t].type == 'pawn':
            if self.get_turn() == 'white':
                self.enpassant_sqr = t + 8
            elif self.get_turn() == 'black':
                self.enpassant_sqr = t - 8
        else:
            self.enpassant_sqr = '-'
            
        if moving_piece.type == 'rook':
            if moving_piece.color == 'white':
                if p == 56:
                    castles += 'Q'
                elif p == 63:
                    castles += 'K'
            if moving_piece.color == 'black':
                if p == 0:
                    castles += 'q'
                elif p == 7:
                    castles += 'k'

        elif moving_piece.type == 'king':
            if moving_piece.color == 'white':
                castles += 'QK'
            elif moving_piece.color == 'black':
                castles += 'qk'
        game_result, new_fen = self.end_move(p, t, castles)

        return {
            'is_legal_flag': True,
            'game_result': game_result,
            'new_fen': new_fen,
            'castles': None
        }
    
    def init_game_with_fen(self, fen):
        fen_split = fen.split()
        fen_turn = fen_split[1]
        fen_enpassant = fen_split[3]
        fen_halfmoves = fen_split[4]
        fen_fullmoves = fen_split[5]
        
        self.fen = fen
    
        if fen_enpassant != '-':
            trgt = self.field_to_number[fen_enpassant]
            if fen_turn == 'w':
                self.prev_p = trgt - 8
                self.prev_t = trgt + 8
            if fen_turn == 'b':
                self.prev_p = trgt + 8
                self.prev_t = trgt - 8
        
        self.halfmoves = int(fen_halfmoves)
        self.fullmoves = int(fen_fullmoves)

    def update_pieces_with_fen(self, fen):
        fen_split = fen.split()
        fen_pieces = fen_split[0]
        fen_castles = fen_split[2]
        position = 0
        for letter in fen_pieces:
            if letter == '/':
                continue
            if re.match('[0-9]', letter):
                position += int(letter)
                continue
            if letter == 'p':
                self.pieces[position] = Piece('black', 'pawn')
            if letter == 'n':
                self.pieces[position] = Piece('black', 'knight')
            if letter == 'b':
                self.pieces[position] = Piece('black', 'bishop')
            if letter == 'r':
                self.pieces[position] = Piece('black', 'rook')
            if letter == 'q':
                self.pieces[position] = Piece('black', 'queen')
            if letter == 'k':
                self.pieces[position] = Piece('black', 'king')
            if letter == 'P':
                self.pieces[position] = Piece('white', 'pawn')
            if letter == 'N':
                self.pieces[position] = Piece('white', 'knight')
            if letter == 'B':
                self.pieces[position] = Piece('white', 'bishop')
            if letter == 'R':
                self.pieces[position] = Piece('white', 'rook')
            if letter == 'Q':
                self.pieces[position] = Piece('white', 'queen')
            if letter == 'K':
                self.pieces[position] = Piece('white', 'king')
            position += 1
        if fen_castles != '-':
            for letter in fen_castles:
                if letter == 'K':
                    self.pieces[60] = Piece('white', 'king')
                    self.pieces[63] = Piece('white', 'rook')
                if letter == 'Q':
                    self.pieces[60] = Piece('white', 'king')
                    self.pieces[56] = Piece('white', 'rook')
                if letter == 'q':
                    self.pieces[4] = Piece('black', 'king')
                    self.pieces[0] = Piece('black', 'rook')
                if letter == 'k':
                    self.pieces[4] = Piece('black', 'king')
                    self.pieces[7] = Piece('black', 'rook')
     
    def update_possible_moves(self, p):
        self.possible_moves = [False] * 64

        picked_type = self.pieces[p].type

        if picked_type == 'pawn':
            self.pawn_moves(p)
            
        elif picked_type == 'knight':
            self.knight_moves(p)
            
        elif picked_type == 'bishop':
            self.bishop_moves(p)
        
        elif picked_type == 'rook':
            self.rook_moves(p)

        elif picked_type == 'queen':
            self.queen_moves(p)
            
        elif picked_type == 'king':
            self.king_moves(p)

    def pawn_moves(self, p):
        c = self.pieces[p].color

        if c == 'white':
            # 1 field up
            if p - 8 >= 0 and self.pieces[p - 8] == None:
                self.possible_moves[p - 8] = True
                # 2 fields up
                if p - 16 >= 0 and (p >= 48 and p <= 55) and self.pieces[p - 16] == None:
                    self.possible_moves[p - 16] = True
            # diagonal up-left
            if p - 9 >= 0 and p % 8 != 0 and self.pieces[p - 9] != None and self.pieces[p - 9].color != c:
                self.possible_moves[p - 9] = True
            # diagonal up-right
            if p - 7 >= 0 and p % 8 != 7 and self.pieces[p - 7] != None and self.pieces[p - 7].color != c:
                self.possible_moves[p - 7] = True

        if c == 'black':
            # 1 field down
            if p + 8 < 64 and self.pieces[p + 8] == None:
                self.possible_moves[p + 8] = True
                # 2 fields down
                if p + 16 < 64 and (p >= 8 and p <= 15) and self.pieces[p + 16] == None:
                    self.possible_moves[p + 16] = True
            # diagonal down-right
            if p + 9 < 64 and p % 8 != 7 and self.pieces[p + 9] != None and self.pieces[p + 9].color != c:
                self.possible_moves[p + 9] = True
            # diagonal down-left
            if p + 7 < 64 and p % 8 != 0 and self.pieces[p + 7] != None and self.pieces[p + 7].color != c:
                self.possible_moves[p + 7] = True

    def knight_moves(self, p):
        c = self.pieces[p].color

        patterns = (-10, 6, -17, 15, -15, 17 ,-6, 10)
        start = 0
        end = 8
        if p % 8 == 0:
            start = 4
        if p % 8 == 1:
            start = 2
        if p % 8 == 6:
            end = 6
        if p % 8 == 7:
            end = 4
        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64 and (self.pieces[trgt] == None or self.pieces[trgt].color != c):
                self.possible_moves[trgt] = True
    
    def bishop_moves(self, p):
        c = self.pieces[p].color

        patterns = (9, 7, -9, -7)
        origin_p = p
        for i in range(4):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] < 0 or \
                p + patterns[i] > 63 or \
                (p % 8 == 0 and (patterns[i] == -9 or patterns[i] == 7)) or \
                (p % 8 == 7 and(patterns[i] == -7 or patterns[i] == 9)) or \
                (self.pieces[p + patterns[i]] != None and self.pieces[p + patterns[i]].color == c):
                    break
                if self.pieces[p + patterns[i]] != None and self.pieces[p + patterns[i]].color != c:
                    p += patterns[i]
                    self.possible_moves[p] = True
                    break
                p += patterns[i]
                self.possible_moves[p] = True

    def rook_moves(self, p):
        c = self.pieces[p].color

        patterns = (8, -8, 1, -1)
        origin_p = p
        for i in range(2):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] > 63 or p + patterns[i] < 0:
                    break
                if self.pieces[p + patterns[i]] != None:
                    if self.pieces[p + patterns[i]].color != c:
                        p += patterns[i]
                        self.possible_moves[p] = True
                        break
                    break
                p += patterns[i]
                self.possible_moves[p] = True

        for i in range(2, 4):
            p = origin_p
            while p >= 0 and p < 64:
                if (patterns[i] == -1 and p % 8 == 0) or (patterns[i] == 1 and p % 8 == 7):
                    break
                if self.pieces[p + patterns[i]] != None:
                    if self.pieces[p + patterns[i]].color != c:
                        p += patterns[i]
                        self.possible_moves[p] = True
                        break
                    break
                p += patterns[i]
                self.possible_moves[p] = True

    def queen_moves(self, p):
        self.rook_moves(p)
        self.bishop_moves(p)

    def king_moves(self, p):
        c = self.pieces[p].color
        start = 0
        end = 8
        patterns = (-9, -1, 7 , -8, 8, -7, 1, 9)
        if p % 8 == 0:
            start = 3
        if p % 8 == 7:
            end = 5
        
        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                if self.pieces[trgt] == None or self.pieces[trgt].color != c:
                    self.possible_moves[trgt] = True
        
        self.castles(p)

    def pawn_fields(self, p):
        c = self.pieces[p].color
        if c == 'white':
            if p - 9 >= 0 and p % 8 != 0:
                self.attacked_fields[p - 9] = True
            if p - 7 >= 0 and p % 8 != 7:
                self.attacked_fields[p - 7] = True
            
        if c == 'black':
            if p + 9 < 63 and p % 8 != 7:
                self.attacked_fields[p + 9] = True
            if p + 7 < 63 and p % 8 != 0:
                self.attacked_fields[p + 7] = True
    
    def knight_fields(self, p):
        patterns = (-10, 6, -17, 15, -15, 17, -6, 10)
        start = 0
        end = 8

        if p % 8 == 0:
            start = 4

        if p % 8 == 1:
            start = 2

        if p % 8 == 6:
            end = 6

        if p % 8 == 7:
            end = 4
        
        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                self.attacked_fields[trgt] = True

    def bishop_fields(self, p):
        patterns = (9, 7, -9, -7)
        c = self.pieces[p].color
        origin_p = p
        for i in range(4):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] < 0 or p + patterns[i] > 63 or \
                (p % 8 == 0 and (patterns[i] == -9 or patterns[i] == 7)) or \
                (p % 8 == 7 and (patterns[i] == -7 or patterns[i] == 9)):
                    break
                if self.pieces[p + patterns[i]] != None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

    def rook_fields(self, p):
        patterns = (8, -8, 1, -1)
        c = self.pieces[p].color
        origin_p = p
        for i in range(2):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] > 63 or p + patterns[i] < 0:
                    break
                if self.pieces[p + patterns[i]] != None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

        for i in range(2, 4):
            p = origin_p
            while p >= 0 and p < 64:
                if p + patterns[i] > 63 or p + patterns[i] < 0 or \
                (patterns[i] == -1 and p % 8 == 0) or \
                (patterns[i] == 1 and p % 8 == 7):
                    break
                if self.pieces[p + patterns[i]] != None:
                    p += patterns[i]
                    self.attacked_fields[p] = True
                    break
                p += patterns[i]
                self.attacked_fields[p] = True

    def queen_fields(self, p):
        self.rook_fields(p)
        self.bishop_fields(p)

    def king_fields(self, p):
        start = 0
        end = 8
        patterns = (-9, -1, 7, -8, 8, -7, 1, 9)

        if p % 8 == 0:
            start = 4
        if p % 8 == 7:
            end = 5
        for i in range(start, end):
            trgt = p + patterns[i]
            if trgt >= 0 and trgt < 64:
                self.attacked_fields[trgt] = True

    def update_attacked_fields(self, c):
        # 'color' argument is the color of the player by whom the fields are attacked by
        self.attacked_fields = [False] * 64
        for p in range(64):
            if self.pieces[p] != None and self.pieces[p].color == c:
                if self.pieces[p].type == 'pawn':
                    self.pawn_fields(p)
                elif self.pieces[p].type == 'knight':
                    self.knight_fields(p)
                elif self.pieces[p].type == 'bishop':
                    self.bishop_fields(p)
                elif self.pieces[p].type == 'rook':
                    self.rook_fields(p)
                elif self.pieces[p].type == 'queen':
                    self.queen_fields(p)
                elif self.pieces[p].type == 'king':
                    self.king_fields(p)

    def castles(self, p):
        c = self.pieces[p].color
        self.update_attacked_fields(self.opposite_color(self.get_turn()))
        if c == 'white':
            indexes_pieces = (57, 58, 59)
            indexes_fields = (58, 59)
            outcome_pieces = [self.pieces[i] for i in indexes_pieces]
            outcome_fields = [self.attacked_fields[i] for i in indexes_fields]

            if all(x == None for x in outcome_pieces) == True and \
            all(x == False for x in outcome_fields) == True and \
            self.pieces[56] != None and self.pieces[56].color == c:
                self.possible_moves[58] = True

            indexes = (61, 62)
            
            outcome_pieces = [self.pieces[i] for i in indexes]
            outcome_fields = [self.attacked_fields[i] for i in indexes]

            if all(x == None for x in outcome_pieces) == True and \
            all(x == False for x in outcome_fields) == True and \
            self.pieces[63] != None and self.pieces[63].color == c:
                self.possible_moves[62] = True

        if c == 'black':
            indexes_pieces = (1, 2, 3)
            indexes_fields = (2, 3)
            outcome_pieces = [self.pieces[i] for i in indexes_pieces]
            outcome_fields = [self.attacked_fields[i] for i in indexes_fields]

            if all(x == None for x in outcome_pieces) == True and \
            all(x == False for x in outcome_fields) == True and \
            self.pieces[0] != None and self.pieces[0].color == c:
                self.possible_moves[2] = True

            indexes = (5, 6)
            
            outcome_pieces = [self.pieces[i] for i in indexes]
            outcome_fields = [self.attacked_fields[i] for i in indexes]

            if all(x == None for x in outcome_pieces) == True and \
            all(x == False for x in outcome_fields) == True and \
            self.pieces[7] != None and self.pieces[7].color == c:
                self.possible_moves[6] = True
    
    def opposite_color(self, color):
        if color == 'white':
            return 'black'
        else:
            return 'white'

    def is_checked(self, color):
        # 'color' argument is color of the player that is being checked
        self.update_attacked_fields(self.opposite_color(color))
        type_list = [
            x.type if x is not None and x.color is color else None \
            for x in self.pieces
        ]
        king_position = type_list.index('king')
        if self.attacked_fields[king_position] == True:
            return True
        else:
            return False

    def is_checked_nextmove(self, p1, p2):
        # saving 'attacked_fields' list so it can be restored later because it's going to get changed in is_checked() function
        # same with 'self.pieces'

        origin_pieces = self.pieces.copy()
        origin_attacked_fields = self.attacked_fields.copy()

        moving_piece = self.pieces[p1]

        self.pieces[p2] = moving_piece
        self.pieces[p1] = None
        output = None

        if self.is_checked(moving_piece.color) == False:
            output = False
        else:
            output = True

        self.pieces = origin_pieces
        self.attacked_fields = origin_attacked_fields

        return output
    
    def update_fen(self, castles):
        output = ""
        empty_spaces = 0
        
        for i in range(64):
            if self.pieces[i] == None:
                empty_spaces += 1
            else:
                if empty_spaces != 0:
                    temp = str(empty_spaces)
                    output += temp
                    empty_spaces = 0

                
                c = self.pieces[i].color
                t = self.pieces[i].type
                key = str(c + t)
                output += self.fen_dict[key]
            
            if i % 8 == 7:
                if empty_spaces != 0:
                    output += str(empty_spaces)
                    empty_spaces = 0
                if i != 63:
                    output += '/'

        output += ' '

        if self.get_turn() == 'white':
            output += 'w'
        else:
            output += 'b'

        output += ' '

        fen_castles = self.fen.split()[2]
       
        if castles:
            fen_castles = [*fen_castles]

            for val in castles:
                if val in fen_castles:
                    fen_castles.remove(val)

            fen_castles = "".join(fen_castles)

        if not fen_castles:
            output += '- '
        else:
            output += fen_castles + ' '
        
        enpassant = '-'

        if self.enpassant_sqr != '-':
            enpassant = self.number_to_field[self.enpassant_sqr]
        
        output += enpassant + ' ' + str(self.halfmoves) + ' ' + str(self.fullmoves)
        return output

    def end_move(self, p, t, castles=None):
        if self.get_turn() == 'black':
            self.fullmoves += 1
        self.prev_p = p
        self.prev_t = t
        self.change_turn()
        self.fen = self.update_fen(castles)
        game_result = self.is_checkmated(self.get_turn())
        if game_result == False:
            if self.halfmoves == 50:
                return 'draw-50m', self.fen
            elif self.threefold_repetition():
                return 'draw-3r', self.fen  
        return game_result, self.fen
    
    def threefold_repetition(self):
        cut_fen = self.fen.split()
        cut_fen.pop(5)
        cut_fen.pop(4)
        cut_fen = " ".join(cut_fen)
        cut_game_positions = []
        for move in self.game_positions:
            cut_move = move.split()
            cut_move.pop(5)
            cut_move.pop(4)
            cut_move = " ".join(cut_move)
            cut_game_positions.append(cut_move)
        cut_game_positions.append(cut_fen)
        if cut_game_positions.count(cut_fen) > 2:
            return True
        else:
            return False
        
    def is_checkmated(self, c):
        # 'c' argument is the color of player who is being checkmated
        for i in range(64):
            if self.pieces[i] != None and self.pieces[i].color == c:
                self.update_possible_moves(i)
                for j in range(64):
                    if self.possible_moves[j] == True and self.is_checked_nextmove(i, j) == False:
                        return False
        
        output = None
        if self.is_checked(c):
            if c == 'white':
                output = 'blackwins'
            elif c == 'black':
                output = 'whitewins'
        else:
            output = 'draw-stalemate'
        return output
    
    def promotion_handler(self, pick_id, drop_id, piece_type, turn, castles):
        self.pieces[pick_id] = None
        self.pieces[drop_id] = Piece(turn, piece_type)
        return self.end_move(pick_id, drop_id, castles)

    def get_fen(self):
        return self.fen

    def get_turn(self):
        fen = self.fen
        fen = fen.split()
        fen_turn = fen[1]
        if fen_turn == 'w':
            return 'white'
        elif fen_turn == 'b':
            return 'black'
    
    def change_turn(self):
        fen = self.fen
        fen = fen.split()
        fen_turn = fen[1]
        if fen_turn == 'w':
            fen[1] = 'b'
        elif fen_turn == 'b':
            fen[1] = 'w'
        new_fen = " ".join(fen)
        self.fen = new_fen
    
    field_to_number = {
        'a8': 0,
        'b8': 1,
        'c8': 2,
        'd8': 3,
        'e8': 4,
        'f8': 5,
        'g8': 6,
        'h8': 7,

        'a7': 8,
        'b7': 9,
        'c7': 10,
        'd7': 11,
        'e7': 12,
        'f7': 13,
        'g7': 14,
        'h7': 15,

        'a6': 16,
        'b6': 17,
        'c6': 18,
        'd6': 19,
        'e6': 20,
        'f6': 21,
        'g6': 22,
        'h6': 23,

        'a5': 24,
        'b5': 25,
        'c5': 26,
        'd5': 27,
        'e5': 28,
        'f5': 29,
        'g5': 30,
        'h5': 31,

        'a4': 32,
        'b4': 33,
        'c4': 34,
        'd4': 35,
        'e4': 36,
        'f4': 37,
        'g4': 38,
        'h4': 39,

        'a3': 40,
        'b3': 41,
        'c3': 42,
        'd3': 43,
        'e3': 44,
        'f3': 45,
        'g3': 46,
        'h3': 47,

        'a2': 48,
        'b2': 49,
        'c2': 50,
        'd2': 51,
        'e2': 52,
        'f2': 53,
        'g2': 54,
        'h2': 55,

        'a1': 56,
        'b1': 57,
        'c1': 58,
        'd1': 59,
        'e1': 60,
        'f1': 61,
        'g1': 62,
        'h1': 63,
        }
    
    number_to_field = {
        0: 'a8',
        1: 'b8',
        2: 'c8',
        3: 'd8',
        4: 'e8',
        5: 'f8',
        6: 'g8',
        7: 'h8',

        8: 'a7',
        9: 'b7',
        10: 'c7',
        11: 'd7',
        12: 'e7',
        13: 'f7',
        14: 'g7',
        15: 'h7',

        16: 'a6',
        17: 'b6',
        18: 'c6',
        19: 'd6',
        20: 'e6',
        21: 'f6',
        22: 'g6',
        23: 'h6',

        24: 'a5',
        25: 'b5',
        26: 'c5',
        27: 'd5',
        28: 'e5',
        29: 'f5',
        30: 'g5',
        31: 'h5',

        32: 'a4',
        33: 'b4',
        34: 'c4',
        35: 'd4',
        36: 'e4',
        37: 'f4',
        38: 'g4',
        39: 'h4',

        40: 'a3',
        41: 'b3',
        42: 'c3',
        43: 'd3',
        44: 'e3',
        45: 'f3',
        46: 'g3',
        47: 'h3',

        48: 'a2',
        49: 'b2',
        50: 'c2',
        51: 'd2',
        52: 'e2',
        53: 'f2',
        54: 'g2',
        55: 'h2',

        56: 'a1',
        57: 'b1',
        58: 'c1',
        59: 'd1',
        60: 'e1',
        61: 'f1',
        62: 'g1',
        63: 'h1',
        }
    
    fen_dict = {
        'whitepawn': 'P',
        'whiteknight': 'N',
        'whitebishop': 'B',
        'whiterook': 'R',
        'whiteking': 'K',
        'whitequeen': 'Q',

        'blackpawn': 'p',
        'blackknight': 'n',
        'blackbishop': 'b',
        'blackrook': 'r',
        'blackking': 'k',
        'blackqueen': 'q',
    }