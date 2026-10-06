from math import sqrt
from time import process_time

def set_fire(building, T_matter, burning=1):
    count_floor = len(building.S_building)
    side = len(building.S_building[0])
    num_floor = count_floor // 2
    i_depart, j_depart = side // 2, side // 2
    building.S_building[num_floor][i_depart][j_depart] = 1
    return num_floor, i_depart, j_depart

def get_neighboring_cells(coordinate, side):
    i, j = coordinate
    north, south, west, east = [i, j], [i, j], [i, j], [i, j]

    if i != 0 and i != side - 1 and j != 0 and j != side - 1:
        north, south, west, east = [i, j + 1], [i, j - 1], [i - 1, j], [i + 1, j]
    elif i == 0 and j != 0 and j != side - 1:
        north, south, west, east = [i, j + 1], [i, j - 1], [i, j], [i + 1, j]
    elif i == side - 1 and j != 0 and j != side - 1:
        north, south, west, east = [i, j + 1], [i, j - 1], [i - 1, j], [i, j]
    elif i != 0 and i != side - 1 and j == 0:
        north, south, west, east = [i, j + 1], [i, j], [i - 1, j], [i + 1, j]
    elif i != 0 and i != side - 1 and j == side - 1:
        north, south, west, east = [i, j], [i, j - 1], [i - 1, j], [i + 1, j]
    elif i == 0 and j == 0:
        north, south, west, east = [i, j + 1], [i, j], [i, j], [i + 1, j]
    elif i == side - 1 and j == 0:
        north, south, west, east = [i, j + 1], [i, j], [i - 1, j], [i, j]
    elif i == 0 and j == side - 1:
        north, south, west, east = [i, j], [i, j - 1], [i, j], [i + 1, j]
    elif i == side - 1 and j == side - 1:
        north, south, west, east = [i, j], [i, j - 1], [i - 1, j], [i, j]

    return [north, south, west, east]

def get_inside_walls(building, floor_number, coordinate, side):
    inside_walls = []
    neighboring_cells = get_neighboring_cells(coordinate, side)

    if building.R_building[floor_number][neighboring_cells[0][1]][neighboring_cells[0][0]] != building.R_building[floor_number][coordinate[1]][coordinate[0]]:
        inside_walls.append(neighboring_cells[0])
    if building.R_building[floor_number][neighboring_cells[1][1]][neighboring_cells[1][0]] != building.R_building[floor_number][coordinate[1]][coordinate[0]]:
        inside_walls.append(neighboring_cells[1])
    if building.R_building[floor_number][neighboring_cells[2][1]][neighboring_cells[2][0]] != building.R_building[floor_number][coordinate[1]][coordinate[0]]:
        inside_walls.append(neighboring_cells[2])
    if building.R_building[floor_number][neighboring_cells[3][1]][neighboring_cells[3][0]] != building.R_building[floor_number][coordinate[1]][coordinate[0]]:
        inside_walls.append(neighboring_cells[3])

    return inside_walls

def get_outside_walls(coordinate, side):
    count_outside_walls = 0
    if coordinate[1] == 0:
        count_outside_walls += 1
    if coordinate[1] == side - 1:
        count_outside_walls += 1
    if coordinate[0] == 0:
        count_outside_walls += 1
    if coordinate[1] == side - 1:
        count_outside_walls += 1
    return count_outside_walls

def test_upper_floor(nb_floor, count_floor):
    return nb_floor != count_floor - 1

def test_lower_floor(nb_floor):
    return nb_floor != 0

def fire_spread(building, S_int, T_matter, fire_power, dt, T_ext=0):
    count_floor = len(building.S_building)
    side = len(building.S_building[0][0])

    lambda_ground = 0.16
    lambda_walls = 0.07
    density = 750
    air_density = 1.225

    S_ext = building.dico['height'] * sqrt(S_int)
    dS_ground = S_int / (side * side)
    dS_walls = S_ext / (side * 1)

    thermal_capacity = (dS_ground**2) * building.dico['ground_thickness'] * density * 1000 + (dS_ground**2) * building.dico['height'] * air_density * 1005
    Rth_e = building.dico['outside_walls_thickness'] / (lambda_walls * dS_walls)
    Rth_h = building.dico['inside_walls_thickness'] / (lambda_walls * dS_walls)
    Rth_v = building.dico['ground_thickness'] / (lambda_ground * dS_ground)
    fire_power = fire_power * dS_ground

    num_floor, i_depart, j_depart = set_fire(building, T_matter)
    building.T_building[num_floor][i_depart][j_depart] = T_matter
    building.S_building[num_floor][i_depart][j_depart] = 1

    count_fire = 1
    ite = 0

    while count_fire < count_floor * (side**2) * 0.80:
        for nb_floor in range(count_floor):
            room_temperature = {}

            for x in range(side):
                for y in range(side):
                    inside_walls = get_inside_walls(building, nb_floor, [x, y], side)
                    nb_inside_walls = len(inside_walls)
                    nb_outside_walls = get_outside_walls([x, y], side)

                    if building.S_building[nb_floor][x][y] == 0:
                        if not test_lower_floor(nb_floor):
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt

                        elif not test_upper_floor(nb_floor, count_floor):
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt

                        else:
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h) * dt

                    elif building.S_building[nb_floor][x][y] == 1:
                        if not test_lower_floor(nb_floor):
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor + 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt

                        elif not test_upper_floor(nb_floor, count_floor):
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] - building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt

                        else:
                            if nb_outside_walls == 0:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 1:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                            elif nb_outside_walls == 2:
                                if nb_inside_walls == 0:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + fire_power) * dt
                                elif nb_inside_walls == 1:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_v + 2 * (T_ext - building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] - building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt
                                elif nb_inside_walls == 2:
                                    building.T_building[nb_floor][x][y] += (1 / thermal_capacity) * ((building.T_building[nb_floor - 1][x][y] + building.T_building[nb_floor + 1][x][y] - 2 * building.T_building[nb_floor][x][y]) / Rth_e + (building.T_building[nb_floor][inside_walls[0][0]][inside_walls[0][1]] + building.T_building[nb_floor][inside_walls[1][0]][inside_walls[1][1]] - 2 * building.T_building[nb_floor][x][y]) / Rth_h + fire_power) * dt

                    if building.R_building[nb_floor][x][y] in room_temperature:
                        room_temperature[building.R_building[nb_floor][x][y]][0] += building.T_building[nb_floor][x][y]
                        room_temperature[building.R_building[nb_floor][x][y]][1] += 1
                    else:
                        room_temperature[building.R_building[nb_floor][x][y]] = [building.T_building[nb_floor][x][y], 1]

            for x in range(side):
                for y in range(side):
                    building.T_building[nb_floor][x][y] = room_temperature[building.R_building[nb_floor][x][y]][0] / room_temperature[building.R_building[nb_floor][x][y]][1]
                    if building.T_building[nb_floor][x][y] > T_matter and building.S_building[nb_floor][x][y] == 0:
                        building.S_building[nb_floor][x][y] = 1
                        count_fire += 1

        ite += 1
        if ite > 2000:
            return ite

    return ite