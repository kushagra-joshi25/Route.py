# Route.py

## Introduction

This Python script, `Route.py`, is designed to find routes between cities using various routing algorithms and options. It leverages data from `city-gps.txt` and `road-segments.txt` to create a graph representing cities and highways. The script supports the following features:

1. Finding the best routing algorithm for different routing options.
2. Determining the fastest algorithm in terms of computation time.
3. Identifying the algorithm with the least memory requirements.
4. Explaining the heuristic function used for route calculation.
5. Discovering the farthest city from a specified starting city.

## Usage

To use this script, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Python installed.
3. Run the script with the following command:

```bash
python Route.py [source_city] [destination_city] [routing_option] [routing_algorithm]
(https://github.com/kushagrajoshi-ghub/Route.py/assets/85024946/5ceed271-3907-4a72-a6a6-f6eeb8f257bd)
```

- Replace `[source_city]` with the starting city.
- Replace `[destination_city]` with the destination city.
- Replace `[routing_option]` with one of the following options: `segments`, `distance`, `scenic`, or `time`.
- Replace `[routing_algorithm]` with one of the following algorithms: `bfs`, `dfs`, `astar`, or `ids`.

## Implementation

![Screenshot (40)](https://github.com/kushagrajoshi-ghub/Route.py/assets/85024946/12854ae8-4533-4e9e-a353-814acc8a013f)


## Results

The script will provide you with the following information:

1. The best routing algorithm for each routing option.
2. The fastest algorithm in terms of computation time.
3. The algorithm with the least memory requirements.
4. Details about the heuristic function used for route calculation.
5. The farthest city from the starting city.

## Scope of Improvements

The script has room for improvement, such as implementing bidirectional search to optimize pathfinding for certain cases.
