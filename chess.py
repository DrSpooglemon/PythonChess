#!/usr/bin/python3
from pieces import *

'''TODO
refactor
undo moves,
record game,
save game,
startrek rules
'''
ALPHA = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
NUMERIC = ['8', '7', '6', '5', '4', '3', '2', '1']

PIECES = {'Pn': Pawn, 'Rk': Rook, 'Kt': Knight, 'Bp': Bishop, 'Qn': Queen, 'Kg': King}

COLORS = {'w': 'White', 'b': 'Black'}

BOARD_LAYOUT = {
    'A8': 'bRk', 'B8': 'bKt', 'C8': 'bBp', 'D8': 'bQn', 'E8': 'bKg', 'F8': 'bBp', 'G8': 'bKt', 'H8': 'bRk',
    'A7': 'bPn', 'B7': 'bPn', 'C7': 'bPn', 'D7': 'bPn', 'E7': 'bPn', 'F7': 'bPn', 'G7': 'bPn', 'H7': 'bPn',
    'A2': 'wPn', 'B2': 'wPn', 'C2': 'wPn', 'D2': 'wPn', 'E2': 'wPn', 'F2': 'wPn', 'G2': 'wPn', 'H2': 'wPn',
    'A1': 'wRk', 'B1': 'wKt', 'C1': 'wBp', 'D1': 'wQn', 'E1': 'wKg', 'F1': 'wBp', 'G1': 'wKt', 'H1': 'wRk',
}


class Board(list):

    __pieces = {'White': [], 'Black': []}
    __pieces_taken = {'White': [], 'Black': []}
    kings = {'White': None, 'Black': None}
    history = []

    def __init__(self, check_callback, checkmate_callback,
                 piece_moved_callback=None, 
                 last_move_undone_callback=None):
        self.check_callback = check_callback
        self.checkmate_callback = checkmate_callback
        if piece_moved_callback:
            self.piece_moved_callback = piece_moved_callback
        else:
            self.piece_moved_callback = lambda move: None
        if last_move_undone_callback:
            self.last_move_undone_callback = last_move_undone_callback
        else:
            self.last_move_undone_callback = lambda move: None
        self.extend([[None] * 8 for _ in range(8)])
        self.player = 0
        self.playing = False

    def __str__(self):
        N = [' 8 ', ' 7 ', ' 6 ', ' 5 ', ' 4 ', ' 3 ', ' 2 ', ' 1 ']
        lines = []
        for j, row in enumerate(self):
            lines.append([N[j]])
            for i, cell in enumerate(row):
                lines[j].append(str(cell) if cell else ('___' if (i+j) % 2 else '///'))
        lines.append(['     A   B   C   D   E   F   G   H '])
        return '\n'.join(['|'.join(line) for line in lines])
        
    @property
    def current_player(self):
        return ['White', 'Black'][self.player]

    @property
    def current_square(self):
        y, x = self.selected_peice.grid_position
        return self[y][x]

    @current_square.setter
    def current_square(self, piece):
        y, x = self.selected_piece.grid_position
        self[y][x] = piece

    @property
    def destination_square(self):
        try:
            y, x = self.__destination_square
            return self[y][x]
        except:
            return

    @destination_square.setter
    def destination_square(self, pos):
        print('destination square:',  
              NUMERIC.index(pos[1]),
              ALPHA.index(pos[0]))
        self.__destination_square = (NUMERIC.index(pos[1]),
                                     ALPHA.index(pos[0]))

    @property
    def pieces(self):
        return self.__pieces[self.current_player]

    @property
    def pieces_taken(self):
        return self.__pieces_taken[self.current_player]

    @property
    def player_is_in_check(self):
        return self.kings[self.current_player].is_in_check()
    
    def switch_player(self):
        self._switch_player()
        if self.player_is_in_check:
            self.check_if_checkmate()

    def _switch_player(self):
        self.player = (self.player + 1) % 2

    def check_if_checkmate(self):
        self.check_callback()
        for piece in self.pieces:
            if piece.calculate_legal_moves():
                return
        self.checkmate_callback()
        self._switch_player()
        self.winner = self.current_player
        
    def new_game(self):
        if not self.playing:
            for board_position, pc in BOARD_LAYOUT.items():
                Piece, color = PIECES[pc[1:]], COLORS[pc[:1]]
                piece = Piece(self, color, board_position)
                row, col = piece.grid_position
                self[row][col] = piece
                self.pieces.append(piece)
                if piece.type == 'King':
                    self.kings.update({color: piece})
            self.playing = True
            self.selected_piece = None

    def end_game(self):
        self.clear()
        self.__init__()
        list(map(lambda list: list.clear(), self.__pieces_taken.values()))
        list(map(lambda list: list.clear(), self.__pieces.values()))
        self.player = 0
        self.playing = False
        
    def select_piece(self, pos):
        try:
            i, j = ALPHA.index(pos[0]), NUMERIC.index(pos[1])
            self.selected_piece = piece = self[j][i]
            return piece
        except:
            return

    def deselect_piece(self):
        self.selected_piece = None

    def move_selected_piece(self, pos):
        if pos in self.selected_piece.legal_moves:
            self._move_selected_piece(pos)
            self.switch_player()
            self.piece_moved_callback(self.history[-1])
        else:
            self.selected_piece = None
            self.piece_moved_callback(None)

    def _move_selected_piece(self, pos):
        print('moving...')
        move = {'color': self.current_player,
                'piece': self.selected_piece.type,
                'start': self.selected_piece.board_position, 
                'destination': pos, 
                'piece_taken': False}
        self.current_square = None
        self.destination_square = pos
        if self.destination_square:
            self.pieces.remove(self.destination_square)
            self.pieces_taken.append(self.destination_square)
            print(self.destination_square.type, self.destination_square.board_position)
            move.update({'piece_taken': True})
        self.selected_piece.board_position = pos
        self.current_square = self.selected_piece
        self.history.append(move)

    def undo_last_move(self):
        if self.history:
            self.move = self.history[-1]
            self.switch_player()
            self._undo_last_move()
            self.last_move_undone_callback(move)

    def _undo_last_move(self):
        print('undoing...')
        move = self.history.pop()
        self.select_piece(move['destination'])
        if move['piece_taken']:
            self.current_square = \
                piece = self.pieces_taken.pop()
            self.pieces.append(piece)
        else:
            self.current_square = None
        self.selected_piece.board_position = move['start']
        self.current_square = self.selected_piece


