from drone import Drone
import sys


def print_data(n_drones, start, end, hub, connection):
    print(n_drones)
    print()
    print(start)
    print()
    print(end)
    print()
    for h in hub:
        print(h)
    print()
    for c in connection:
        print(c)


def main() -> None:
    if len(sys.argv) == 1:
        print("Usage: python main.py <map_file>")
        return

    try:
        drones: Drone = Drone.from_file(sys.argv[1])
        drones.set_map()
        drones.show_data()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
