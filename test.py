import chess
import chess.svg

from src.config import settings
from src.game import Game

game = Game(settings)
game.new_board()
# game.board.push(chess.Move(chess.A4, chess.B5))
#
game.save_board()

# move = game.get_possible_moves_from(chess.B7)[1]
# game.move(chess.Move(chess.A4, chess.B5))

# svg = game.get_png()
# with open('board.png', 'wb') as f:
# 	f.write(svg)


