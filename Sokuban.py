import numpy as np
import os
import pygame
import json # <--- THƯ VIỆN MỚI ĐỂ LƯU DATA CHUYÊN NGHIỆP HƠN
import hill_climbing 

# --- Cấu hình đường dẫn ---
current_dir = os.path.dirname(__file__)
path_board = os.path.abspath(os.path.join(current_dir, 'Testcases'))
path_checkpoint = os.path.abspath(os.path.join(current_dir, 'Checkpoints'))
assets_path = os.path.join(current_dir, 'Assets')
path_save = os.path.join(current_dir, 'savegame.json') # <--- ĐỔI THÀNH FILE JSON

def get_boards():
    if not os.path.exists(path_board): return []
    files = [f for f in os.listdir(path_board) if f.endswith(".txt")]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(ch.isdigit() for ch in x) else 0)
    return [get_board(os.path.join(path_board, f)) for f in files]

def get_check_points():
    if not os.path.exists(path_checkpoint): return []
    files = [f for f in os.listdir(path_checkpoint) if f.endswith(".txt")]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(ch.isdigit() for ch in x) else 0)
    return [np.loadtxt(os.path.join(path_checkpoint, f), dtype=int, delimiter=',', ndmin=2) for f in files]

def get_board(path):
    result = np.loadtxt(path, dtype=str, delimiter=',', ndmin=2)
    new_board = np.full(result.shape, ' ', dtype=object)
    
    for r in range(len(result)):
        for c in range(len(result[r])):
            val = str(result[r][c]).strip().lower()
            if val == '1': new_board[r][c] = '#'
            elif val == 'p': new_board[r][c] = '@'
            elif val == 'b': new_board[r][c] = '$'
            elif val in ['c', '0']: new_board[r][c] = '%'
            else: new_board[r][c] = ' '
    return new_board

# --- HỆ THỐNG LƯU TRỮ NÂNG CẤP BẰNG JSON ---
def load_game_data():
    default_data = {
        "max_level": 0,
        "high_scores": {}, 
        "total_deaths": 0,
        "total_wins": 0
    }
    if not os.path.exists(path_save):
        return default_data
    try:
        with open(path_save, 'r') as f:
            return json.load(f)
    except:
        return default_data

def save_game_data(data):
    with open(path_save, 'w') as f:
        json.dump(data, f, indent=4)

# --- Khởi tạo dữ liệu ---
maps = get_boards()
check_points = get_check_points()
game_data = load_game_data() # Load data ngay khi mở game

pygame.init()
SCREEN_W = 950
SCREEN_H = 750
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption('Sokoban - Among-koban NHOM 2')
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE_BTN = (30, 144, 255)
RED_BTN = (220, 20, 60)
BTN_WOOD_COLOR = (184, 115, 51) 

PLAY_BUTTON_RECT = pygame.Rect(250, 680, 180, 50)
AI_BUTTON_RECT = pygame.Rect(520, 680, 180, 50)

SUB_BTN_W = 320
SUB_BTN_H = 50
SUB_CENTER_X = SCREEN_W // 2 - SUB_BTN_W // 2

NEW_GAME_RECT = pygame.Rect(SUB_CENTER_X, 180, SUB_BTN_W, SUB_BTN_H)
CONTINUE_RECT = pygame.Rect(SUB_CENTER_X, 250, SUB_BTN_W, SUB_BTN_H)
SETTINGS_RECT = pygame.Rect(SUB_CENTER_X, 320, SUB_BTN_W, SUB_BTN_H)
HIGH_SCORES_RECT = pygame.Rect(SUB_CENTER_X, 390, SUB_BTN_W, SUB_BTN_H)
ACHIEVEMENTS_RECT = pygame.Rect(SUB_CENTER_X, 460, SUB_BTN_W, SUB_BTN_H)
EXIT_MENU_RECT = pygame.Rect(SUB_CENTER_X, 530, SUB_BTN_W, SUB_BTN_H)

