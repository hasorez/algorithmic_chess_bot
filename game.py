import turtle
import math
from board import Board
from players import Players
from opponent import Opponent
from pieces import piece_values
from copy import deepcopy
turtle.tracer(0)

width, height = 800, 800
square_size = width/8
player_color = Players.BLACK

screen = turtle.Screen()
screen.setup(width, height)
screen.setworldcoordinates(0, height+10, width+10, 0)
screen.cv._rootwindow.resizable(False, False)

pen = turtle.Turtle()
pieces = list(piece_values[Players.WHITE].values()) + list(piece_values[Players.BLACK].values())
for piece in pieces:
    screen.addshape(piece)

board = Board(square_size)
opponent = Opponent()

def get_mouse_click_coor(x, y):
    row = math.floor(y/square_size)
    col = math.floor(x/square_size)
    if row < 0 or row > 7 or col < 0 or col > 7:
        return
    square_changes = deepcopy(board).board
    moved,_ = board.handle_clicks(row, col, pen)
    if moved:
        board.draw_board(pen, square_changes=board.get_changed_squares(square_changes))
        board.change_turns()
        square_changes = deepcopy(board).board
        board.check_draw_and_mate(pen)
        opponent.make_move(board)
        board.change_turns()
        board.draw_board(pen, square_changes=board.get_changed_squares(square_changes))
        board.check_draw_and_mate(pen)

if __name__ == "__main__":
    if player_color == Players.BLACK:
        board.change_turns()
    board.draw_board(pen)
    screen.onscreenclick(get_mouse_click_coor)
    turtle.mainloop()

# TODO: clean code - optimize move gen and bot