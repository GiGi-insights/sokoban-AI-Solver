import os
import random

# 1. Tạo thư mục nếu chưa có
os.makedirs('Testcases', exist_ok=True)
os.makedirs('Checkpoints', exist_ok=True)

# 2. Số lượng thùng tăng dần cho 20 level
box_counts = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 25]

# 3. Vòng lặp tạo map
for level, num_boxes in enumerate(box_counts, 1):
    map_file = f"Testcases/map_{level}.txt"
    chk_file = f"Checkpoints/checkpoint_{level}.txt"

    # Tạo map 10x12
    board = [[' ' for _ in range(12)] for _ in range(10)]
    # Vẽ tường viền
    for r in range(10):
        board[r][0] = board[r][11] = '1'
    for c in range(12):
        board[0][c] = board[9][c] = '1'

    # Đặt player
    board[1][1] = 'p'

    checkpoints = []
    placed = 0
    attempts = 0
    max_attempts = 5000

    while placed < num_boxes and attempts < max_attempts:
        r = random.randint(1, 8)
        c = random.randint(1, 10)
        r2 = random.randint(1, 8)
        c2 = random.randint(1, 10)

        # Đảm bảo thùng và checkpoint không trùng, và ô trống
        if board[r][c] == ' ' and board[r2][c2] == ' ':
            board[r][c] = 'b'
            board[r2][c2] = 'c'
            checkpoints.append(f"{r2},{c2}")
            placed += 1
        attempts += 1

    # Ghi ra file map
    with open(map_file, 'w') as f:
        for row in board:
            f.write(','.join(row) + '\n')

    # Ghi ra file checkpoint
    with open(chk_file, 'w') as f:
        f.write('\n'.join(checkpoints))

print("Tạo thành công 20 level với thùng và checkpoint rải rác. Hill Climbing sẽ dễ chạy hơn!")