if __name__ == '__main__':
    from os import system
    from time import sleep

    def clear():
        system('clear')
        sleep(.2)

    def print_board():
        print('       Chess', 
            '\n   --------------------\n')
        print(board, '\n')

    check = False
    def check_callback():
        global check
        check = True

    checkmate = False
    def checkmate_callback():
        global checkmate
        checkmate = True

    clear()
    board = Board(check_callback, checkmate_callback)
    board.new_game()
    playing = True
    invalid_selection = False
    invalid_move = False
    game = True
    while game:
        clear()
        print_board()
        print(f"\n    {board.current_player} player's turn.\n")
        if checkmate:
            print(f'    Check Mate!\n\n    {board.winner} wins\n')
            try:
                new_game = input('    Would you like to play another game?(y/N): ')
                if new_game.lower() == 'n':
                    game = False
                    clear()
                    continue
                else:               
                    board.end_game()
                    board.new_game()
            except KeyboardInterrupt:
                board.end_game()
                board.new_game()
                continue
            except EOFError:
                end_game = input(
                    ('\n\n    You are about to close the program.\n'
                     + '\n    Are you sure(y/N): '))
                if end_game.lower() == 'y':
                    clear()
                    game = False
                continue
        else:
            if check:
                print('    Check!\n')
            if invalid_selection:
                print('    ERROR: Invalid selection!\n')
            try:
                selection = input('    Select a piece: ')
                if selection == 'undo':
                    board.undo_last_move()
                    continue
            except KeyboardInterrupt:
                new_game = input(
                    ('\n\n    You are about to throw the current game away.\n'
                     + '\n    Are you sure (y/N): '))
                if new_game.lower() == 'y':
                    board.end_game()
                    board.new_game()
                continue
            except EOFError:
                end_game = input(
                    ('\n\n    You are about to close the program.\n'
                     + '\n    Are you sure(y/N): '))
                if end_game.lower() == 'y':
                    clear()
                    game = False
                continue
        selection = selection[0].upper() + selection[1]
        if selection:
            clear()
            piece = board.select_piece(selection)
            if piece:
                invalid_selection = False
                piece.calculate_moves()
                if piece:
                    waiting = True
                    while waiting:
                        clear()
                        print_board()
                        print(f'\n    You have selected: {piece.type} {piece.board_position}\n')
                        print('    legal moves:', piece.legal_moves, '\n')
                        if invalid_move:
                            print('    ERROR: Invalid move!\n')
                        try:
                            move = input('    Make your move: ')
                        except KeyboardInterrupt:
                            board.deselect_piece()
                            break
                        except EOFError:
                            end_game = input(
                                ('\n\n    You are about to close the program.\n'
                                 + '\n    Are you sure(y/N): '))
                            if end_game.lower() == 'y':
                                clear()
                                game = False
                                break
                        move = move[0].upper() + move[1]
                        if move in piece.legal_moves:
                            invalid_move = False
                            board.move_selected_piece(move)
                            check = False
                            waiting = False
                        else:
                            invalid_move = True
            else:
                invalid_selection = True
    print('Thanks for playing.')
    sleep(2)
    clear()