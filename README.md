*This project has been created as part of the 42 curriculum by tchemin*

# Fly-In

## Description

Fly-In is a 3D drone-routing simulation built with Ursina. The project reads a custom map file, validates it, builds a network of hubs and connections, and animates a fleet of drones as they travel from a start hub to an end hub.

The goal is to visualize how multiple drones move through a constrained network while respecting link capacities, hub types, and turn-based progression. The project combines parsing, validation, graph traversal, and real-time rendering.

## Instructions

### Requirements

- Python 3
- The dependencies listed in [requirements.txt](requirements.txt)

### Installation

```bash
make venv (optionnal)
make install
```

### Execution

Run the simulator with a map file:

```bash
make run FILE=maps/easy/01_linear_path.txt
```

You can also use another map from the `maps/` directory, for example:

```bash
make run FILE=maps/medium/03_priority_puzzle.txt
```

### Controls

- `n`: advance one turn and animate the next movement step
- `Esc`: quit the application

## Algorithm and Implementation Strategy

The project is structured in three main stages:

1. **Parsing and validation**: the map is loaded from a text file, then validated with Pydantic rules. The parser enforces a single `start_hub` and `end_hub`, checks hub names, validates metadata, verifies connection endpoints, and rejects duplicate links.
2. **Graph construction**: hubs, start/end nodes, and connections are converted into Python objects. The `Drone` model also builds a lightweight adjacency/belonging structure used to reason about reachable zones and parents.
3. **Turn-based movement**: each drone computes a reachable path for the current state, selects the best candidate toward the end hub, then advances one hub at a time while respecting constraints such as link capacity, blocked zones, restricted zones, and priority zones.

The movement logic is turn driven. Each turn records the drones' positions, resets connection usage counters, and updates the total number of turns. This keeps the simulation deterministic and makes the visual progression easy to follow.

## Visual Representation

The visual layer is implemented with Ursina and is designed to make the routing logic readable at a glance:

- The ground, sky, and first-person camera create a navigable 3D scene.
- Hubs are rendered as cubes with labels showing their name and zone type.
- Colors and textures are derived from map metadata, which helps distinguish special hubs such as rainbow or brick variants.
- Connections are displayed as visible lines between hubs, so the network topology is immediately understandable.
- Drones are rendered as distinct 3D entities with labels, making it easy to track individual units during the simulation.
- A turn counter is shown on screen and updated in place, so the user can follow the simulation state without clutter.

These choices improve usability because the map structure, the active drone positions, and the current turn are visible at the same time.

## Project Structure

- `main.py`: application entry point
- `drone.py`: map model, path computation, and movement logic
- `parsing/`: map parsing and validation
- `entities/`: Ursina entities for hubs and drones
- `graphic.py`: scene setup and rendering helpers
- `maps/`: example input files

## Resources

### References

- [Ursina Engine documentation](https://www.ursinaengine.org/)
- [Ursina GitHub repository](https://github.com/pokepetter/ursina)

### AI Usage

AI was used to draft and polish this README, summarize the codebase structure from the source files.The project logic itself, including parsing, validation, path selection, and rendering behavior were done by tchemin

## Notes

The project includes sample maps of increasing difficulty in `maps/easy`, `maps/medium`, `maps/hard`, and `maps/challenger`.
