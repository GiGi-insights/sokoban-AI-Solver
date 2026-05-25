import numpy as np
from collections import deque
import heapq

def Hill_Climbing_Search(sokoban_board, checkpoint_array=None):
    if sokoban_board is None: return []

    rows = len(sokoban_board)
    cols = len(sokoban_board[0])
    walls, goals, start_boxes = set(), set(), []
    start_player = None

    # 1. Quét Map
    for r in range(rows):
        for c in range(cols):
            v = str(sokoban_board[r][c]).strip().lower()
            if v in ['1', '#']: walls.add((r, c))
            elif v in ['p', '@']: start_player = (r, c)
            elif v in ['b', '$']: start_boxes.append((r, c))
            elif v in ['c', '%', '.']: goals.add((r, c))
            elif v in ['*', 'v']:
                start_boxes.append((r, c))
                goals.add((r, c))

    if checkpoint_array:
        for pos in checkpoint_array:
            r_cp, c_cp = int(pos[0]) - 1, int(pos[1]) - 1
            if 0 <= r_cp < rows and 0 <= c_cp < cols:
                goals.add((r_cp, c_cp))

    goals = frozenset(goals)
    walls = frozenset(walls)
    start_boxes_fs = frozenset(start_boxes)

    # 2. Tạo bản đồ các ô Chết (Deadlock Zones)
    def is_static_deadlock(r, c):
        if (r, c) in goals: return False
        up = (r-1, c) in walls; down = (r+1, c) in walls
        left = (r, c-1) in walls; right = (r, c+1) in walls
        if (up and left) or (up and right) or (down and left) or (down and right):
            return True
        return False

    # 3. Heuristic: Manhattan Distance
    def get_heuristic(boxes):
        total = 0
        boxes_list = list(boxes)
        goals_list = list(goals)
        for b in boxes_list:
            if b not in goals:
                dists = [abs(b[0]-g[0]) + abs(b[1]-g[1]) for g in goals_list]
                total += min(dists) if dists else 0
            else:
                total -= 10 
        return total

    # 4. Flood fill tìm vùng người chơi có thể di chuyển
    def get_reachable(player_pos, boxes_set):
        q = deque([player_pos])
        visited = {player_pos}
        while q:
            r, c = q.popleft()
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if (nr, nc) not in walls and (nr, nc) not in boxes_set and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        return visited

    # --- THUẬT TOÁN A* TỐI ƯU ---
    queue = [(get_heuristic(start_boxes_fs), 0, start_player, start_boxes_fs, [])]
    visited = {(start_player, start_boxes_fs)}
    
    print("AI dang tim duong, vui long cho...")

    limit = 0
    while queue:
        h, g, curr_p, curr_boxes, history = heapq.heappop(queue)
        limit += 1

        if curr_boxes == goals:
            print(f"THANH CONG! Tim thay loi giai sau {limit} trang thai.")
            return rebuild_path(history + [(curr_p, curr_boxes)], walls, goals, rows, cols)

        if limit > 80000:
            break

        reachable = get_reachable(curr_p, curr_boxes)
        
        # Chỉ xét các hành động ĐẨY thùng (Macro moves)
        for box in curr_boxes:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                push_from = (box[0]-dr, box[1]-dc) 
                push_to = (box[0]+dr, box[1]+dc)   
                
                if push_from in reachable and push_to not in walls and push_to not in curr_boxes:
                    if not is_static_deadlock(push_to[0], push_to[1]):
                        new_boxes = frozenset((curr_boxes - {box}) | {push_to})
                        new_state = (box, new_boxes) 
                        
                        if new_state not in visited:
                            visited.add(new_state)
                            new_h = get_heuristic(new_boxes)
                            heapq.heappush(queue, (g + 1 + 2*new_h, g + 1, box, new_boxes, history + [(curr_p, curr_boxes)]))

    print("Khong tim thay loi giai. Goi y: Hay xoa bot tuong le o giua map.")
    return []

# --- HÀM TÌM ĐƯỜNG ĐI BỘ CHI TIẾT ---
def get_path_bfs(start, goal, boxes, walls):
    if start == goal: return []
    q = deque([(start, [])])
    visited = {start}
    while q:
        curr, path = q.popleft()
        if curr == goal: return path
        r, c = curr
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r+dr, c+dc
            if (nr, nc) not in walls and (nr, nc) not in boxes and (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [(nr, nc)]))
    return []

# --- HÀM TÁI TẠO FRAME THEO TỪNG BƯỚC CHÂN ---
def rebuild_path(history, walls, goals, rows, cols):
    final_path = []
    
    def create_grid(p, b):
        grid = np.full((rows, cols), ' ', dtype=object)
        for r, c in walls: grid[r][c] = '1'
        for r, c in goals: grid[r][c] = 'c'
        for r, c in b: grid[r][c] = '*' if (r, c) in goals else 'b'
        grid[p[0]][p[1]] = 'p'
        return grid

    # Phân tích các bước nhảy vĩ mô và điền thêm khung hình đi bộ vào giữa
    for i in range(len(history) - 1):
        p_curr, b_curr = history[i]
        p_next, b_next = history[i+1]
        
        # 1. Lưu lại khung hình lúc đang đứng yên
        final_path.append(create_grid(p_curr, b_curr))

        # Tìm xem thùng nào chuẩn bị bị đẩy
        b_old = list(b_curr - b_next)[0]
        b_new = list(b_next - b_curr)[0]
        
        # Tính vị trí đứng trước khi đẩy thùng
        dr = b_new[0] - b_old[0]
        dc = b_new[1] - b_old[1]
        push_from = (b_old[0] - dr, b_old[1] - dc)
        
        # 2. Sinh ra các khung hình đi bộ đến chỗ chuẩn bị đẩy thùng
        walk_path = get_path_bfs(p_curr, push_from, b_curr, walls)
        for step in walk_path:
            final_path.append(create_grid(step, b_curr))

    # Cuối cùng gắn nốt cái khung hình chiến thắng vào
    if history:
        final_p, final_b = history[-1]
        final_path.append(create_grid(final_p, final_b))
        
    return final_path