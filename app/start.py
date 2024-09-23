import os
import psycopg2
import random


def connect_db():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST")
    )
    return conn


def save_game_result(player_name, attempts):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_results (
            id SERIAL PRIMARY KEY,
            player_name VARCHAR(50),
            attempts INTEGER
        );
    """)
    cursor.execute("""
        INSERT INTO game_results (player_name, attempts)
        VALUES (%s, %s);
    """, (player_name, attempts))
    conn.commit()
    cursor.close()
    conn.close()


def print_board(board, hide_ships=False):
    print("  1 2 3 4 5")
    for i, row in enumerate(board):
        display_row = ["~" if hide_ships and cell == "S" else cell for cell in row]
        print(f"{i + 1} {' '.join(display_row)}")


def create_board(size):
    return [["~"] * size for _ in range(size)]


def place_ship(board, size):
    direction = random.choice(["horizontal", "vertical"])
    if direction == "horizontal":
        row = random.randint(0, len(board) - 1)
        col = random.randint(0, len(board) - size)
        for i in range(size):
            if board[row][col + i] == "S":
                return place_ship(board, size)
        for i in range(size):
            board[row][col + i] = "S"
    else:
        row = random.randint(0, len(board) - size)
        col = random.randint(0, len(board) - 1)
        for i in range(size):
            if board[row + i][col] == "S":
                return place_ship(board, size)
        for i in range(size):
            board[row + i][col] = "S"


def place_all_ships(board):
    ships = [1, 2, 3]
    for ship_size in ships:
        place_ship(board, ship_size)


def player_turn(board):
    while True:
        guess_row = int(input("Угадай строку (1-5): ")) - 1
        guess_col = int(input("Угадай колонку (1-5): ")) - 1
        if 0 <= guess_row < len(board) and 0 <= guess_col < len(board):
            if board[guess_row][guess_col] == "S":
                print()
                print("\U0001F525 Попадание! \U0001F525")
                board[guess_row][guess_col] = "X"
                return True
            elif board[guess_row][guess_col] == "~":
                print()
                print("\U0000274C Мимо! \U0000274C")
                board[guess_row][guess_col] = "O"
                return False
            else:
                print()
                print("Ты уже стрелял сюда. Попробуй снова.")
        else:
            print()
            print("Вне поля! Попробуй снова.")


def check_winner(board):
    for row in board:
        if "S" in row:
            return False
    return True


def battleship():
    size = 5
    board = create_board(size)

    place_all_ships(board)

    print("Добро пожаловать в игру 'Морской бой'!")
    player_name = input("Введите ваше имя: ")

    attempts = 0
    while True:
        print("\nПоле боя:")
        print_board(board, hide_ships=True)

        print("\nТвой ход!")
        if player_turn(board):
            if check_winner(board):
                print("Поздравляю! Ты потопил все корабли!")
                save_game_result(player_name, attempts)
                break

        attempts += 1
        print(f"Попыток сделано: {attempts}")


battleship()
