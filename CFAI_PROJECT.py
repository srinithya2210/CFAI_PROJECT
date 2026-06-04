"""
Sudoku Solver & Generator — Command Line Tool
=============================================
Features:
  - Generate puzzles with 3 difficulty levels
  - Solve any valid Sudoku puzzle
  - Pretty-print board with box borders
  - Input your own puzzle to solve
"""

import random
import copy
import time


# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────

def print_board(board, title=""):
    if title:
        print(f"\n{'─'*25}  {title}  {'─'*25}\n")
    else:
        print()

    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            print("  ------+-------+------")
        row_str = "  "
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            row_str += (str(val) if val != 0 else ".") + " "
        print(row_str)
    print()


# ─────────────────────────────────────────────
#  VALIDATOR
# ─────────────────────────────────────────────

def is_valid(board, row, col, num):
    """Check if placing `num` at (row, col) is valid."""
    # Row check
    if num in board[row]:
        return False
    # Column check
    if num in [board[r][col] for r in range(9)]:
        return False
    # 3x3 box check
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


# ─────────────────────────────────────────────
#  SOLVER  (backtracking)
# ─────────────────────────────────────────────

def find_empty(board):
    """Return (row, col) of next empty cell, or None."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def solve(board):
    """Solve in-place using backtracking. Returns True if solved."""
    pos = find_empty(board)
    if pos is None:
        return True  # No empty cells → solved

    row, col = pos
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0  # backtrack

    return False


def count_solutions(board, limit=2):
    """Count solutions up to `limit` (used to ensure unique puzzles)."""
    pos = find_empty(board)
    if pos is None:
        return 1
    row, col = pos
    count = 0
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            count += count_solutions(board, limit)
            board[row][col] = 0
            if count >= limit:
                break
    return count


# ─────────────────────────────────────────────
#  GENERATOR
# ─────────────────────────────────────────────

DIFFICULTY = {
    "easy":   (36, 45),   # clues range
    "medium": (27, 35),
    "hard":   (22, 26),
}


def generate_full_board():
    """Create a fully solved valid Sudoku board."""
    board = [[0] * 9 for _ in range(9)]
    nums = list(range(1, 10))

    def fill(board):
        pos = find_empty(board)
        if pos is None:
            return True
        row, col = pos
        random.shuffle(nums)
        for num in nums:
            if is_valid(board, row, col, num):
                board[row][col] = num
                if fill(board):
                    return True
                board[row][col] = 0
        return False

    fill(board)
    return board


def generate_puzzle(difficulty="medium"):
    """Remove cells from a solved board to create a puzzle."""
    full = generate_full_board()
    puzzle = copy.deepcopy(full)

    clue_min, clue_max = DIFFICULTY[difficulty]
    target_clues = random.randint(clue_min, clue_max)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if 81 - removed <= target_clues:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0

        test = copy.deepcopy(puzzle)
        if count_solutions(test) != 1:
            puzzle[r][c] = backup  # restore if not unique
        else:
            removed += 1

    return puzzle, full


# ─────────────────────────────────────────────
#  USER INPUT
# ─────────────────────────────────────────────

def input_board():
    """Ask the user to enter a Sudoku board row by row."""
    print("\nEnter your puzzle row by row (9 digits each, use 0 for empty).")
    print("Example:  530070000\n")
    board = []
    for i in range(9):
        while True:
            row_str = input(f"  Row {i+1}: ").strip()
            if len(row_str) == 9 and row_str.isdigit():
                board.append([int(d) for d in row_str])
                break
            print("  ✗ Please enter exactly 9 digits (0–9).")
    return board


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def menu():
    print("\n" + "═" * 55)
    print("        🟦  SUDOKU  SOLVER  &  GENERATOR  🟦")
    print("═" * 55)
    print("  1. Generate a new puzzle")
    print("  2. Solve your own puzzle")
    print("  3. Quit")
    print("─" * 55)
    return input("  Choose an option (1/2/3): ").strip()


def difficulty_menu():
    print("\n  Difficulty levels:")
    print("    1. Easy   (36–45 clues)")
    print("    2. Medium (27–35 clues)")
    print("    3. Hard   (22–26 clues)")
    choice = input("  Choose difficulty (1/2/3): ").strip()
    return {"1": "easy", "2": "medium", "3": "hard"}.get(choice, "medium")


def main():
    while True:
        choice = menu()

        if choice == "1":
            diff = difficulty_menu()
            print(f"\n  ⏳ Generating {diff} puzzle …", end="", flush=True)
            t0 = time.time()
            puzzle, solution = generate_puzzle(diff)
            elapsed = time.time() - t0
            print(f" done in {elapsed:.2f}s")

            print_board(puzzle, title=f"PUZZLE  [{diff.upper()}]")
            input("  Press Enter to reveal the solution …")
            print_board(solution, title="SOLUTION")

        elif choice == "2":
            board = input_board()
            print_board(board, title="YOUR PUZZLE")

            # Quick sanity check
            test = copy.deepcopy(board)
            print("  ⏳ Solving …", end="", flush=True)
            t0 = time.time()
            solved = solve(test)
            elapsed = time.time() - t0
            print(f" done in {elapsed:.3f}s")

            if solved:
                print_board(test, title="SOLUTION ✓")
            else:
                print("\n  ✗ No solution exists for this puzzle. Please check your input.\n")

        elif choice == "3":
            print("\n  Goodbye! 👋\n")
            break

        else:
            print("\n  ✗ Invalid option. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()