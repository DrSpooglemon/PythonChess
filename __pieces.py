ALPHA = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
NUMERIC = ['8', '7', '6', '5', '4', '3', '2', '1']


class Piece:

    __legal_moves = []
    grid_position = None, None
    
    def __init__(self, board, color, board_position):
        self.board = board
        self.color = color
        self.board_position = board_position

    def __str__(self):
        return self.color[0].lower() + self.type[0] + self.type[-1]

    @property
    def x(self):
        return self.grid_position[1]

    @property
    def y(self):
        return self.grid_position[0]

    @property
    def king(self):
        return self.boards.kings[self.color]

    @property
    def legal_moves(self):
        return self.__legal_moves
                
    @property
    def board_position(self):
        n, a = self.grid_position
        return ALPHA[a] + NUMERIC[n]
    
    @board_position.setter
    def board_position(self, board_position):
        print('board position:', board_position)
        a, n = [char for char in board_position]
        self.grid_position = (NUMERIC.index(n), ALPHA.index(a.upper()))

    def calculate_moves(self):
        print(f'calculating moves for {self.type} {self.board_position}...')
        self.__legal_moves.clear()
        row, col = self.grid_position
        self._calculate_moves(row, col)

    def _add_move(self, move):
        move = ALPHA[move[1]] + NUMERIC[move[0]]
        self.board._move_selected_piece(move)
        print('History:', self.board.history)
        if not self.board.player_is_in_check:
            self.__legal_moves.append(move)
        self.board._undo_last_move()


class PawnMixin:

    type = 'Pawn'
    is_first_move = True
    is_passing = False

    @property
    def board_direction(self):
        if self.color == 'White':
            return -1
        else:
            return 1

    def _calculate_moves(self, row, col):
        d = self.board_direction
        self.__calculate_forward_moves(row, col, d)
        for i in {-1, 2}:
            if -1 < col + i < 8:
                self.__check_if_other_piece_can_be_taken(row + d, col + i)
                self.__check_if_other_piece_is_passing(row, col + i, d)

    def __calculate_forward_moves(self, row, col, d):
        if 0 <= row + d < 8 and not self.board[row + d][col]:
            self._add_move((row + d, col))
            if self.is_first_move and 0 <= row + d * 2 < 8:
                if not self.board[row + d * 2][col]:
                    self._add_move((row + d * 2, col))

    def __check_if_other_piece_can_be_taken(self, row, col):
        other = self.board[row][col]
        if other and other.color != self.color:
            self._add_move((row, col))       

    def __check_if_other_piece_is_passing(self, row, col, d):
        other = self.board[row][col]
        if (0 <= row + d < 8 and other and other.color != self.color 
            and other.type == 'Pawn' and other.is_passing):
                self._add_move((row + d, col))

    def check_if_self_is_passing(self, row, col, d):
        for i in {-1, 2}:
            other = self.board[row][col + i]
            if (other and other.color != self.color 
                and other.type == 'Pawn'):
                    self.is_passing = True
                    self.board.register_pawn_is_passing(self)


class KnightMixin:

    type = 'Knight'
    __moves = {
            (1, -2), (1, 2), (2, -1), (2, 1), 
            (-1, -2), (-1, 2), (-2, -1), (-2, 1)
        }

    def _calculate_moves(self, row, col):
        for r, c in self.__moves:
            if 0 <= row + r < 8 and 0 <= col + c < 8:
                if (not self.board[row + r][col + c] 
                    or self.board[row + r][col + c].color != self.color):
                        self._add_move((row + r, col + c))


class __LinearMoves:

    def _calculate_linear_moves(self, row, col, n=7):
        self.__calculate_up_moves(row, col, n)
        self.__calculate_down_moves(row, col, n)
        self.__calculate_left_moves(row, col, n)
        self.__calculate_right_moves(row, col, n)

    def __calculate_up_moves(self, row, col, n):
        for i in range(1, n+1):
            if row - i >= 0:
                if not self.board[row - i][col]:
                    self._add_move((row - i, col))
                elif self.board[row - i][col].color != self.color:
                    self._add_move((row - i, col))
                    break
            else:
                break

    def __calculate_down_moves(self, row, col, n):
        for i in range(1, n+1):
            if row + i < 8:    
                if self.board[row + i][col] is None:
                    self._add_move((row + i, col))
                elif self.board[row + i][col].color != self.color:
                    self._add_move((row + i, col))
                    break
            else:
                break

    def __calculate_left_moves(self, row, col, n):
        for i in range(1, n+1):
            if col - i >= 0:
                if self.board[row][col - i] is None:
                    self._add_move((row, col - i))
                elif self.board[row][col - i].color != self.color:
                    self._add_move((row, col - i))
                    break
            else:
                break

    def __calculate_right_moves(self, row, col, n):
        for i in range(1, n+1):
            if col + i < 8:    
                if self.board[row][col + i] is None:
                    self._add_move((row, col + i))
                elif self.board[row][col + i].color != self.color:
                    self._add_move((row, col + i))
                    break
            else:
                break


