from GameBoard import GameBoard

game = GameBoard()

while (game.cards_remaining > 0):

    game.complete_round()

game.report_score()
