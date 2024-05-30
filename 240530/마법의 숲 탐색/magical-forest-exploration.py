import pathlib
import sys

DEBUG = False
input = sys.stdin.readline
if DEBUG:
    input = pathlib.Path(__file__).with_suffix(".txt").open("rt").readline

R, C, K = list(map(int, input().strip().split()))


class Golem:
    def __init__(self, col, door) -> None:
        self.col = col
        self.row = -1
        self.door = door

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.__dict__}"

    def move_left(self):
        self.col -= 1
        self.door = (self.door - 1) % 4
        if DEBUG:
            print(self.col, self.row)

    def move_right(self):
        self.col += 1
        self.door = (self.door + 1) % 4
        if DEBUG:
            print(self.col, self.row)

    def move_down(self):
        self.row += 1

    def move_up(self):
        self.row -= 1


golems = []
for _ in range(K):
    ci, di = list(map(int, input().strip().split()))
    golems.append(Golem(ci - 1, di))

if DEBUG:
    for i, golem in enumerate(golems):
        print(i + 1, golem)
    print()


class Board:
    def __init__(self, R, C) -> None:
        self.R = R
        self.C = C
        self.sum_soul = 0
        self.reset_board()

    def __repr__(self) -> str:
        ret = "Board\n"
        ret += f"R={self.R}, C={self.C}\n"
        for line in self.board:
            for item in line:
                ret += f"{item}"
            ret += "\n"
        return ret

    def reset_board(self) -> None:
        self.board = [["-"] * self.C for _ in range(self.R)]

    def is_right(self, golem: Golem) -> bool:
        for point in [(1, -1), (2, 0), (1, 1)]:
            x, y = golem.col + point[0], golem.row + point[1]
            if x >= self.C:
                return False
            if self.board[y][x] != "-" and (0 <= x < self.C and 0 <= y < self.R):
                return False

        return True

    def is_left(self, golem: Golem) -> bool:
        for point in [(-1, -1), (-2, 0), (-1, 1)]:
            x, y = golem.col + point[0], golem.row + point[1]
            if x < 0:
                return False
            if self.board[y][x] != "-" and (0 <= x < self.C and 0 <= y < self.R):
                return False
        return True

    def is_down(self, golem: Golem) -> bool:
        for point in [(-1, 1), (0, 2), (1, 1)]:
            x, y = golem.col + point[0], golem.row + point[1]
            if y >= self.R:
                return False
            if self.board[y][x] != "-" and (0 <= x < self.C and 0 <= y < self.R):
                return False
        return True

    def is_leftdown(self, golem: Golem) -> bool:
        if self.is_left(golem):
            golem.move_left()
            if self.is_down(golem):
                golem.move_right()
                return True
            else:
                golem.move_right()
                return False
        return False

    def is_rightdown(self, golem: Golem) -> bool:
        if self.is_right(golem):
            golem.move_right()
            if self.is_down(golem):
                golem.move_left()
                return True
            else:
                golem.move_left()
                return False
        return False

    def calc_soul(self, golem: Golem) -> None:
        visited = [[False] * self.C for _ in range(self.R)]
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # TODO:BFS
        queue = []

        queue.append((golem.col, golem.row))
        max_soul = 0
        while queue:
            x, y = queue.pop(0)
            if not visited[y][x]:
                visited[y][x] = True

                door = int(self.board[y][x])
                door_direction = directions[door]
                door_x, door_y = x + door_direction[0], y + door_direction[1]
                visited[door_y][door_x] = True

                max_soul = y + 1
                for direction in directions:
                    search_x = door_x + direction[0]
                    search_y = door_y + direction[1]
                    if 0 <= search_x < self.C and 0 <= search_y < self.R:
                        visited[search_y][search_x] = True
                        if self.board[search_y][search_x] == "T":
                            new_x = search_x
                            new_y = search_y + 1
                            queue.append((new_x, new_y))
                            max_soul = max(max_soul, new_y + 1)
                        if self.board[search_y][search_x] == "R":
                            new_x = search_x - 1
                            new_y = search_y
                            queue.append((new_x, new_y))
                            max_soul = max(max_soul, new_y + 1)
                        if self.board[search_y][search_x] == "B":
                            new_x = search_x
                            new_y = search_y - 1
                            queue.append((new_x, new_y))
                            max_soul = max(max_soul, new_y + 1)
                        if self.board[search_y][search_x] == "L":
                            new_x = search_x + 1
                            new_y = search_y
                            queue.append((new_x, new_y))
                            max_soul = max(max_soul, new_y + 1)

        # 총합 구하기
        self.sum_soul += max_soul + 1

    def add_golem(self, golem: Golem) -> None:
        # TODO:골렘 움직일수 있는지 체크
        move_right = False
        while True:
            if self.is_down(golem):
                golem.move_down()
                continue

            if golem.row == self.R - 2:
                break

            if self.is_leftdown(golem) and not move_right:
                golem.move_left()
                golem.move_down()
                continue
            else:
                if self.is_rightdown(golem):
                    golem.move_right()
                    golem.move_down()
                    move_right = True
                    continue
                else:
                    break

        if golem.row > 0:
            # TODO:골렘 추가후 정령 위치 계산
            self.board[golem.row][golem.col] = str(golem.door)
            self.board[golem.row - 1][golem.col] = "T"
            self.board[golem.row][golem.col + 1] = "R"
            self.board[golem.row + 1][golem.col] = "B"
            self.board[golem.row][golem.col - 1] = "L"
            self.calc_soul(golem)
        else:
            # 골렘 추가후 보드 밖에 있으면 보드 초기화
            self.reset_board()

    def result(self) -> int:
        return self.sum_soul


board = Board(R, C)

for i, golem in enumerate(golems):
    if DEBUG:
        print(i + 1, golem)
    board.add_golem(golem)
    if DEBUG:
        print(board.result())
        print(board)

print(board.result())