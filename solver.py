#!/usr/bin/env python3

"""
Pentomino calendar puzzle solver.

Board layout (7x7 grid):
  Row 0: Jan  Feb  Mar  Apr  May  Jun  [blocked]
  Row 1: Jul  Aug  Sep  Oct  Nov  Dec  [blocked]
  Row 2:  1    2    3    4    5    6    7
  Row 3:  8    9   10   11   12   13   14
  Row 4: 15   16   17   18   19   20   21
  Row 5: 22   23   24   25   26   27   28
  Row 6: 29   30   31  [blocked x4]

8 pieces (7 pentominoes + 1 hexomino) cover the 41 remaining cells,
leaving the target month and day exposed.
"""

import sys

ROWS = 7
COLS = 7

BLOCKED = [(0, 6), (1, 6), (6, 3), (6, 4), (6, 5), (6, 6)]

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

MONTH_POSITIONS = {
    1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (0, 3), 5: (0, 4), 6: (0, 5),
    7: (1, 0), 8: (1, 1), 9: (1, 2), 10: (1, 3), 11: (1, 4), 12: (1, 5),
}

DAY_POSITIONS = {}
for d in range(1, 32):
    r = (d - 1) // 7 + 2
    c = (d - 1) % 7
    DAY_POSITIONS[d] = (r, c)

# Piece definitions (relative coordinates)
# 7 pentominoes + 1 hexomino (2x3 rectangle)
PIECES = {
    "A": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],       # V-pentomino
    "B": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],        # Z-pentomino
    "C": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 2)],        # Y-pentomino
    "D": [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],        # L-pentomino
    "E": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],        # U-pentomino (rotated)
    "F": [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)],        # P-pentomino
    "G": [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1)],        # N-pentomino
    "H": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)], # 2x3 rectangle
}


def rotate_90(cells):
    return [(c, -r) for r, c in cells]


def normalize(cells):
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    shifted = sorted((r - min_r, c - min_c) for r, c in cells)
    return tuple(shifted)


def all_orientations(cells):
    orientations = set()
    current = cells
    for _ in range(4):
        orientations.add(normalize(current))
        flipped = [(-r, c) for r, c in current]
        orientations.add(normalize(flipped))
        current = rotate_90(current)
    return [list(o) for o in orientations]


def precompute_placements(pieces):
    placements = {}
    for name, cells in pieces.items():
        placements[name] = all_orientations(cells)
    return placements


def solve(month, day):
    board = [[False] * COLS for _ in range(ROWS)]
    labels = [["." for _ in range(COLS)] for _ in range(ROWS)]

    for r, c in BLOCKED:
        board[r][c] = True
        labels[r][c] = "#"

    mr, mc = MONTH_POSITIONS[month]
    board[mr][mc] = True
    labels[mr][mc] = " "

    dr, dc = DAY_POSITIONS[day]
    board[dr][dc] = True
    labels[dr][dc] = " "

    placements = precompute_placements(PIECES)
    piece_names = list(PIECES.keys())

    def find_first_empty():
        for r in range(ROWS):
            for c in range(COLS):
                if not board[r][c]:
                    return r, c
        return None

    def try_place(piece_cells, origin_r, origin_c, name):
        positions = []
        for dr, dc in piece_cells:
            r, c = origin_r + dr, origin_c + dc
            if r < 0 or r >= ROWS or c < 0 or c >= COLS or board[r][c]:
                return None
            positions.append((r, c))
        for r, c in positions:
            board[r][c] = True
            labels[r][c] = name
        return positions

    def remove(positions):
        for r, c in positions:
            board[r][c] = False
            labels[r][c] = "."

    def backtrack(remaining):
        cell = find_first_empty()
        if cell is None:
            return True

        r, c = cell
        for i, name in enumerate(remaining):
            for orientation in placements[name]:
                min_r = orientation[0][0]
                min_c = min(cc for rr, cc in orientation if rr == min_r)
                shifted = [(rr - min_r, cc - min_c) for rr, cc in orientation]

                # Try placing so that the first empty cell is covered
                for dr, dc in shifted:
                    origin_r = r - dr
                    origin_c = c - dc
                    placed = try_place(orientation, origin_r, origin_c, name)
                    if placed is not None:
                        new_remaining = remaining[:i] + remaining[i + 1:]
                        if backtrack(new_remaining):
                            return True
                        remove(placed)

        return False

    # Optimization: only try placements that cover the first empty cell
    def backtrack_optimized(remaining):
        cell = find_first_empty()
        if cell is None:
            return True

        r, c = cell
        for i, name in enumerate(remaining):
            for orientation in placements[name]:
                for dr, dc in orientation:
                    origin_r = r - dr
                    origin_c = c - dc
                    placed = try_place(orientation, origin_r, origin_c, name)
                    if placed is not None:
                        new_remaining = remaining[:i] + remaining[i + 1:]
                        if backtrack_optimized(new_remaining):
                            return True
                        remove(placed)
        return False

    if backtrack_optimized(piece_names):
        return labels
    return None


def format_board(labels, month, day):
    lines = []
    lines.append(f"Solution for {MONTHS[month - 1]} {day}:")
    lines.append("")

    month_names = MONTHS[:6]
    month_row1 = ""
    for i, m in enumerate(month_names):
        pos = (0, i)
        label = labels[0][i]
        if label == " ":
            month_row1 += f"[{m:>4}]"
        else:
            month_row1 += f"  {label}   "
    lines.append(month_row1)

    month_names2 = MONTHS[6:]
    month_row2 = ""
    for i, m in enumerate(month_names2):
        label = labels[1][i]
        if label == " ":
            month_row2 += f"[{m:>4}]"
        else:
            month_row2 += f"  {label}   "
    lines.append(month_row2)

    for row in range(2, ROWS):
        line = ""
        for col in range(COLS):
            if (row, col) in BLOCKED:
                line += "      "
                continue
            d = (row - 2) * 7 + col + 1
            if d > 31:
                line += "      "
                continue
            label = labels[row][col]
            if label == " ":
                line += f"[{d:>3} ]"
            else:
                line += f"  {label}   "
        lines.append(line)

    return "\n".join(lines)


def format_board_simple(labels):
    lines = []
    for row in range(ROWS):
        line = ""
        for col in range(COLS):
            label = labels[row][col]
            line += label
        lines.append(line)
    return "\n".join(lines)


def main():
    if len(sys.argv) == 3:
        month = int(sys.argv[1])
        day = int(sys.argv[2])
    elif len(sys.argv) == 1:
        from datetime import date
        today = date.today()
        month = today.month
        day = today.day
    else:
        print(f"Usage: {sys.argv[0]} [month day]")
        print(f"  month: 1-12")
        print(f"  day: 1-31")
        sys.exit(1)

    if month < 1 or month > 12:
        print(f"Invalid month: {month}")
        sys.exit(1)
    if day < 1 or day > 31:
        print(f"Invalid day: {day}")
        sys.exit(1)

    print(f"Solving for {MONTHS[month - 1]} {day}...")
    solution = solve(month, day)
    if solution:
        print()
        print(format_board_simple(solution))
        print()
        print(format_board(solution, month, day))
    else:
        print("No solution found!")


if __name__ == "__main__":
    main()
