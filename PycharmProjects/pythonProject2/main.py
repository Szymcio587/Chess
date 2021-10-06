import pygame as p
import engine, time

p.font.init()

LIGHT, DARK, GREEN, RED, BLACK, WHITE = (255, 230, 204), (191, 128, 64), (0, 128, 0), (176, 28, 28), (0, 0, 0), (255, 255, 255)
D_BLUE, L_BLUE = (0, 36, 218), (0, 109, 218)
WIDTH, HEIGHT = 712, 512
DIM = 8
SQUARE_SIZE = HEIGHT // DIM
IMAGES = {}
MAX_FPS = 30
colors = [LIGHT, DARK]
FONT = p.font.SysFont('arial', 25)
FONT_L = p.font.SysFont('arial', 12)
START_TIME, TIME_INC = 5, 3


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def draw_game_state(screen, gs, possibleMoves, squareSelected, white_time_text, black_time_text, win, draw, promotion):
    draw_board(screen, white_time_text, black_time_text, win, draw)
    highlight(screen, gs, possibleMoves, squareSelected, promotion)
    draw_pieces(screen, gs.board)

def highlight(screen, gs, possibleMoves, squareSelected, promotion):
    if squareSelected != ():
        try:
            r, c = squareSelected
            if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
                s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(GREEN)
                screen.blit(s, (c*SQUARE_SIZE, r*SQUARE_SIZE))
                for move in possibleMoves:
                    if (move.startRow == r and move.startCol == c and gs.board[move.endRow][move.endCol][0] == "-"):
                        s.fill(GREEN)
                        p.draw.circle(screen, GREEN, (move.endCol*SQUARE_SIZE+32, move.endRow*SQUARE_SIZE+32), 4)
                    elif (move.startRow == r and move.startCol == c and gs.board[move.endRow][move.endCol][0] ==
                         ("b" if gs.whiteToMove else "w")):
                        s.fill(RED)
                        screen.blit(s, (move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE))
        except IndexError:
            pass

def draw_board(screen, white_time_text, black_time_text, win, draw):
    for c in range(DIM):
        for r in range(DIM):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    p.draw.rect(screen, RED, p.Rect(512, 0, 3, 512))
    p.draw.rect(screen, WHITE, p.Rect(515, 0, 197, 512))
    screen.blit(white_time_text, (540, 20))
    screen.blit(black_time_text, (540, 420))
    if win == 1:
        text = FONT_L.render("Black has won! Press r to reset the game", True, BLACK)
        screen.blit(text, (520, 220))
    if win == 2:
        text = FONT_L.render("White has won! Press r to reset the game", True, BLACK)
        screen.blit(text, (520, 220))
    if draw:
        text = FONT_L.render("Draw! Press r to reset the game", True, BLACK)
        screen.blit(text, (520, 220))

def draw_pieces(screen, board):
    for c in range(DIM):
        for r in range(DIM):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def move_animation(move, screen, board, clock, white_time_text, black_time_text, win, draw):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FPS = 4
    frameCount = max(abs(dR), abs(dC)) * FPS
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        draw_board(screen, white_time_text, black_time_text, win, draw)
        draw_pieces(screen, board)
        color = colors[(move.endCol + move.endRow)%2]
        endSquare = p.Rect(move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def main():
    load_images()
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(LIGHT))

    possibleMoves = []
    squareSelected = ()
    playerClicks = []
    gs = engine.GameState()
    validMoves = gs.get_valid_moves()

    moveMade = False
    running = True
    animate = False
    promotion = False
    draw = False
    win = 0

    start = time.time()
    time_log = []
    white_time_m, white_time_s, black_time_m, black_time_s = START_TIME, 0, START_TIME, 0

    while running:

        white_time_text = FONT.render(str(white_time_m) + ":" + str(white_time_s), True, BLACK)
        black_time_text = FONT.render(str(black_time_m) + ":" + str(black_time_s), True, BLACK)

        end = time.time()

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not win and not draw:
                mouse_loc = p.mouse.get_pos()
                col = mouse_loc[0] // SQUARE_SIZE
                row = mouse_loc[1] // SQUARE_SIZE
                try:
                    if squareSelected == (row, col):
                        squareSelected = ()
                        playerClicks = []
                        possibleMoves.clear()
                    if squareSelected or gs.board[row][col] != "--":
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                        for move in validMoves:
                            if row == move.get_start_row() and col == move.get_start_col():
                                possibleMoves.append(move)
                    if len(playerClicks) == 2:
                        move = engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.make_move(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks.clear()
                            playerClicks.append(squareSelected)
                            possibleMoves.clear()
                            for move in validMoves:
                                if row == move.get_start_row() and col == move.get_start_col():
                                    possibleMoves.append(move)
                except IndexError:
                    pass

            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE:
                    gs.undo_move()
                    win = 0
                    draw = False
                    promotion = False
                    moveMade = True
                    animate = False
                    if time_log:
                        time_log.pop()
                    if time_log:
                        white_time_m, white_time_s, black_time_m, black_time_s = time_log[-1][0], time_log[-1][1], time_log[-1][2], time_log[-1][3]
                    else:
                        white_time_m, white_time_s, black_time_m, black_time_s = START_TIME, 0, START_TIME, 0
                if e.key == p.K_r:
                    gs = engine.GameState()
                    validMoves = gs.get_valid_moves()
                    playerClicks = []
                    squareSelected = ()
                    draw = False
                    win = 0
                    promotion = False
                    moveMade = False
                    white_time_m, white_time_s, black_time_m, black_time_s = START_TIME, 0, START_TIME, 0

        if moveMade:
            if animate:
                move_animation(move, screen, gs.board, clock, white_time_text, black_time_text, win, draw)
                time_log.append((white_time_m, white_time_s, black_time_m, black_time_s))
            if gs.whiteToMove:
                white_time_s += TIME_INC
                if white_time_s > 59:
                    white_time_s -= 60
                    white_time_m += 1
            else:
                black_time_s += TIME_INC
                if black_time_s > 59:
                    black_time_s -= 60
                    black_time_m += 1
            possibleMoves.clear()
            validMoves = gs.get_valid_moves()
            moveMade = False
            print(move.notification())
            animate = False
            promotion = False

        if not win and not draw:
            if (not gs.whiteToMove and end-start>=1):
                start = end
                if white_time_s:
                    white_time_s -= 1
                else:
                    white_time_s = 59
                    white_time_m -= 1
            elif (gs.whiteToMove and end-start>=1):
                start = end
                if black_time_s:
                    black_time_s = black_time_s - 1
                else:
                    black_time_s = 59
                    black_time_m = black_time_m - 1

        if validMoves == 1 or (black_time_s == 0 and black_time_m == 0) or (white_time_m == 0 and white_time_s == 0):
            if gs.whiteToMove:
                win = 1
            else:
                win = 2
        elif validMoves == 2:
            draw = True

        clock.tick(MAX_FPS)
        draw_game_state(screen, gs, possibleMoves, squareSelected, white_time_text, black_time_text, win, draw, promotion)
        p.display.flip()


if __name__ == "__main__":
    main()