class __DiagonalMoves:

    def _calculate_diagonal_moves(self, row, col, n=7):
        self.__calculate_up_left_moves(row, col, n)
        self.__calculate_up_right_moves(row, col, n)
        self.__calculate_down_left_moves(row, col, n)
        self.__calculate_down_right_moves(row, col, n)

    def __calculate_up_left_moves(self, row, col, n):
        for i in range(1, n+1):
            if row - i >= 0 and col - i >= 0:
                if self.board[row - i][col - i] is None:
                    self._add_move((row - i, col - i))
                elif self.board[row - i][col - i].color != self.color:
                    self._add_move((row - i, col - i))
                    break
            else:
                break

    def __calculate_up_right_moves(self, row, col, n):
        for i in range(1, n+1):
            if row - i >= 0 and col + i < 8:
                if self.board[row - i][col + i] is None:
                    self._add_move((row - i, col + i))
                elif self.board[row - i][col + i].color != self.color:
                    self._add_move((row - i, col + i))
                    break
            else:
                break

    def __calculate_down_left_moves(self, row, col, n):
        for i in range(1, n+1):
            if row + i < 8 and col -i >= 0:
                if self.board[row + i][col - i] is None:
                    self._add_move((row + i, col - i))
                elif self.board[row + i][col - i].color != self.color:
                    self._add_move((row + i, col - i))
                    break
            else:
                break

    def __calculate_down_right_moves(self, row, col, n):
        for i in range(1, n+1):
            if row + i < 8 and col + i < 8:
                if self.board[row + i][col + i] is None:
                    self._add_move((row + i, col + i))
                elif self.board[row + i][col + i].color != self.color:
                    self._add_move((row + i, col + i))
                    break
            else:
                break


class RookMixin(__LinearMoves):

    type = 'Rook'

    def _calculate_moves(self, row, col):
        self._calculate_linear_moves(row, col)


class BishopMixin(__DiagonalMoves):

    type = 'Bishop'

    def _calculate_moves(self, row, col):
        self._calculate_diagonal_moves(row, col)
    

class QueenMixin(__LinearMoves, __DiagonalMoves):
    
    type ='Queen'

    def _calculate_moves(self, row, col):
        self._calculate_linear_moves(row, col)
        self._calculate_diagonal_moves(row, col)


class KingMixin(__LinearMoves, __DiagonalMoves):
    
    type = 'King'

    def _calculate_moves(self, row, col):
        self._calculate_linear_moves(row, col, 1)
        self._calculate_diagonal_moves(row, col, 1)

    def is_in_check(self):
        for i in range(1, 8):
            if self.y + i < 8:
                cell = self.board[self.y + i][self.x]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Rook' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.y + i < 8 and self.x - i >= 0:
                cell = self.board[self.y + i][self.x - i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Bishop' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.y + i < 8 and self.x + i < 8:
                cell = self.board[self.y + i][self.x + i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Bishop' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.y - i >= 0:
                cell = self.board[self.y - i][self.x]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Rook' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.y - i >= 0 and self.x - i >= 0:
                cell = self.board[self.y - i][self.x - i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Bishop' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.y - i >= 0 and self.x + i < 8:
                cell = self.board[self.y -i][self.x + i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Bishop' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.x + i < 8:
                cell = self.board[self.y][self.x + i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Rook' or cell.type == 'Queen':
                        return True
            else:
                break
        for i in range(1, 8):
            if self.x - i >= 0:
                cell = self.board[self.y][i]
                if cell:
                    if cell.color == self.color:
                        break
                    elif cell.type == 'Rook' or cell.type == 'Queen':
                        return True
            else:
                break