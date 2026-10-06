import random

class Building:
    def __init__(self, dico, S_building, T_building, R_building):
        self.dico = dico
        self.S_building = [S_building[i] for i in range(len(S_building))]
        self.T_building = [T_building[i] for i in range(len(T_building))]
        self.R_building = [R_building[i] for i in range(len(R_building))]

class Floor:
    def __init__(self, side):
        self.side = int(side)
        self.spaces = [[0 for _ in range(self.side)] for _ in range(self.side)]
        self.temperatures = [[15 for _ in range(self.side)] for _ in range(self.side)]
        self.rooms = self.create_rooms()

    def create_rooms(self):
        room_count = random.randint(3, 5)
        room_sizes = self.get_room_sizes(room_count)
        rooms = [[0 for _ in range(self.side)] for _ in range(self.side)]
        current_room = 1

        for room_size in room_sizes:
            self.assign_room(rooms, current_room, room_size)
            current_room += 1

        return rooms

    def get_room_sizes(self, room_count):
        total_area = self.side * self.side
        remaining_area = total_area
        min_room_size = 1
        max_room_size = remaining_area // room_count
        room_sizes = []

        for i in range(room_count - 1):
            room_size = random.randint(min_room_size, max_room_size)
            room_sizes.append(room_size)
            remaining_area -= room_size
            max_room_size = remaining_area // (room_count - len(room_sizes))

        room_sizes.append(remaining_area)
        return room_sizes

    def assign_room(self, rooms, room_number, room_size):
        room_width = random.randint(1, self.side)
        room_height = room_size // room_width

        for i in range(self.side):
            for j in range(self.side):
                if rooms[i][j] == 0:
                    for dx in range(room_width):
                        for dy in range(room_height):
                            if i + dx < self.side and j + dy < self.side:
                                rooms[i + dx][j + dy] = room_number