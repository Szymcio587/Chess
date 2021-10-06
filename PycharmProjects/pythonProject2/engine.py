class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"p": self.get_pawn_move, "B": self.get_bishop_move, "R": self.get_rook_move,
                              "N": self.get_knight_move, "Q": self.get_queen_move, "K": self.get_king_move}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.isCheck = False
        self.Stalemate = False
        self.Checkmate = False
        self.checks = []
        self.pins = []
        self.anPeasantPossible = ()
        self.currentCastleRights = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currentCastleRights.wk, self.currentCastleRights.wq,
                                             self.currentCastleRights.bk, self.currentCastleRights.bq)]
        self.choice = ""


    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isAnPeasantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.anPeasantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.anPeasantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        self.update_castle_rights(move)
        self.castleRightsLog.append(castleRights(self.currentCastleRights.wk, self.currentCastleRights.wq,
                                             self.currentCastleRights.bk, self.currentCastleRights.bq))

    def undo_move(self):
        if len(self.moveLog):
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isAnPeasantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.anPeasantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.anPeasantPossible = ()

            self.castleRightsLog.pop()
            self.currentCastleRights = castleRights(self.castleRightsLog[-1].wk, self.castleRightsLog[-1].wq,
                                                    self.castleRightsLog[-1].bk, self.castleRightsLog[-1].bq)

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    def update_castle_rights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRights.wk = False
            self.currentCastleRights.wq = False
        elif move.pieceMoved == "bK":
            self.currentCastleRights.bk = False
            self.currentCastleRights.bq = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7 and move.startCol == 0:
                self.currentCastleRights.wq = False
            if move.startRow == 7 and move.startCol == 7:
                self.currentCastleRights.wk = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0 and move.startCol == 0:
                self.currentCastleRights.bq = False
            if move.startRow == 0 and move.startCol == 7:
                self.currentCastleRights.bk = False

    def get_valid_moves(self):
        tempIsAnPeasantPossible = self.anPeasantPossible
        tempCastleRights = castleRights(self.currentCastleRights.wk, self.currentCastleRights.wq,
                                        self.currentCastleRights.bk, self.currentCastleRights.bq)
        moves = []
        self.inCheck, self.pins, self.checks = self.get_pins_and_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow), (checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.get_king_move(kingRow, kingCol, moves)
        else:
            moves = self.get_all_possible_moves()

        if self.whiteToMove:
            self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        self.currentCastleRights = tempCastleRights
        self.anPeasantPossible = tempIsAnPeasantPossible
        if not moves and self.inCheck:
            self.Checkmate = True
            return 1
        elif not moves and not self.inCheck:
            self.Stalemate = True
            return 2
        return moves

    def get_pins_and_checks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "p" and ((enemyColor == "w" and 6 <= j <= 7) or
                                (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (type == "K" and i == 1):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break

        knightMoves = ((-2, 1), (2, -1), (-2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2))
        for d in knightMoves:
            endCol = startCol + d[1]
            endRow = startRow + d[0]
            if 0 <= endCol < 8 and 0 <= endRow < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[1] == "N" and endPiece[0] == enemyColor:
                    checks.append((endRow, endCol, d[0], d[1]))
                    inCheck = True
        return inCheck, pins, checks


    def get_pawn_move(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0 and (not piecePinned or pinDirection == (-1, -1)):
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.anPeasantPossible:
                    moves.append(Move((r,c), (r-1, c-1), self.board, isAnPeasantMove = True))
            if c+1 <= 7 and (not piecePinned or pinDirection == (-1, 1)):
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.anPeasantPossible:
                    moves.append(Move((r,c), (r-1, c+1), self.board, isAnPeasantMove = True))

        else:
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0 and (not piecePinned or pinDirection == (1, -1)):
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.anPeasantPossible:
                    moves.append(Move((r,c), (r+1, c-1), self.board, isAnPeasantMove = True))
            if c+1 <= 7 and (not piecePinned or pinDirection == (1, 1)):
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.anPeasantPossible:
                    moves.append(Move((r,c), (r+1, c+1), self.board, isAnPeasantMove = True))

    def get_rook_move(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endCol = c + d[1] * i
                endRow = r + d[0] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_bishop_move(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endCol = c + d[1] * i
                endRow = r + d[0] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_move(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endCol = c + d[1] * i
                endRow = r + d[0] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_move(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, 1), (2, -1), (-2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            endCol = c + d[1]
            endRow = r + d[0]
            if 0 <= endCol < 8 and 0 <= endRow < 8 and not piecePinned:
                if self.board[endRow][endCol] == "--":
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                elif self.board[endRow][endCol][0] == enemyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def get_king_move(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endCol = c + colMoves[i]
            endRow = r + rowMoves[i]
            if 0 <= endCol < 8 and 0 <= endRow < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.get_pins_and_checks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.whiteToMove and self.currentCastleRights.wk) or (not self.whiteToMove and self.currentCastleRights.bk):
            self.get_kingside_castle(r, c, moves)
        if (self.whiteToMove and self.currentCastleRights.wq) or (not self.whiteToMove and self.currentCastleRights.bq):
            self.get_queenside_castle(r, c, moves)

    def get_kingside_castle(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if (not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2)):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))

    def get_queenside_castle(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))

    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in moves:
            if(move.endRow == r and move.endCol == c):
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                turn = self.board[r][c][0]
                if(turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves


class Move:

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_square, end_square, board, isAnPeasantMove = False, isCastleMove = False):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startCol*1000 + self.startRow * 100 + self.endCol * 10 + self.endRow
        self.isPromotion = ((self.pieceMoved == "wp" and self.endRow == 0) or
                           (self.pieceMoved == "bp" and self.endRow == 7))
        self.isAnPeasantMove = isAnPeasantMove
        self.isCastleMove = isCastleMove
        if self.isAnPeasantMove:
            self.pieceCaptured = "bp" if self.pieceMoved == "wp" else "wp"

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def get_end_row(self):
        return self.endRow

    def get_end_col(self):
        return self.endCol

    def get_start_col(self):
        return self.startCol

    def get_start_row(self):
        return self.startRow

    def notification(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

class castleRights():
    def __init__(self, wk, wq, bk, bq):
        self.wk = wk
        self.wq = wq
        self.bk = bk
        self.bq = bq