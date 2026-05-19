import turtle

loopCount = 0
selectedPiece = None
selectedSquare = None
activeTeam = 'white'
capturedPiece = None
turn_writer = None
selection_marker = None
last_move = None
board = {}
selection_markers = []
fps = 60

BOARD_SIZE = 8
SQUARE_SIZE = 60
FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
BACK_RANK = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
PIECE_SYMBOLS = {
    'pawn': 'P',
    'rook': 'R',
    'knight': 'N',
    'bishop': 'B',
    'queen': 'Q',
    'king': 'K',
}
    #Shapes for chess pieces
def register_piece_shapes():
    turtle.register_shape('pawn', ((8,5),(8,-5),(4,-5),(4,-3),(-1,-3),(-2,-2),(-4,-2),(-5,-1),(-6,-1),(-7,0),(-6,1),(-5,1),(-4,2),(-2,2),(-1,3),(4,3),(4,5),(8,5)))
    turtle.register_shape('rook', ((8,5),(8,-5),(2,-5),(2,-3),(-2,-3),(-2,-5),(-8,-5),(-8,-3),(-2,-3),(-2,-1),(-8,-1),(-8,1),(-2,1),(-2,3),(-8,3),(-8,5),(-2,5),(-2,3),(2,3),(2,5),(8,5)))
    turtle.register_shape('knight', ((8,5),(8,-5),(2,-3),(3,-4),(-1,-2),(-4,-3),(-6,0),(-5,2),(-3,3),(-1,4),(1,5),(8,5)))
    turtle.register_shape('bishop', ((8,3),(8,-3),(4,-3),(4,-1),(1,-1),(0,-2),(-1,-1),(-4,-1),(-5,-2),(-8,0),(-5,2),(-4,1),(-1,1),(0,2),(1,1),(4,1),(4,3),(8,3)))
    turtle.register_shape('queen', ((8, -6), (8, 6), (5, 5), (-4, 8), (-8, 8), (-4, 4), (-10, 0), (-4, -4), (-8, -8), (-4, -8), (5, -5), (8, -6)))
    turtle.register_shape('king', ((8,4),(8,-4),(4,-4),(4,-2),(0,-2),(-1,-3),(-2,-2),(-4,-2),(-5,-3),(-8,0),(-5,3),(-4,2),(-2,2),(-1,3),(0,2),(4,2),(4,4),(8,4)))

    for shape in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
        if shape not in turtle.getshapes():
            turtle.register_shape(shape, ((0, 0),))

    #Chessboard
def draw_board(drawer):
    drawer.penup()
    drawer.hideturtle()
    drawer.speed('fastest')
    start_x = -BOARD_SIZE * SQUARE_SIZE / 2
    start_y = BOARD_SIZE * SQUARE_SIZE / 2

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = start_x + col * SQUARE_SIZE
            y = start_y - row * SQUARE_SIZE
            drawer.goto(x, y)
            drawer.pendown()
            drawer.fillcolor('cornsilk' if (row + col) % 2 == 0 else 'mediumseagreen') #Color of squares
            drawer.begin_fill()
            for _ in range(4):
                drawer.forward(SQUARE_SIZE)
                drawer.right(90)
            drawer.end_fill()
            drawer.penup()


def square_center(square):
    file = square[0]
    rank = int(square[1])
    col = FILES.index(file)
    row = BOARD_SIZE - rank
    x = -BOARD_SIZE * SQUARE_SIZE / 2 + col * SQUARE_SIZE + SQUARE_SIZE / 2
    y = BOARD_SIZE * SQUARE_SIZE / 2 - row * SQUARE_SIZE - SQUARE_SIZE / 2
    return x, y

    #Chess pieces and movement logic
def place_piece(piece_type, color, square, piece_turtles):
    piece = turtle.Turtle()
    piece.penup()
    piece.shape(piece_type)
    piece.color('black')
    piece.fillcolor(color)
    piece.shapesize(1.8, 1.8)
    piece.goto(square_center(square))
    piece.showturtle()
    piece.piece_type = piece_type
    piece.color_name = color
    piece.square = square
    piece.has_moved = False
    piece_turtles.append(piece)
    board[square] = piece

    #Selecting and moving pieces
