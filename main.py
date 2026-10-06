import matplotlib.pyplot as plt
from src.building import Floor, Building
from src.physics import fire_spread

def main():
    side = 25
    floor_1 = Floor(side)
    floor_2 = Floor(side)
    floor_3 = Floor(side)

    S_int = 500
    S_building = [floor_1.spaces, floor_2.spaces, floor_3.spaces]
    T_building = [floor_1.temperatures, floor_2.temperatures, floor_3.temperatures]
    R_building = [floor_1.rooms, floor_2.rooms, floor_3.rooms]
    dt = 1200

    height_values = [1.50 + i * 0.4 for i in range(5)]
    count_fire_values = []

    T_matter = 200
    fire_power = 100_000

    for height in height_values:
        dico = {
            'outside_walls_thickness': 0.3,
            'inside_walls_thickness': 0.15,
            'ground_thickness': 0.3,
            'height': height
        }
        building = Building(dico, S_building, T_building, R_building)
        building.T_building = [[[15 for _ in range(side)] for _ in range(side)] for _ in range(3)]
        building.S_building = [[[0 for _ in range(side)] for _ in range(side)] for _ in range(3)]
        
        count_fire = fire_spread(building, S_int, T_matter, fire_power, dt, T_ext=0)
        count_fire_values.append(count_fire * dt / 3600)

    plt.plot(height_values, count_fire_values, marker='o')
    plt.xlabel('hauteur au plafond')
    plt.ylabel('heures')
    plt.show()

if __name__ == "__main__":
    main()