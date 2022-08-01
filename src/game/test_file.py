# list = [6, 7, 5, 3, 1, 1, None, None, None, 4]
# index_1 = [6, 7, 8, 9]
# outcome_1 = [list[i] for i in index_1]
# index_2 = [6, 7, 8]
# outcome_2 = [list[i] for i in index_2]



# print(outcome_1)
# print(all(x == None for x in outcome_1))
# print(outcome_2)
# print(all(x == None for x in outcome_2))


# class Piece:
#     def __init__(self, color, type, moved):
#         self.color = color
#         self.type = type
#         self.moved = moved

# list = [Piece('white', 'bishop', False), Piece('black', 'bishop', False), Piece('white', 'knight', False), None, None, Piece('white', 'king', False)]

# color = 'white'

# type_list = [x.type if x is not None and x.color is color else None for x in list]

# print(type_list)

# var1 = var2 = 'hello'

# print(var1)
# print(var2)

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
fen_split = fen.split()
print(fen_split)