def coords_to_square(x, y):
    half = BOARD_SIZE * SQUARE_SIZE / 2
    if x < -half or x > half or y < -half or y > half:
        return None
    col = int((x + half) // SQUARE_SIZE)
    row = int((half - y) // SQUARE_SIZE)
    if col < 0 or col >= BOARD_SIZE or row < 0 or row >= BOARD_SIZE:
        return None
    return f"{FILES[col]}{BOARD_SIZE - row}"


def square_to_coords(square):
    col = FILES.index(square[0])
    row = BOARD_SIZE - int(square[1])
    return col, row


def legal_destinations(piece, from_sq):
    dests = []
    for f in FILES:
        for r in range(1, BOARD_SIZE+1):
            to = f + str(r)
            if not is_legal_move(piece, from_sq, to):
                # check en passant possibility for pawns
                if piece.piece_type == 'pawn':
                    sc, sr = square_to_coords(from_sq)
                    tc, tr = square_to_coords(to)
                    if abs(tc - sc) == 1 and tr - sr in (-1, 1):
                        if board.get(to) is None and last_move:
                            last_piece, lm_from, lm_to, lm_two = last_move
                            if lm_two and last_piece.piece_type == 'pawn' and last_piece.color_name != piece.color_name:
                                lm_c, lm_r = square_to_coords(lm_to)
                                if lm_c == tc and lm_r == sr:
                                    # en passant capture square
                                    if not would_cause_check(piece, from_sq, to):
                                        dests.append(to)
                continue
            if not would_cause_check(piece, from_sq, to):
                dests.append(to)
    return dests


def coords_to_square_str(col, row):
    if col < 0 or col >= BOARD_SIZE or row < 0 or row >= BOARD_SIZE:
        return None
    return f"{FILES[col]}{BOARD_SIZE - row}"


def sign(v):
    return 0 if v == 0 else (1 if v > 0 else -1)


def squares_between(start, end):
    sc, sr = square_to_coords(start)
    ec, er = square_to_coords(end)
    dc = sign(ec - sc)
    dr = sign(er - sr)
    if dc != 0 and dr != 0 and abs(ec - sc) != abs(er - sr):
        return None
    squares = []
    c = sc + dc
    r = sr + dr
    while c != ec or r != er:
        squares.append(coords_to_square_str(c, r))
        c += dc
        r += dr
    return squares


def is_path_clear(start, end):
    between = squares_between(start, end)
    if between is None:
        return False
    return all(board.get(s) is None for s in between)


def is_legal_move(piece, from_sq, to_sq):
    if from_sq == to_sq:
        return False
    target = board.get(to_sq)
    if target and target.color_name == piece.color_name:
        return False

    ptype = piece.piece_type
    sc, sr = square_to_coords(from_sq)
    ec, er = square_to_coords(to_sq)
    dc = ec - sc
    dr = er - sr

    if ptype == 'pawn':
        direction = -1 if piece.color_name == 'white' else 1
        start_row = 6 if piece.color_name == 'white' else 1
        #Forward
        if dc == 0:
            if dr == direction and target is None:
                return True
            if dr == 2 * direction and sr == start_row:
                mid = coords_to_square_str(sc, sr + direction)
                return target is None and board.get(mid) is None
            return False
        #Capture
        if abs(dc) == 1 and dr == direction and target is not None:
            return True
        return False

    if ptype == 'rook':
        if dc == 0 or dr == 0:
            return is_path_clear(from_sq, to_sq)
        return False

    if ptype == 'bishop':
        if abs(dc) == abs(dr):
            return is_path_clear(from_sq, to_sq)
        return False

    if ptype == 'queen':
        if dc == 0 or dr == 0 or abs(dc) == abs(dr):
            return is_path_clear(from_sq, to_sq)
        return False

    if ptype == 'king':
        #Allow normal one-square king moves
        if max(abs(dc), abs(dr)) == 1:
            return True
        #Allow castling attempt (two-square horizontal)
        if dr == 0 and abs(dc) == 2:
            return can_castle(piece, from_sq, to_sq)
        return False

    if ptype == 'knight':
        return (abs(dc), abs(dr)) in [(1, 2), (2, 1)]

    return False


def can_castle(king, from_sq, to_sq):
    #King must not have moved
    if king.has_moved:
        return False
    sc, sr = square_to_coords(from_sq)
    ec, er = square_to_coords(to_sq)
    if sr != er:
        return False
    direction = 1 if ec > sc else -1
    #Find rook at the end in that row
    rook_col = 7 if direction == 1 else 0
    rook_sq = coords_to_square_str(rook_col, sr)
    rook = board.get(rook_sq)
    if not rook or rook.piece_type != 'rook' or rook.color_name != king.color_name or getattr(rook, 'has_moved', False):
        return False
    #Squares between must be empty
    between = squares_between(from_sq, rook_sq)
    if between is None:
        return False
    if any(board.get(s) is not None for s in between):
        return False
    #King cannot be in check, pass through check, or land in check
    opponent = 'black' if king.color_name == 'white' else 'white'
    #Squares king traverses: from_sq, plus one step, and destination
    traverse_cols = [sc, sc + direction, sc + 2 * direction]
    for c in traverse_cols:
        sq = coords_to_square_str(c, sr)
        if is_square_attacked(sq, opponent):
            return False
    return True


def find_king(color):
    for sq, p in board.items():
        if p.piece_type == 'king' and p.color_name == color:
            return sq
    return None


def is_square_attacked(square, by_color):
    #Pawn attacks are directional
    for sq, p in board.items():
        if p.color_name != by_color:
            continue
        ptype = p.piece_type
        sc, sr = square_to_coords(sq)
        tc, tr = square_to_coords(square)
        dc = tc - sc
        dr = tr - sr
        if ptype == 'pawn':
            direction = -1 if p.color_name == 'white' else 1
            if dr == direction and abs(dc) == 1:
                return True
            continue
        if ptype == 'knight':
            if (abs(dc), abs(dr)) in [(1, 2), (2, 1)]:
                return True
            continue
        if ptype == 'king':
            if max(abs(dc), abs(dr)) == 1:
                return True
            continue
        #Sliding pieces: rook/bishop/queen
        if ptype in ('rook', 'bishop', 'queen'):
            #Reuse is_legal_move for path validation but avoid recursion on castling
            if is_legal_move(p, sq, square):
                return True
    return False


def would_cause_check(piece, from_sq, to_sq):
    #Simulate move and see if own king is attacked
    orig_to = board.get(to_sq)
    orig_from = board.get(from_sq)
    # handle en passant simulation
    ep_captured = None
    sc, sr = square_to_coords(from_sq)
    ec, er = square_to_coords(to_sq)
    if piece.piece_type == 'pawn' and abs(ec - sc) == 1 and orig_to is None:
        #Possible en passant
        if last_move:
            last_piece, lm_from, lm_to, lm_two = last_move
            if lm_two and last_piece.piece_type == 'pawn' and last_piece.color_name != piece.color_name:
                lm_c, lm_r = square_to_coords(lm_to)
                if lm_c == ec and lm_r == sr:
                    ep_captured = last_piece
                    board.pop(lm_to, None)

    #Perform move
    board.pop(from_sq, None)
    board[to_sq] = piece
    piece.square = to_sq

    #Find king square
    if piece.piece_type == 'king':
        king_sq = to_sq
    else:
        king_sq = find_king(piece.color_name)

    opponent = 'black' if piece.color_name == 'white' else 'white'
    attacked = is_square_attacked(king_sq, opponent)

    #Revert
    board.pop(to_sq, None)
    if orig_to:
        board[to_sq] = orig_to
        orig_to.square = to_sq
    board[from_sq] = orig_from
    if orig_from:
        orig_from.square = from_sq
    if ep_captured:
        #Restore en passant captured pawn at lm_to
        board[last_move[2]] = ep_captured
        ep_captured.square = last_move[2]

    return attacked


def clear_selection():
    global selectedPiece, selectedSquare
    if selectedPiece:
        selectedPiece.shapesize(1.8, 1.8)
    selectedPiece = None
    selectedSquare = None
    #Hide and remove any move markers
    global selection_markers
    for m in selection_markers:
        try:
            m.hideturtle()
            m.clear()
        except Exception:
            pass
    selection_markers = []


def select_piece(piece, square):
    global selectedPiece, selectedSquare
    clear_selection()
    selectedPiece = piece
    selectedSquare = square
    selectedPiece.shapesize(2.2, 2.2)
    # show markers for all legal destinations
    dests = legal_destinations(piece, square)
    global selection_markers
    for to in dests:
        m = turtle.Turtle()
        m.hideturtle()
        m.penup()
        m.speed('fastest')
        m.shape('circle')
        m.color('gray')
        m.shapesize(0.45, 0.45)
        m.goto(square_center(to))
        m.showturtle()
        selection_markers.append(m)
    turtle.Screen().update()


def toggle_active_team():
    global activeTeam
    activeTeam = 'black' if activeTeam == 'white' else 'white'


def update_turn_display(writer):
    writer.clear()
    writer.hideturtle()
    writer.penup()
    writer.goto(0, BOARD_SIZE * SQUARE_SIZE / 2 + 20)
    writer.write(f"{activeTeam.capitalize()}\'s turn", align='center', font=('Arial', 16, 'bold'))


def on_click(x, y):
    square = coords_to_square(x, y)
    if square is None:
        return

    piece = board.get(square)
    global capturedPiece, last_move

    if selectedPiece is None:
        if piece and piece.color_name == activeTeam:
            select_piece(piece, square)
        return

    if square == selectedSquare:
        clear_selection()
        return

    #Validate move
    if not is_legal_move(selectedPiece, selectedSquare, square):
        clear_selection()
        return

    #Don't allow moves that leave own king in check
    if would_cause_check(selectedPiece, selectedSquare, square):
        clear_selection()
        return

    #En passant capture
    sc, sr = square_to_coords(selectedSquare)
    ec, er = square_to_coords(square)
    if selectedPiece.piece_type == 'pawn' and abs(ec - sc) == 1 and board.get(square) is None:
        #Check last move was a two-square pawn move from adjacent file
        if last_move:
            last_piece, lm_from, lm_to, lm_two = last_move
            if lm_two and last_piece.piece_type == 'pawn' and last_piece.color_name != selectedPiece.color_name:
                lm_c, lm_r = square_to_coords(lm_to)
                #Captured pawn is on same file as target and same row as start
                if lm_c == ec and lm_r == sr:
                    #Capture the pawn
                    last_piece.hideturtle()
                    board.pop(lm_to, None)

    #Capture normal target
    if piece and piece.color_name != selectedPiece.color_name:
        capturedPiece = piece
        capturedPiece.hideturtle()
        board.pop(square, None)

    #Move piece
    board.pop(selectedSquare, None)
    selectedPiece.goto(square_center(square))
    selectedPiece.square = square
    board[square] = selectedPiece

    #Castling
    if selectedPiece.piece_type == 'king':
        sc, sr = square_to_coords(selectedSquare)
        ec, er = square_to_coords(square)
        if abs(ec - sc) == 2:
            direction = 1 if ec > sc else -1
            rook_col = 7 if direction == 1 else 0
            rook_sq = coords_to_square_str(rook_col, sr)
            rook = board.pop(rook_sq, None)
            if rook:
                new_rook_col = sc + direction
                new_rook_sq = coords_to_square_str(new_rook_col, sr)
                rook.goto(square_center(new_rook_sq))
                rook.square = new_rook_sq
                board[new_rook_sq] = rook
                rook.has_moved = True

    #Promotion
    if selectedPiece.piece_type == 'pawn':
        #White promotes on rows 8 (rows 0), black on rows 1 (rows 7)
        if (selectedPiece.color_name == 'white' and square[1] == '8') or (selectedPiece.color_name == 'black' and square[1] == '1'):
            choice = screen.textinput('Promotion', 'Promote to (q,r,b,n):')
            if choice:
                ch = choice.strip().lower()
                mapping = {'q':'queen','r':'rook','b':'bishop','n':'knight'}
                new_type = mapping.get(ch, 'queen')
                selectedPiece.piece_type = new_type
                try:
                    selectedPiece.shape(new_type)
                except Exception:
                    pass

    #Update move flags
    moved_two = False
    if selectedPiece.piece_type == 'pawn':
        if abs(er - sr) == 2:
            moved_two = True

    selectedPiece.has_moved = True
    last_move = (selectedPiece, selectedSquare, square, moved_two)

    clear_selection()
    toggle_active_team()
    update_turn_display(turn_writer)


def setup_pieces():
    pieces = []

    # Black pieces on rows 7 and 8
    for index, piece_type in enumerate(BACK_RANK):
        square = f"{FILES[index]}8"
        place_piece(piece_type, 'black', square, pieces)
    for index in range(BOARD_SIZE):
        square = f"{FILES[index]}7"
        place_piece('pawn', 'black', square, pieces)

    # White pieces on rows 1 and 2
    for index in range(BOARD_SIZE):
        square = f"{FILES[index]}2"
        place_piece('pawn', 'white', square, pieces)
    for index, piece_type in enumerate(BACK_RANK):
        square = f"{FILES[index]}1"
        place_piece(piece_type, 'white', square, pieces)

    return pieces

if __name__ == '__main__':
    screen = turtle.Screen()
    screen.title('Chessboard')
    screen.bgcolor('white')
    screen.setup(width=700, height=700)
    screen.tracer(0)

    register_piece_shapes()

    drawer = turtle.Turtle()
    draw_board(drawer)
    pieces = setup_pieces()

    selection_markers = []

    turn_writer = turtle.Turtle()
    update_turn_display(turn_writer)

    screen.onclick(on_click)
    screen.listen()
    screen.tracer(1)
    screen.mainloop()