PLAY_SELECT_RECT = pygame.Rect(SCREEN_W//2 - 160, 660, 140, 50)
BACK_SELECT_RECT = pygame.Rect(SCREEN_W//2 + 20, 660, 140, 50)
BACK_INFO_RECT = pygame.Rect(SCREEN_W//2 - 100, 650, 200, 50)

RESTART_BTN_RECT = pygame.Rect(SCREEN_W - 130, 20, 100, 40)
QUIT_BTN_RECT = pygame.Rect(SCREEN_W - 250, 20, 100, 40)

def load_img(name, size=(32,32)):
    try: 
        img = pygame.image.load(os.path.join(assets_path, name))
        return pygame.transform.scale(img, size)
    except: 
        s = pygame.Surface(size); s.fill((100,100,100)); return s

player = load_img('player.png')
wall = load_img('wall.png')
box = load_img('box.png')
point = load_img('point.png')
space = load_img('space.png')
arrow_left = load_img('arrow_left.png', (40, 40))
arrow_right = load_img('arrow_right.png', (40, 40))

init_background = load_img('init_background.png', (SCREEN_W, SCREEN_H))
loading_background = load_img('loading_background.png', (SCREEN_W, SCREEN_H))
found_background = load_img('found_background.png', (SCREEN_W, SCREEN_H))
notfound_background = load_img('notfound_background.png', (SCREEN_W, SCREEN_H))

# Thêm Load Âm Thanh (Chỉ khởi tạo, bạn cần có file để nó chạy)
try:
    pygame.mixer.init()
    # Tải nhạc nền nếu có file 'bgm.mp3' trong Assets
    # pygame.mixer.music.load(os.path.join(assets_path, 'bgm.mp3'))
    # pygame.mixer.music.play(-1)
except:
    pass

def get_font(size):
    font_path = os.path.join(assets_path, 'gameFont.ttf') 
    try:
        return pygame.font.Font(font_path, size)
    except:
        return pygame.font.SysFont('Arial', size, bold=True)

font_title = get_font(60)
font_level = get_font(35)
font_btn = get_font(22)
font_guide = get_font(20)

def renderMap(board, indent_y=250): 
    if board is None: return
    width, height = len(board[0]), len(board)
    indent_x = (SCREEN_W - width * 32) / 2.0
    
    for i in range(height):
        for j in range(width):
            ch = str(board[i][j]).strip().lower() 
            pos = (j * 32 + indent_x, i * 32 + indent_y)
            screen.blit(space, pos)
            if ch in ['#', '1']: screen.blit(wall, pos)
            elif ch in ['$', 'b', '*', 's']: screen.blit(box, pos)
            elif ch in ['%', 'c']: screen.blit(point, pos)
            elif ch in ['@', 'p', '+']: screen.blit(player, pos)

def is_deadlock(board):
    for r in range(len(board)):
        for c in range(len(board[0])):
            val = str(board[r][c]).strip().lower()
            if val in ['$', 'b']:
                up = board[r-1][c] in ['#', '1'] if r > 0 else True
                down = board[r+1][c] in ['#', '1'] if r < len(board)-1 else True
                left = board[r][c-1] in ['#', '1'] if c > 0 else True
                right = board[r][c+1] in ['#', '1'] if c < len(board[0])-1 else True
                if (up or down) and (left or right):
                    return True
    return False

mapNumber = 0
sceneState = "init"
current_board = None
player_checkpoints = set()

def move_player(board, dr, dc, checkpoints):
    r, c = -1, -1
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] in ['@', '+', 'p']: 
                r, c = row, col
                break
    if r == -1: return False, False

    nr, nc = r + dr, c + dc
    if not (0 <= nr < len(board) and 0 <= nc < len(board[0])): return False, False
    if board[nr][nc] in ['#', '1']: return False, False

    if board[nr][nc] in [' ', '%', 'c']:
        board[r][c] = '%' if (r, c) in checkpoints else ' '
        board[nr][nc] = '+' if (nr, nc) in checkpoints else '@'
        return True, False 

    if board[nr][nc] in ['$', '*', 'b']:
        nnr, nnc = nr + dr, nc + dc
        if 0 <= nnr < len(board) and 0 <= nnc < len(board[0]) and board[nnr][nnc] in [' ', '%', 'c']:
            board[nnr][nnc] = '*' if (nnr, nnc) in checkpoints else '$'
            board[nr][nc] = '+' if (nr, nc) in checkpoints else '@'
            board[r][c] = '%' if (r, c) in checkpoints else ' '
            return True, True 
    return False, False

def initGame(map_data):
    screen.blit(init_background, (0, 0))
    txt_title = font_title.render('Among-koban', True, WHITE)
    screen.blit(txt_title, txt_title.get_rect(center=(SCREEN_W//2, 80)))
    
    txt_guide = font_guide.render('Chon ban do di nao!!!', True, WHITE)
    screen.blit(txt_guide, txt_guide.get_rect(center=(SCREEN_W//2, 140)))
    
    txt_lv = font_level.render(f"Lv.{mapNumber + 1}", True, WHITE)
    lv_rect = txt_lv.get_rect(center=(SCREEN_W//2, 195))
    screen.blit(txt_lv, lv_rect)
    screen.blit(arrow_left, (lv_rect.left - 60, lv_rect.top))
    screen.blit(arrow_right, (lv_rect.right + 20, lv_rect.top))
    
    renderMap(map_data, indent_y=260)
    
    pygame.draw.rect(screen, BLUE_BTN, PLAY_BUTTON_RECT, border_radius=12)
    t_play = font_btn.render('CHOI TAY', True, WHITE)
    screen.blit(t_play, t_play.get_rect(center=PLAY_BUTTON_RECT.center))
    pygame.draw.rect(screen, RED_BTN, AI_BUTTON_RECT, border_radius=12)
    t_ai = font_btn.render('CHAY AI', True, WHITE)
    screen.blit(t_ai, t_ai.get_rect(center=AI_BUTTON_RECT.center))

def draw_sub_menu_btn(rect, text):
    pygame.draw.rect(screen, BTN_WOOD_COLOR, rect, border_radius=8)
    pygame.draw.rect(screen, (100, 50, 20), rect, 2, border_radius=8)
    txt_surf = font_btn.render(text, True, WHITE)
    screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

def playerMenuGame():
    screen.blit(init_background, (0, 0))
    txt_title = font_title.render('SOKOBAN', True, WHITE)
    screen.blit(txt_title, txt_title.get_rect(center=(SCREEN_W//2, 80)))
    
    draw_sub_menu_btn(NEW_GAME_RECT, 'New game')
    draw_sub_menu_btn(CONTINUE_RECT, 'Continue game')
    draw_sub_menu_btn(SETTINGS_RECT, 'Settings')
    draw_sub_menu_btn(HIGH_SCORES_RECT, 'High scores')
    draw_sub_menu_btn(ACHIEVEMENTS_RECT, 'Achievements')
    draw_sub_menu_btn(EXIT_MENU_RECT, 'Back to Main Menu')

def mapSelectionGame(map_data):
    screen.blit(init_background, (0, 0))
    txt_title = font_title.render('Chon ban do di nao', True, WHITE)
    screen.blit(txt_title, txt_title.get_rect(center=(SCREEN_W//2, 60)))
    
    # Hiển thị kỷ lục nếu đã từng qua màn này
    best_score_text = 'Chua co ky luc'
    level_key = str(mapNumber)
    if level_key in game_data['high_scores']:
        best = game_data['high_scores'][level_key]
        best_score_text = f"Best: {best['moves']} moves, {best['pushes']} pushes"
        
    txt_score = font_guide.render(best_score_text, True, (255, 215, 0)) # Màu vàng
    screen.blit(txt_score, txt_score.get_rect(center=(SCREEN_W//2, 100)))

    txt_guide = font_guide.render('Phim <- -> chon ban do.', True, WHITE)
    screen.blit(txt_guide, txt_guide.get_rect(center=(SCREEN_W//2, 130)))
    
    txt_lv = font_level.render(f"Lv.{mapNumber + 1}", True, WHITE)
    lv_rect = txt_lv.get_rect(center=(SCREEN_W//2, 185))
    screen.blit(txt_lv, lv_rect)
    screen.blit(arrow_left, (lv_rect.left - 60, lv_rect.top))
    screen.blit(arrow_right, (lv_rect.right + 20, lv_rect.top))
        
    renderMap(map_data, indent_y=260)
    
    draw_sub_menu_btn(PLAY_SELECT_RECT, 'Play')
    draw_sub_menu_btn(BACK_SELECT_RECT, 'Back')

def drawInfoScreen(title, lines):
    screen.blit(init_background, (0, 0))
    txt_title = font_title.render(title, True, WHITE)
    screen.blit(txt_title, txt_title.get_rect(center=(SCREEN_W//2, 80)))
    
    # Vẽ các dòng thông tin, đẩy lên một chút để không bị che nút Back
    start_y = 180
    for i, line in enumerate(lines):
        txt = font_level.render(line, True, WHITE)
        screen.blit(txt, txt.get_rect(center=(SCREEN_W//2, start_y + i * 50)))
        
    draw_sub_menu_btn(BACK_INFO_RECT, 'Back')

def loadingGame():
    screen.blit(loading_background, (0, 0))
    t1 = font_title.render('SHHHHHHH!', True, WHITE)
    t2 = font_guide.render('DOI XIU NHA, DANG MAN NE!', True, WHITE)
    screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, 100)))
    screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, 160)))

def foundGame(map_data):
    screen.blit(found_background, (0, 0))
    t_vic = font_btn.render('QUA DE, MAN XONG RUI NE!!!', True, WHITE)
    screen.blit(t_vic, t_vic.get_rect(center=(SCREEN_W//2, 130)))
    
    renderMap(map_data, indent_y=280)
    
    t_next = font_btn.render('NHAN ENTER DE TIP TUC NHO..', True, WHITE)
    screen.blit(t_next, t_next.get_rect(center=(SCREEN_W//2, 660)))

def gameOverScreen(map_data, reason="deadlock"):
    screen.blit(notfound_background, (0, 0))
    
    if reason == "timeout":
        t1 = font_btn.render('Het gio roi! Nhanh tay len nhe!', True, WHITE)
    else:
        t1 = font_btn.render('Ban thua roi. Lan sau co len nhe', True, WHITE)
        
    t2 = font_guide.render('Nhan ENTER de quay lai chon Level', True, (220, 220, 220))
    
    screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, 130)))
    renderMap(map_data, indent_y=280)
    screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, 660)))

def sokoban():
    global sceneState, mapNumber, current_board, player_checkpoints, game_data
    running = True
    list_board = []
    currentState = 0
    playing_mode = None  
    
    current_info_title = ""
    current_info_lines = []
    game_over_reason = "deadlock" 

    moves = 0
    pushes = 0
    start_time = 0
    TIME_LIMIT = 300 

    while running:
        screen.fill((0,0,0)) 

        if sceneState == "init":
            initGame(maps[mapNumber] if maps else [])
        elif sceneState == "player_menu":
            playerMenuGame()
        elif sceneState == "map_selection":
            mapSelectionGame(maps[mapNumber] if maps else [])
        elif sceneState == "info_screen":
            drawInfoScreen(current_info_title, current_info_lines)
        elif sceneState == "loading":
            loadingGame()
            pygame.display.flip()
            cp = check_points[mapNumber] if mapNumber < len(check_points) else []
            list_board = hill_climbing.Hill_Climbing_Search(maps[mapNumber], cp)
            if list_board and len(list_board) > 0:
                sceneState = "ai_playing"
                currentState = 0
                playing_mode = "ai"  
            else:
                sceneState = "init"
                print("AI: No solution found.")
        elif sceneState == "ai_playing":
            clock.tick(4) 
            if currentState < len(list_board):
                current_board = list_board[currentState]
                renderMap(current_board, indent_y=260)
                currentState += 1
            else:
                sceneState = "end"
        elif sceneState == "playing":
            if current_board is None:
                current_board = [list(row) for row in maps[mapNumber]]
                player_checkpoints = set()
                for r in range(len(current_board)):
                    for c in range(len(current_board[0])):
                        val = str(current_board[r][c]).strip().lower()
                        if val in ['%', 'c']: player_checkpoints.add((r, c))
                if mapNumber < len(check_points):
                    for p in check_points[mapNumber]: player_checkpoints.add((int(p[0]), int(p[1])))
                
                moves = 0
                pushes = 0
                start_time = pygame.time.get_ticks()

            renderMap(current_board, indent_y=260)

            elapsed_secs = (pygame.time.get_ticks() - start_time) // 1000
            remaining_secs = TIME_LIMIT - elapsed_secs
            
            if remaining_secs <= 0:
                remaining_secs = 0
                sceneState = "game_over"
                game_over_reason = "timeout" 
                
                game_data["total_deaths"] += 1
                save_game_data(game_data)

            txt_lv = font_level.render(f'Level: {mapNumber + 1}', True, WHITE)
            screen.blit(txt_lv, (30, 20))

            pygame.draw.rect(screen, BTN_WOOD_COLOR, QUIT_BTN_RECT, border_radius=8)
            t_quit = font_guide.render('Quit', True, WHITE)
            screen.blit(t_quit, t_quit.get_rect(center=QUIT_BTN_RECT.center))

            pygame.draw.rect(screen, BTN_WOOD_COLOR, RESTART_BTN_RECT, border_radius=8)
            t_res = font_guide.render('Restart', True, WHITE)
            screen.blit(t_res, t_res.get_rect(center=RESTART_BTN_RECT.center))

            txt_moves = font_level.render(f'Moves: {moves}', True, WHITE)
            screen.blit(txt_moves, (30, SCREEN_H - 60))

            mins, secs = divmod(remaining_secs, 60)
            time_color = (255, 50, 50) if remaining_secs <= 30 else WHITE 
            txt_time = font_level.render(f'Time: {mins:02d}:{secs:02d}', True, time_color)
            screen.blit(txt_time, txt_time.get_rect(center=(SCREEN_W // 2, SCREEN_H - 45)))

            txt_pushes = font_level.render(f'Pushes: {pushes}', True, WHITE)
            screen.blit(txt_pushes, (SCREEN_W - 200, SCREEN_H - 60))

        elif sceneState == "end":
            foundGame(current_board if current_board is not None else list_board[-1])
        elif sceneState == "game_over":
            gameOverScreen(current_board, game_over_reason)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if sceneState == "init":
                    if PLAY_BUTTON_RECT.collidepoint(pos):
                        sceneState = "player_menu"
                    elif AI_BUTTON_RECT.collidepoint(pos):
                        sceneState = "loading"
                        
                elif sceneState == "player_menu":
                    if NEW_GAME_RECT.collidepoint(pos):
                        mapNumber = 0  
                        sceneState = "map_selection" 
                    elif CONTINUE_RECT.collidepoint(pos):
                        mapNumber = game_data["max_level"]
                        if mapNumber >= len(maps): mapNumber = len(maps) - 1 
                        current_board = None
                        sceneState = "playing"
                        playing_mode = "player"
                    elif SETTINGS_RECT.collidepoint(pos):
                        current_info_title = "SETTINGS"
                        current_info_lines = ["Am thanh: DANG BAT", "Nhac nen: DANG BAT", "(Dang phat trien them...)"]
                        sceneState = "info_screen"
                    elif HIGH_SCORES_RECT.collidepoint(pos):
                        # --- TRÍCH XUẤT DATA THẬT CHO HIGH SCORES ---
                        current_info_title = "HIGH SCORES"
                        current_info_lines = []
                        if not game_data["high_scores"]:
                            current_info_lines.append("Ban chua vuot qua man nao!")
                        else:
                            # Sắp xếp các map đã chơi theo level
                            sorted_levels = sorted([int(k) for k in game_data["high_scores"].keys()])
                            for lvl in sorted_levels:
                                record = game_data["high_scores"][str(lvl)]
                                current_info_lines.append(f"Lv {lvl+1}: {record['moves']} moves, {record['pushes']} pushes")
                        
                        sceneState = "info_screen"
                    elif ACHIEVEMENTS_RECT.collidepoint(pos):
                        # --- TRÍCH XUẤT DATA THẬT CHO ACHIEVEMENTS ---
                        current_info_title = "ACHIEVEMENTS"
                        current_info_lines = [
                            f"Tong so Level da qua: {game_data['max_level']}",
                            f"Tong so lan chien thang: {game_data['total_wins']}",
                            f"Tong so lan choi lai: {game_data['total_deaths']}",
                        ]
                        
                        if game_data['total_wins'] >= 5:
                            current_info_lines.append("[DANH HIEU] Ke huy diet ban do!")
                        elif game_data['total_wins'] > 0:
                            current_info_lines.append("[DANH HIEU] Nguoi moi buoc vao nghe!")
                        
                        sceneState = "info_screen"
                    elif EXIT_MENU_RECT.collidepoint(pos):
                        sceneState = "init"
                        
                elif sceneState == "info_screen":
                    if BACK_INFO_RECT.collidepoint(pos):
                        sceneState = "player_menu"
                        
                elif sceneState == "map_selection":
                    if PLAY_SELECT_RECT.collidepoint(pos):
                        current_board = None
                        sceneState = "playing" 
                        playing_mode = "player"  
                    elif BACK_SELECT_RECT.collidepoint(pos):
                        sceneState = "player_menu" 

                elif sceneState == "playing":
                    if RESTART_BTN_RECT.collidepoint(pos):
                        game_data["total_deaths"] += 1
                        save_game_data(game_data)
                        current_board = None 
                    elif QUIT_BTN_RECT.collidepoint(pos):
                        sceneState = "map_selection"

            if event.type == pygame.KEYDOWN:
                if sceneState == "init" or sceneState == "map_selection":
                    # Khóa không cho chuyển tới level chưa mở khóa (tùy chọn)
                    if event.key == pygame.K_RIGHT and mapNumber < len(maps) - 1:
                        # Nếu chỉ muốn cho chơi level đã mở thì mở dòng if bên dưới:
                        # if mapNumber < game_data["max_level"]: mapNumber += 1
                        mapNumber += 1 # Hiện tại cho phép xem hết các map
                        
                    if event.key == pygame.K_LEFT and mapNumber > 0: mapNumber -= 1
                    if sceneState == "map_selection" and event.key == pygame.K_RETURN: 
                        current_board = None
                        sceneState = "playing"
                        playing_mode = "player"  
                
                elif sceneState == "end" and event.key == pygame.K_RETURN:
                    if playing_mode == "ai":
                        sceneState = "init"
                    else:
                        sceneState = "map_selection" 
                    
                    current_board = None
                    list_board = []
                
                elif sceneState == "game_over" and event.key == pygame.K_RETURN:
                    sceneState = "map_selection"
                    current_board = None

                elif sceneState == "playing":
                    if event.key == pygame.K_r: 
                        game_data["total_deaths"] += 1
                        save_game_data(game_data)
                        current_board = None
                    elif event.key == pygame.K_ESCAPE: 
                        sceneState = "map_selection"

                    dr, dc = 0, 0
                    if event.key == pygame.K_UP: dr, dc = -1, 0
                    elif event.key == pygame.K_DOWN: dr, dc = 1, 0
                    elif event.key == pygame.K_LEFT: dr, dc = 0, -1
                    elif event.key == pygame.K_RIGHT: dr, dc = 0, 1
                    
                    if (dr != 0 or dc != 0) and current_board:
                        success, is_push = move_player(current_board, dr, dc, player_checkpoints)
                        if success:
                            moves += 1
                            if is_push: pushes += 1

                            win = True
                            for r, c in player_checkpoints:
                                if current_board[r][c] not in ['*', 's']: win = False; break
                            
                            if win: 
                                sceneState = "end"
                                if playing_mode == "player":
                                    # --- XỬ LÝ LƯU DATA KHI THẮNG ---
                                    game_data["total_wins"] += 1
                                    
                                    # Lưu level cao nhất
                                    if mapNumber + 1 > game_data["max_level"]:
                                        game_data["max_level"] = mapNumber + 1
                                    
                                    # Lưu kỷ lục nếu tốt hơn (số bước di chuyển ít hơn)
                                    lvl_str = str(mapNumber)
                                    if lvl_str not in game_data["high_scores"]:
                                        game_data["high_scores"][lvl_str] = {"moves": moves, "pushes": pushes}
                                    else:
                                        if moves < game_data["high_scores"][lvl_str]["moves"]:
                                            game_data["high_scores"][lvl_str] = {"moves": moves, "pushes": pushes}
                                            
                                    save_game_data(game_data)
                                    
                            elif is_deadlock(current_board):
                                sceneState = "game_over"
                                game_over_reason = "deadlock"
                                game_data["total_deaths"] += 1
                                save_game_data(game_data)

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    sokoban()