from copy import deepcopy
import uuid
from pieces import King, Queen, Knight, Rook, Bishop, Pawn
import turtle
from players import Players

padding = "\t"

rook_positions = [(0, 0), (0, 7), (7, 0), (7, 7)]
knight_positions = [(0, 1), (0, 6), (7, 1), (7, 6)]
bishop_positions = [(0, 2), (0, 5), (7, 2), (7, 5)]
king_positions = [(0, 4), (7, 4)]
queen_positions = [(0, 3), (7, 3)]

alphabet = list(map(chr, range(97, 105)))

class Board:
    def __init__(self, square_size):
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        self.set_up_pieces()
        self.turn = Players.WHITE
        self.square_size = square_size
        self.black_square_color = (0.5,0.65,0.3)
        self.white_square_color = (0.9, 0.9, 0.8)
        self.border_color = (0, 0, 0)
        self.selected_color = (1, 0, 0)
        self.highlighted_squares = []
        self.selected = None
        self.no_captures_or_pawn_moves = {
            Players.WHITE: 0,
            Players.BLACK: 0
        }

    def set_up_pieces(self):
        for i in range(8):
            self.board[1][i] = Pawn(1)
            self.board[6][i] = Pawn(6)
        for rook_pos in rook_positions:
            self.board[rook_pos[0]][rook_pos[1]] = Rook(rook_pos[0])
        for knight_pos in knight_positions:
            self.board[knight_pos[0]][knight_pos[1]] = Knight(knight_pos[0])
        for bishop_pos in bishop_positions:
            self.board[bishop_pos[0]][bishop_pos[1]] = Bishop(bishop_pos[0])
        for king_pos in king_positions:
            self.board[king_pos[0]][king_pos[1]] = King(king_pos[0])
        for queen_pos in queen_positions:
            self.board[queen_pos[0]][queen_pos[1]] = Queen(queen_pos[0])
    
    def get_value(self, row, column):
        return self.board[row][column]

    def set_value(self, row, column, new_val):
        self.board[row][column] = new_val

    def check_move(self, old_row, old_col, new_row, new_col):
        piece = self.get_value(old_row, old_col)
        previous_val = self.get_value(new_row, new_col)
        if piece == 0:
            return False, "There isn't a piece in the selected square"
        if old_row == new_row and old_col == new_col:
            return False, "You haven't moved"
        if (piece.white and self.turn == Players.BLACK) or ((not piece.white) and self.turn == Players.WHITE):
            return False, "You tried to move a piece that was your opponents"
        if previous_val != 0:
            if (previous_val.white and piece.white) or (not previous_val.white and not piece.white):
                if not (type(piece) == King and type(previous_val) == Rook):
                    return False, "Eating your own pieces isn't a valid move"
                else:
                    return self.castle(old_row, old_col, new_row, new_col), "Not a valid castle"
        valid_move = piece.is_valid_move(old_row, old_col, new_row, new_col, self)
        if not valid_move:
            return False, "That isn't a valid move for that piece"
        self.set_value(old_row, old_col, 0)
        self.set_value(new_row, new_col, piece)
        in_check = self.in_check()
        self.set_value(old_row, old_col, piece)
        self.set_value(new_row, new_col, previous_val)
        if in_check:
            return False, "The king would be in check"
        if valid_move in ["en_passant", "double_pawn_move"]:
            return valid_move, ""
        return True, ""
    
    def move(self, old_row, old_col, new_row, new_col):
        result, expl = self.check_move(old_row, old_col, new_row, new_col)
        self.set_en_passantable(self.get_value(old_row, old_col)) if result == "double_pawn_move" else self.set_en_passantable()
        if result and self.get_value(new_row, new_col) == 0 and self.get_value(old_row, old_col).__class__.__name__.lower() != "pawn":
            self.no_captures_or_pawn_moves[self.turn] += 1
        elif result and (self.get_value(new_row, new_col) != 0 or self.get_value(old_row, old_col).__class__.__name__.lower() == "pawn"):
            self.no_captures_or_pawn_moves[self.turn] = 0
        if result == "castle":
            king = self.get_value(old_row, old_col)
            rook = self.get_value(new_row, new_col)
            king.first, rook.first = False, False
            new_rook_pos = (old_row, old_col-1 if new_col < old_col else old_col+1)
            new_king_pos = (new_row, old_col-2 if new_col < old_col else old_col+2)
            self.set_value(new_rook_pos[0], new_rook_pos[1], rook)
            self.set_value(new_king_pos[0], new_king_pos[1], king)
            self.set_value(old_row, old_col, 0)
            self.set_value(new_row, new_col, 0)
            return True, ""
        if result == "en_passant":
            self.set_value(new_row, new_col, self.get_value(old_row, old_col))
            self.set_value(old_row, old_col, 0)
            self.set_value(new_row+1 if self.turn == Players.WHITE else new_row-1 , new_col, 0)
            return True, expl
        if result:
            self.set_value(new_row, new_col, self.get_value(old_row, old_col))
            if self.get_value(old_row, old_col).__class__.__name__.lower() == "pawn" and (new_row == 0 or new_row == 7):
                self.set_value(new_row, new_col, Queen(abs(new_row-len(self.board))))
            self.set_value(old_row, old_col, 0)
            self.get_value(new_row, new_col).first = False
            return True, expl
        return False, expl
    
    def get_board(self):
        if self.turn == Players.WHITE:
            return self.board
        else:
            return [x[::-1] for x in self.board][::-1]
    
    def change_turns(self):
        if self.turn == Players.WHITE:
            self.turn = Players.BLACK
        else:
            self.turn = Players.WHITE

    def get_diagonal(self, row, column):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_lines(row, column, directions)

    def get_horizontal(self, row, column):
        directions = [(-1,0), (1, 0), (0, -1), (0, 1)]
        return self._get_lines(row, column, directions)
    
    def _get_lines(self, row, column, directions):
        lines = [[], [], [], []]
        for index, (row_change, column_change) in enumerate(directions):
            temp_row, temp_column = row+row_change, column+column_change
            while 0 <= temp_row < len(self.board) and 0 <= temp_column < len(self.board[0]):
                value = self.get_value(temp_row, temp_column)
                lines[index].append(value)
                if value != 0:
                    break
                temp_row += row_change
                temp_column += column_change
        return lines

    def in_check(self, board=None):
        if board is None:
            board = self
        piece_positions = board.get_piece_positions()
        enemy_color = Players.BLACK if board.turn == Players.WHITE else Players.WHITE
        king_row, king_column = piece_positions[board.turn]["king"]["pos"]
        for piece_dict in list(piece_positions[enemy_color].values()):
            row, column = piece_dict["pos"]
            piece = piece_dict["piece"]
            if piece.is_valid_move(row, column, king_row, king_column, board):
                return True
        return False
                    
    def get_piece_positions(self):
        black = {}
        white = {}
        for row in range(len(self.get_board())):
            for column in range(len(self.get_board()[0])):
                piece = self.get_value(row, column)
                if piece != 0:
                    name = str(self.get_value(row, column).__class__.__name__).lower()
                    if (name != "king"):
                        name += f"_{uuid.uuid4().hex.upper()[0:6]}"
                    piece_dict = {"piece": piece, "pos":(row, column)}
                    if piece.white:
                        white[name] = piece_dict
                    else:
                        black[name] = piece_dict
        return {Players.WHITE:white,Players.BLACK:black}
                    
    def check_mate(self, color=None):
        if color is None:
            color = self.turn
        if not self.in_check():
            return False
        pieces = list(self.get_piece_positions()[color].values())
        for row in range(len(self.board)): 
            for col in range(len(self.board[0])):
                for piece_dict in pieces:
                    curr_row, curr_col = piece_dict["pos"]
                    if self.check_move(curr_row, curr_col, row, col)[0]:
                        test_board = deepcopy(self)
                        test_board.move(curr_row, curr_col, row, col)
                        if not test_board.in_check():
                            return False
        return True

    def stale_mate(self):
        pieces = list(self.get_piece_positions()[self.turn].values())
        for row in range(len(self.board)): 
            for col in range(len(self.board[0])):
                for piece_dict in pieces:
                    curr_row, curr_col = piece_dict["pos"]
                    if self.check_move(curr_row, curr_col, row, col)[0]:
                            return False
        return True
    
    def draw(self):
        if self.stale_mate():
            print("A stalemate")
            return True
        pieces = list(self.get_piece_positions()[Players.BLACK].values()) + list(self.get_piece_positions()[Players.WHITE].values())
        amounts = {
            "bishop": 0,
            "rook": 0,
            "queen": 0,
            "knight": 0,
            "pawn": 0,
        }
        for key, _ in amounts.items():
            for piece in pieces:
                if piece["piece"].__class__.__name__.lower() == key:
                    amounts[key] += 1
        if amounts["rook"] == 0 and amounts["queen"] == 0 and amounts["pawn"] == 0:
            if amounts["knight"] < 2 and amounts["bishop"] == 0:
                print("Not enough material")
                return True
            if amounts["bishop"] < 2 and amounts["knight"] == 0:
                print("Not enough material")
                return True
        if self.no_captures_or_pawn_moves[Players.WHITE] >= 50 and self.no_captures_or_pawn_moves[Players.BLACK] >= 50:
            print("No captures or pawn moves in  50")
            return True
        return False

    def castle(self, old_row, old_col, new_row, new_col):
        king = self.get_value(old_row, old_col)
        rook = self.get_value(new_row, new_col)
        rook_dir = 2 if new_col < old_col else 3
        horizontals = self.get_horizontal(old_row, old_col)[rook_dir]
        step = -1 if rook_dir == 2 else 1
        if not (rook.first and king.first):
            return False
        if horizontals[-1] != rook:
            return False
        if self.in_check():
            return False
        for col in range(old_col+step, new_col, step):
            self.set_value(old_row, old_col, 0)
            self.set_value(old_row, col, king)
            in_check = self.in_check()
            self.set_value(old_row, old_col, king)
            self.set_value(old_row, col, 0)
            if in_check:
                return False
        return "castle"
    
    def set_en_passantable(self, moved_piece=None):
        pieces = list(self.get_piece_positions()[Players.WHITE].values()) + list(self.get_piece_positions()[Players.BLACK].values())
        for piece in pieces:
            if piece["piece"] == moved_piece:
                moved_piece.en_passantable = True
                continue
            piece["piece"].en_passantable = False

    def _draw_square(self, white, x, y, pen):
        pen.up()
        pen.goto(x, y)
        pen.down()
        color = self.white_square_color if white else self.black_square_color
        pen.fillcolor(color)
        pen.pencolor(self.border_color)
        pen.begin_fill() 
        for _ in range(4):
            pen.forward(self.square_size)
            pen.right(360 / 4)
        pen.end_fill()

    def _draw_piece(self, x, y, piece, pen):
        pen.up()
        pen.goto(x, y)
        pen.down()
        pen.shape(piece.value)
        pen.stamp()
        pen.ht()
    
    def _highlight(self, color, square, pen):
        if self.turn == Players.BLACK:
            square = (len(self.board)-1-square[0], len(self.board[0])-1-square[1])
        x, y = 1+self.square_size*square[1], self.square_size+self.square_size*square[0]
        pen.pencolor(color)
        pen.up()
        pen.goto(x, y)
        pen.down()
        for _ in range(4):
            pen.forward(self.square_size)
            pen.right(360 / 4)

    def handle_clicks(self, row, col, pen):
        row, col = len(self.board)-1-row if self.turn == Players.BLACK else row, len(self.board[0])-1-col if self.turn == Players.BLACK else col
        return_value = None
        if len(self.highlighted_squares) > 0:
            self._highlight(color=self.border_color, square=self.selected, pen=pen)
            for square in self.highlighted_squares:
                if (row, col) == square:
                    return_value = self.move(self.selected[0], self.selected[1], row, col)
                self._highlight(color=self.border_color, square=square, pen=pen)
        self.highlighted_squares = []
        if return_value is not None:
            self.selected = None
            return return_value
        value = self.get_value(row, col)
        if value == 0:
            return False, ""
        if (self.turn == Players.WHITE and not value.white) or (self.turn == Players.BLACK and value.white):
            return False, ""
        self.selected = (row, col)
        for move in value.get_all_valid_moves(row, col, self)+[(row, col)]:
            self.highlighted_squares.append(move)
            self._highlight(square=move, color=self.selected_color, pen=pen)
        turtle.update()
        return False, ""

    def draw_board(self, pen, square_changes=None):
        if square_changes is None:
            square_changes = [[False]*8]*8
        elif square_changes is not None and self.turn == Players.BLACK:
            square_changes = [x[::-1] for x in square_changes][::-1]
        for row in range(len(self.get_board())):
            for col in range(len(self.get_board()[0])):
                if square_changes[row][col] == False:
                    x, y = 1 + self.square_size*col, self.square_size + self.square_size*row
                    value = self.get_board()[row][col]
                    self._draw_square(True, x, y, pen) if (row+col) % 2 == 0 else self._draw_square(False, x, y, pen)
                    if value != 0:
                        self._draw_piece(x+0.5*self.square_size, y-0.5*self.square_size, value, pen)     
        turtle.update()
    
    def display_text(self, pen, text):
        pen.up()
        pen.goto(800/2-(20*len(text)), 800/2)
        pen.down()
        pen.pencolor(self.selected_color)
        pen.write(text.upper(), font=("Arial", 50, "bold"))
        pen.ht()
        turtle.update()
    
    def get_changed_squares(self, old_board):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                old_board[row][col] = repr(self.board[row][col]) == repr(old_board[row][col])
        return old_board
    
    def evaluate_position(self, color):
        opponent_color = Players.BLACK if color == Players.WHITE else Players.WHITE
        own_pieces = list(self.get_piece_positions()[color].values())
        opponent_pieces = list(self.get_piece_positions()[opponent_color].values())
        own_pieces_worth, opponent_pieces_worth = 0, 0
        for own_piece in own_pieces:
            own_pieces_worth += own_piece["piece"].worth
        for opponent_piece in opponent_pieces:
            opponent_pieces_worth += opponent_piece["piece"].worth
        if self.check_mate(color):
            return float("-inf")
        if self.draw():
            return 0
        if self.in_check():
            return (own_pieces_worth-opponent_pieces_worth)-500
        return own_pieces_worth-opponent_pieces_worth

    def get_all_valid_moves(self):
        pieces = [piece["pos"] for piece in list(self.get_piece_positions()[self.turn].values())]
        valid_moves = []
        for piece_row, piece_col in pieces:
            moves_for_piece = self.get_value(piece_row, piece_col).get_all_valid_moves(piece_row, piece_col, self)
            if moves_for_piece:
                valid_moves.append([(piece_row, piece_col) + move for move in moves_for_piece])
        return sum(valid_moves, [])

    def check_draw_and_mate(self, pen):
        if self.check_mate():
            self.change_turns()
            turn = self.turn.value.lower().capitalize()
            self.change_turns()
            self.display_text(pen, f"{turn} won!")
            turtle.done()
            quit()
        if self.draw():
            self.display_text(pen, "A draw!")
            turtle.done()
            quit()