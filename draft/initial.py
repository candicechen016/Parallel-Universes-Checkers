"""
Parallel-Universes Checkers.

winninig:
1. NO PIECES on both boards
2. NO STEPS AND NO TRANFE on both boards

rules:
1. can only Transfer once
2. can not capture at the transferring round
3. only transfer to an empty square and must go to an orthogonally-adjacent square
4. Make Moves:
    a. move one piece at the same universe two turns
    b. move one piece of each board

"""
import random

import numpy as np
import copy


class GameState:
    count = 0

    def __init__(self, board_size, player, board1=None, board2=None, no_capture=0):
        GameState.count += 1
        self.board1 = board1
        self.board2 = board2
        if board1 is None or board2 is None:
            self.board1, self.board2 = self.initial_board(board_size)


        self.board_size = board_size
        self.player = player
        self.direction = 1 if self.player == 'w' else -1
        self.opponent = 'b' if self.player == 'w' else 'w'
        self.no_capture = no_capture
        self.positions = self.get_positions(self.player)
        self.opponent_positions = self.get_positions(self.opponent)

    def initial_board(self, size):
        rows_with_pieces = (size - 2) / 2
        board = []
        for i in list(range(size + 2)):
            if i == 0 or i == size + 1:
                board.append(['  '] + ['---'] * (size) + ['  '])
            elif i in [rows_with_pieces + 1, rows_with_pieces + 2]:
                board.append(['|'] + ['.'] * size + ['|'])
            else:
                p = 'w1'
                if i % 2 != 0:
                    if i >= (size - rows_with_pieces):
                        p = ' b1'
                    board.append(['|'] + ['.', p] * (size // 2) + ['|'])
                else:
                    if i >= (size - rows_with_pieces):
                        p = 'b1'
                    board.append(['|'] + [p, '.'] * (size // 2) + ['|'])

        b1 = np.array(board)
        b = np.flip(b1, 1)
        c = np.where(b == 'w1', 'w2', b)
        b2 = np.where(c == 'b1', 'b2', c)
        return b1, b2

    def get_positions(self, player):
        """
          :param positions1: postions of pieces in original board, ex. w1 in board1, b2 in board2
          :param king_postions1: postions of king pieces in original board, ex. w1k in board1, b2k in board2
          :param postions2: postions of pieces in tranfer board, ex. w2 in board1, b1 in board2
          :param king_positions: postions of king pieces in tranfer board, ex. w2k in board1, b1k in board2
          :param board:  original board for current player
          :param tranfer_board: transfer board for current player
          :return:
          """
        return {'board1': {'positions1': np.argwhere(self.board1 == player + '1'),
                           'king_positions1': np.argwhere(self.board1 == player + '1k'),
                           'positions2': np.argwhere(self.board1 == player + '2'),
                           'king_positions2': np.argwhere(self.board1 == player + '2k')
                           },
                'board2': {'positions1': np.argwhere(self.board2 == player + '1'),
                           'king_positions1': np.argwhere(self.board2 == player + '1k'),
                           'positions2': np.argwhere(self.board2 == player + '2'),
                           'king_positions2': np.argwhere(self.board2 == player + '2k')}}

    def get_one_move(self, row_dir_list, positions, board, board_num):
        one_move_board = []
        one_move_list = []
        for position in positions:
            for row_dir in row_dir_list:
                next_row = position[0] + row_dir
                for dir in [-1, 1]:
                    next_col = position[1] + dir
                    if board[next_row, next_col] == '.':
                        next_move = {'start_move': (position[0], position[1]), 'start_board': board_num,
                                     'end_move': (next_row, next_col), 'end_board': board_num, 'capture': False}
                        one_move_list.append(next_move)
                        next_one_move = self.update_board_normal(next_move)
                        one_move_board.append(next_one_move)
                    if board[next_row, next_col][0] == self.opponent:
                        if board[next_row + row_dir, next_col + dir] == '.':
                            next_move = {'start_move': (position[0], position[1]), 'start_board': board_num,
                                         'end_move': (next_row + row_dir, next_col + dir),
                                         'end_board': board_num, 'capture': True}
                            one_move_list.append(next_move)
                            next_capture_move = self.update_board_normal(next_move)
                            one_move_board.append(next_capture_move)

        return one_move_list, one_move_board

    def get_two_continuous_move(self, one_move_list, one_move_board, row_dir):
        two_move_board = []
        two_moves = []
        for i in range(len(one_move_list)):
            second_moves, second_move_boards = self.get_one_move(row_dir, [one_move_list[i]['end_move']],
                                                                 one_move_board[i], one_move_list[i]['end_board'])
            if len(second_moves):
                two_move_board.append(second_move_boards)
                for second_move in second_moves:
                    two_moves.append([one_move_list[i], second_move])
        return two_moves, two_move_board

    def update_board_normal(self, move, make_move=False):
        board = self.board1 if move['start_board'] == 1 else self.board2
        if make_move:
            board_temp = board
        else:
            board_temp = copy.deepcopy(board)
        player = board[move['start_move'][0], move['start_move'][1]]
        board_temp[move['start_move'][0], move['start_move'][1]] = '.'
        if (player[0] == 'w' and move['end_move'][0] == self.board_size) or (
                player[0] == 'b' and move['end_move'][0] == 1):
            board_temp[move['end_move'][0], move['end_move'][1]] = player[:2] + 'k'  # change to king
        else:
            board_temp[move['end_move'][0], move['end_move'][1]] = player
        if move['capture']:
            board_temp[int((move['start_move'][0] + move['end_move'][0]) / 2), int(
                (move['start_move'][1] + move['end_move'][1]) / 2)] = '.'
        return board_temp

    def find_orthogonally_neighbors(self, piece_position, board):
        x, y = piece_position
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        empty = []
        for n in neighbors:
            if board[n] == '.':
                empty.append(n)
        return empty

    def check_win(self, next_move):
        has_pieces = 0

        # condition 1: the player has NO STEPS and NO WAY to transfer to both boards
        if not next_move:
            print('c1winner:', self.opponent)
            return self.opponent

        for board_name in ['board1', 'board2']:
            piece_positions = np.concatenate((self.positions[board_name]['positions1'],
                                              self.positions[board_name]['positions2'],
                                              self.positions[board_name]['king_positions1'],
                                              self.positions[board_name]['king_positions2']))
            # condition 2: the player has NO PIECES on Both boards
            if piece_positions.size == 0:
                has_pieces += 1
                continue
            print('has_pieces', has_pieces)
        if has_pieces == 2:
            print('c2winner:', self.opponent)
            return self.opponent
        for move in next_move:
            if move['capture'] == False:
                self.no_capture += 1
            else:
                self.no_capture = 0
        # draw: no capture in 50 turns
        if self.no_capture >= 50:
            print('draw')
            return 'draw'
        return False

    def transfer_piece(self, move_dict, make_move=False):

        board1 = self.board1 if move_dict['start_board'] == 1 else self.board2
        board2 = self.board1 if move_dict['end_board'] == 1 else self.board2

        if make_move:
            start_board = board1
            end_board = board2
        else:
            start_board = copy.deepcopy(board1)
            end_board = copy.deepcopy(board2)

        start_move, end_move = move_dict['start_move'], move_dict['end_move']
        player = board1[start_move[0], start_move[1]]
        start_board[start_move[0], start_move[1]] = '.'
        if (player[0] == 'w' and move_dict['end_move'][0] == self.board_size) or (
                player[0] == 'b' and move_dict['end_move'][0] == 1):
            end_board[move_dict['end_move'][0], move_dict['end_move'][1]] = player[:2] + 'k'  # change to king
        else:
            end_board[move_dict['end_move'][0], move_dict['end_move'][1]] = player

        return start_board, end_board

    def get_transferred_list(self, row_dir_list, positions, board, board_num):
        end_board_num = 2 if board_num == 1 else 1
        other_board = self.board2 if board_num == 1 else self.board1
        transfer_move_list = []
        transfer_board_list = []

        for piece in positions:
            list = self.find_orthogonally_neighbors(piece, other_board)
            for move in list:
                to_move = {'start_move': (piece[0], piece[1]), 'start_board': board_num, 'end_move': move,
                           'end_board': end_board_num, 'capture': False}

                new_start_board, new_end_board = self.transfer_piece(to_move)

                second_move_list, second_move_board = self.get_one_move(row_dir_list, [move], new_end_board,
                                                                        end_board_num)
                if len(second_move_list):
                    transfer_board_list.append(second_move_board)
                    for second_move in second_move_list:
                        transfer_move_list.append([to_move, second_move])
        return transfer_move_list, transfer_board_list

    def move_list(self):
        one_move_list_nomarl1, one_move_board_normal1 = self.get_one_move([self.direction], np.concatenate(
            (self.positions['board1']['positions1'], self.positions['board1']['positions2'])), self.board1, 1)
        one_move_list_nomarl2, one_move_board_normal2 = self.get_one_move([self.direction], np.concatenate(
            (self.positions['board2']['positions1'], self.positions['board2']['positions2'])), self.board2, 2)
        one_move_list_king1, one_move_board_king1 = self.get_one_move([1, -1], np.concatenate(
            (self.positions['board1']['king_positions1'], self.positions['board1']['king_positions2'])), self.board1, 1)
        one_move_list_king2, one_move_board_king2 = self.get_one_move([1, -1], np.concatenate(
            (self.positions['board2']['king_positions1'], self.positions['board2']['king_positions2'])), self.board2, 2)
        two_move_list_nomarl1, two_move_board_normal1 = self.get_two_continuous_move(one_move_list_nomarl1,
                                                                                     one_move_board_normal1,
                                                                                     [self.direction])
        two_move_list_nomarl2, two_move_board_normal2 = self.get_two_continuous_move(one_move_list_nomarl2,
                                                                                     one_move_board_normal2,
                                                                                     [self.direction])
        two_move_list_king1, two_move_board_king1 = self.get_two_continuous_move(one_move_list_king1,
                                                                                 one_move_board_king1, [1, -1])
        two_move_list_king2, two_move_board_king2 = self.get_two_continuous_move(one_move_list_king2,
                                                                                 one_move_board_king2, [1, -1])
        transfer_list_nomarl1, transfer_board_normal1 = self.get_transferred_list([self.direction],
                                                                                  self.positions['board1'][
                                                                                      'positions1'], self.board1, 1)
        transfer_list_nomarl2, transfer_board_normal2 = self.get_transferred_list([self.direction],
                                                                                  self.positions['board2'][
                                                                                      'positions2'], self.board2, 2)
        transfer_list_king1, transfer_board_king1 = self.get_transferred_list([1, -1],
                                                                              self.positions['board1'][
                                                                                  'king_positions1'], self.board1, 1)
        transfer_list_king2, transfer_board_king2 = self.get_transferred_list([1, -1],
                                                                              self.positions['board2'][
                                                                                  'king_positions2'], self.board2, 2)
        return {'one_move_each_board': {'board1': one_move_list_nomarl1 + one_move_list_king1,
                                        'board2': one_move_list_nomarl2 + one_move_list_king2},
                'two_moves_one_board': two_move_list_nomarl1 + two_move_list_nomarl2 + two_move_list_king1 + two_move_list_king2,
                'transfer_move_board': transfer_list_nomarl1 + transfer_list_nomarl2 + transfer_list_king1 + transfer_list_king2}


class randomPlayer:
    count_player = 0
    def __init__(self, piece):
        randomPlayer.count_player += 1
        self.name = 'Random'+ str(randomPlayer.count_player)
        self.piece = piece
        self.win_count = 0

    def get_next_move(self, next_move_options):
        mode1_num = len(next_move_options['one_move_each_board']['board1']) * len(
            next_move_options['one_move_each_board']['board2'])
        mode2_num = len(next_move_options['two_moves_one_board'])
        mode3_num = len(next_move_options['transfer_move_board'])
        option_list = [1] * mode1_num + [2] * mode2_num + [3] * mode3_num
        next_move = []
        if option_list:
            next_move_mode = random.choice(option_list)
            if next_move_mode == 1:
                next_move = [random.choice(next_move_options['one_move_each_board']['board1']),
                             random.choice(next_move_options['one_move_each_board']['board2'])]
            elif next_move_mode == 2:
                next_move = random.choice(next_move_options['two_moves_one_board'])
            elif next_move_mode == 3:
                next_move = random.choice(next_move_options['transfer_move_board'])
        return next_move



def one_turn(player, game):
    next_move_options = game.move_list()
    next_move = player.get_next_move(next_move_options)
    game_result = game.check_win(next_move)
    if game_result == 'w' or game_result == 'b':
        player.win_count += 1
        return False
    if game_result == 'draw':
        return False
    print('player:', game.player, 'next_move:', next_move)
    for move in next_move:
        if move['start_board'] != move['end_board']:
            new_board1, new_board2 = game.transfer_piece(move, make_move=True)
        else:
            if move['start_board'] == 1:
                new_board1 = game.update_board_normal(move, make_move=True)
                new_board2 = game.board2
            else:
                new_board2 = game.update_board_normal(move, make_move=True)
                new_board1 = game.board1
    print('=======')
    print(new_board1)
    print(new_board2)
    print('game', game.no_capture)
    return new_board1, new_board2


def one_round(player1, player2, board1, board2, size=4):
    game = GameState(size, player1.piece, board1, board2, 0)
    while True:
        result = one_turn(player1, game)
        if result:
            new_board1, new_board2 = result
            game = GameState(size, player1.piece, new_board1, new_board2, game.no_capture)
        else:
            break

        result = one_turn(player2, game)
        if result:
            new_board1, new_board2 = result
            game = GameState(size, player2.piece, new_board1, new_board2, game.no_capture)
        else:
            break


class MinimaxPlayer:

    def __init__(self, piece):
        self.piece = piece
        self.win_count = 0
        self.lose_count = 0
        self.draw_count = 0
        self.baord1 = None
        self.board2 = None

    def search_moves(self, board1, board2, next_move_options: dict):
        self.baord1 = copy.deepcopy(board1)
        self.baord2 = copy.deepcopy(board2)

        pass

        for key, value in next_move_options.items():
            if not next_move_options:
                return self.heuristic()

    def heuristic(self):
        pass

    def next_moves(self, next_move_options):
        mode1_num = len(next_move_options['one_move_each_board']['board1']) * len(
            next_move_options['one_move_each_board']['board2'])
        mode2_num = len(next_move_options['two_moves_one_board'])
        mode3_num = len(next_move_options['transfer_move_board'])
        option_list = [1] * mode1_num + [2] * mode2_num + [3] * mode3_num
        options = set(option_list)
        next_move = []
        if option_list:
            for next_move_mode in options:
                # next_move_list = random.choice(option_list)
                if next_move_mode == 1:
                    next_move = [random.choice(next_move_options['one_move_each_board']['board1']),
                                 random.choice(next_move_options['one_move_each_board']['board2'])]
                elif next_move_mode == 2:
                    next_move = random.choice(next_move_options['two_moves_one_board'])
                elif next_move_mode == 3:
                    next_move = random.choice(next_move_options['transfer_move_board'])

        return next_move

    def minimax_moves(self, next_move_options):
        pass

    def next_move(self, strateg):
        pass


if __name__ == '__main__':
    # board1 = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
    #                    [1, 'w1', '.', 'w1', '.', 'w1', '.', 1],
    #                    [1, '.', 'w1', '.', 'w1', '.', 'w1', 1],
    #                    [1, '.', '.', '.', '.', '.', '.', 1],
    #                    [1, '.', '.', '.', '.', '.', '.', 1],
    #                    [1, 'b1', '.', 'b1', '.', 'b1', '.', 1],
    #                    [1, '.', 'b1', '.', 'b1', '.', 'b1', 1],
    #                    [1, 1, 1, 1, 1, 1, 1, 1]])
    #
    # board2 = np.array([
    #     [1, 1, 1, 1, 1, 1, 1, 1],
    #     [1, '.', 'w2', '.', 'w2', '.', 'w2', 1],
    #     [1, 'w2', '.', 'w2', '.', 'w2', '.', 1],
    #     [1, '.', '.', '.', '.', '.', '.', 1],
    #     [1, '.', '.', '.', '.', '.', '.', 1],
    #     [1, '.', 'b2', '.', 'b2', '.', 'b2', 1],
    #     [1, 'b2', '.', 'b2', '.', 'b2', '.', 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1]])

    player1 = randomPlayer('w')
    player2 = randomPlayer('b')
    seed = 3
    random.seed(seed)

    size = 4
    for i in range(5):
        print(i)
        board1 = np.array([[1, 1, 1, 1, 1, 1],
                           [1, 'w1', '.', 'w1', '.', 1],
                           [1, '.', '.', '.', '.', 1],
                           [1, '.', '.', '.', '.', 1],
                           [1, '.', 'b1', '.', 'b1', 1],
                           [1, 1, 1, 1, 1, 1]])

        board2 = np.array([[1, 1, 1, 1, 1, 1],
                           [1, '.', 'w2', '.', 'w2', 1],
                           [1, '.', '.', '.', '.', 1],
                           [1, '.', '.', '.', '.', 1],
                           [1, 'b2', '.', 'b2', '.', 1],
                           [1, 1, 1, 1, 1, 1]])
        one_round(player1, player2, board1, board2, size=4)

    print(player1.win_count)
    print(player2.win_count)