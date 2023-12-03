from players import Players

piece_values = {
    Players.BLACK: {
        "pawn": "pieces/black_pawn.gif",
        "rook": "pieces/black_rook.gif",
        "knight": "pieces/black_knight.gif",
        "bishop": "pieces/black_bishop.gif",
        "queen": "pieces/black_queen.gif",
        "king": "pieces/black_king.gif",
    },

    Players.WHITE: {
        "pawn": "pieces/white_pawn.gif",
        "rook": "pieces/white_rook.gif",
        "knight": "pieces/white_knight.gif",
        "bishop": "pieces/white_bishop.gif",
        "queen": "pieces/white_queen.gif",
        "king": "pieces/white_king.gif",
    },
}

class Piece: 
    def __init__(self, row): 
        self.white = True if row > 3 else False
        self.piece_color = Players.WHITE if self.white else Players.BLACK
        self.value = None
        self.first = True
        self.en_passantable = False
        self.worth = 0

    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        return True
    
    @staticmethod
    def get_all_valid_moves(row, col, board):
        valid_moves = []
        for new_row in range(len(board.board)):
            for new_col in range(len(board.board[0])):
                if board.check_move(row, col, new_row, new_col)[0]:
                    valid_moves.append((new_row, new_col))
        return valid_moves
    
    def __repr__(self):
        return f"{self.__class__.__name__.lower()}_{'white' if self.white else 'black'}"

class Pawn(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["pawn"]
        self.worth = 100
    
    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        difference = old_row-new_row if self.white else new_row-old_row
        horizontals = board.get_horizontal(old_row, old_col)
        horizontal = horizontals[0] if self.white else horizontals[1]
        diagonals = board.get_diagonal(old_row, old_col)
        diagonals = (diagonals[0], diagonals[1]) if self.white else (diagonals[2], diagonals[3])
        if difference != 1:
            if self.first and difference == 2 and len(horizontal) > 2 and old_col == new_col: # double pawn move
                return "double_pawn_move"
            return False
        if (board.get_value(new_row, new_col) != 0) or (old_col != new_col):
            if old_col-1 == new_col:
                diagonal = diagonals[0]
                side = horizontals[2]
            elif old_col+1 == new_col:
                diagonal = diagonals[1]
                side = horizontals[3]
            else:
                return False
            if len(diagonal) == 1:
                if diagonal[0] != 0:
                    return True
            if len(side) == 1:
                if isinstance(side[0], Pawn):
                    if side[0].en_passantable:
                        return "en_passant"
            return False
        return True
    
class Rook(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["rook"]
        self.worth = 500
    
    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        directions = board.get_horizontal(old_row, old_col)
        move_directions = [old_row-new_row, new_row-old_row, old_col-new_col, new_col-old_col]
        if old_col != new_col and old_row != new_row:
            return False
        for direction in move_directions:
            if direction > 0:
                idx = move_directions.index(direction)
                if move_directions[idx] > len(directions[idx]):
                    return False
        return True

class Knight(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["knight"]
        self.worth = 300
    
    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        row_dif = abs(old_row-new_row)
        col_dif = abs(old_col-new_col)
        return (row_dif == 2 and col_dif == 1) or (row_dif == 1 and col_dif == 2)

class Bishop(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["bishop"]
        self.worth = 300
    
    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        directions = board.get_diagonal(old_row, old_col) # upper_left, upper_right, lower_left, lower_right
        move_directions = [
            old_row-new_row>0 and old_col-new_col>0,
            old_row-new_row>0 and new_col-old_col>0, 
            new_row-old_row>0 and old_col-new_col>0,
            new_row-old_row>0 and new_col-old_col>0 
        ]
        if abs(old_row-new_row) != abs(old_col-new_col):
            return False
        for idx, direction in enumerate(move_directions):
            if direction:
                if abs(old_row-new_row) > len(directions[idx]):
                    return False
        return True

class Queen(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["queen"]
        self.worth = 800
    
    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        horizontal_directions = board.get_horizontal(old_row, old_col)
        upper_left, upper_right, lower_left, lower_right = board.get_diagonal(old_row, old_col)
        diagonal_directions = [[upper_left, upper_right], [lower_left, lower_right]]
        move_directions = [
            old_row-new_row, 
            new_row-old_row, 
            old_col-new_col, 
            new_col-old_col,
        ]
        active_move_dirs = list(filter(lambda x: x > 0, move_directions))
        diagonal = []
        if (abs(old_row-new_row) != abs(old_col-new_col)) and (old_col != new_col and old_row != new_row):
            return False
        for idx, direction in enumerate(move_directions):
            if direction > 0:
                diagonal.append(idx)
                if len(active_move_dirs) == 1 and move_directions[idx] > len(horizontal_directions[idx]):
                    return False
        if len(diagonal) == 2:
            diagonal[1] -= 2
            diagonal_direction = diagonal_directions[diagonal[0]][diagonal[1]]
            if abs(old_row-new_row) > len(diagonal_direction):
                return False
        return True

class King(Piece):
    def __init__(self, row):
        super().__init__(row)
        self.value = piece_values[self.piece_color]["king"]

    def is_valid_move(self, old_row, old_col, new_row, new_col, board):
        row_dif = abs(old_row-new_row)
        col_dif = abs(old_col-new_col)
        if not ((row_dif == 1 and col_dif == 1) or (row_dif == 1 and col_dif == 0) or (row_dif == 0 and col_dif == 1)):
            return False
        return True