import sys
import math
import timeit
import webbrowser
import os
from copy import deepcopy
from collections import defaultdict

try:
    import folium
except ImportError:
    folium = None

source = input("Enter source city (e.g., Bloomington,_Indiana): ").strip()
destination = input("Enter destination city (e.g., Chicago,_Illinois): ").strip()
routing_option = input("Enter routing option (segments / distance / time / scenic): ").strip().lower()
routing_algorithm = input("Enter routing algorithm (bfs / dfs / ids / astar): ").strip().lower()
plot_choice = input("Do you want to plot the route on a map? (yes/no): ").strip().lower()
plot_flag = plot_choice in ("yes", "y")

start_time = timeit.default_timer()
print("Building a graph....this may take about half a minute")

city = tuple([
    [y for index, y in enumerate(x.strip().split(" ")) if y]
    for x in open("./city-gps.txt") if x.strip() != ""
])

road_seg = tuple([
    [y for index, y in enumerate(x.strip().split(" ")) if y]
    for x in open("./road-segments.txt") if x.strip() != ""
])

class City:
    def __init__(self, name, latitude=None, longitude=None):
        self.name = name
        self.latitude = float(latitude) if latitude else 0.0
        self.longitude = float(longitude) if longitude else 0.0

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class Highway:
    def __init__(self, name, city_one, city_two, distance, speed_limit):
        self.name = name
        self.city_one = city_one
        self.city_two = city_two
        self.distance = float(distance)
        self.speed_limit = float(speed_limit)

highway_map = defaultdict(list)
road_set = set()
speed_limit_sum, highway_count = 0, 0

for h in road_seg:
    if len(h) == 5 and h[3].replace('.', '', 1).isdigit():
        road = Highway(h[4], h[0], h[1], float(h[2]), float(h[3]))
        road_set.add(road)
        highway_map[h[0]].append(road)
        highway_map[h[1]].append(road)
        speed_limit_sum += float(h[3])
        highway_count += 1

average_speed_limit = speed_limit_sum / highway_count if highway_count else 55.0

list_of_cities = []
for row in road_seg:
    list_of_cities.extend([row[0], row[1]])
list_of_cities = list(set(list_of_cities))

city = list(city)
for inter in list_of_cities:
    if inter not in [row[0] for row in city]:
        city.append([inter, None, None])
city = tuple(city)

city_map = {}
for row in city:
    city_map[row[0]] = City(
        row[0],
        row[1] if len(row) > 1 else None,
        row[2] if len(row) > 2 else None
    )

print("Completed Building Graph")

def displacement(city_one, city_two):
    """Calculate great-circle distance between two cities."""
    lat1, lon1 = city_map[city_one].latitude, city_map[city_one].longitude
    lat2, lon2 = city_map[city_two].latitude, city_map[city_two].longitude

    if (lat1 == 0.0 and lon1 == 0.0) or (lat2 == 0.0 and lon2 == 0.0):
        return 0.0

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c * 0.621371  # miles


def get_edge_cost(city_one, city_two):
    """Return (distance, speed_limit) between two cities."""
    for edge in highway_map.get(city_one, []):
        if edge.city_one == city_two or edge.city_two == city_two:
            return edge.distance, edge.speed_limit
    return None


def get_overall_cost(route):
    """Calculate total distance and time for a route."""
    total_distance, total_time = 0.0, 0.0
    for i in range(len(route) - 1):
        edge_cost = get_edge_cost(route[i], route[i + 1])
        if not edge_cost:
            continue
        d, s = edge_cost
        total_distance += d
        total_time += d / (s if s > 0 else average_speed_limit)
    return total_distance, total_time


def reconstruct(parents, dest):
    """Reconstruct route from parents dictionary."""
    path = []
    node = dest
    while node is not None:
        path.append(node)
        node = parents.get(node)
    return list(reversed(path))

def astar_search(source, destination):
    from heapq import heappush, heappop

    open_heap = []
    parents = {source: None}
    g_score = {source: 0.0}
    heappush(open_heap, (0.0, source))

    while open_heap:
        f, current = heappop(open_heap)
        if current == destination:
            return reconstruct(parents, destination)

        for edge in highway_map.get(current, []):
            neighbor = edge.city_two if edge.city_one == current else edge.city_one

            if routing_option == "segments":
                g = g_score[current] + 1
            elif routing_option == "time":
                g = g_score[current] + edge.distance / (edge.speed_limit or average_speed_limit)
            else:
                g = g_score[current] + edge.distance

            if neighbor not in g_score or g < g_score[neighbor]:
                g_score[neighbor] = g
                parents[neighbor] = current

                if routing_option == "segments":
                    h = 1
                elif routing_option == "time":
                    h = displacement(neighbor, destination) / average_speed_limit
                else:
                    h = displacement(neighbor, destination)

                f_score = g + h
                heappush(open_heap, (f_score, neighbor))
    return None


def bfs_search(source, destination):
    from collections import deque

    q = deque([source])
    parents = {source: None}
    visited = {source}

    while q:
        current = q.popleft()
        if current == destination:
            return reconstruct(parents, destination)

        for edge in highway_map.get(current, []):
            neighbor = edge.city_two if edge.city_one == current else edge.city_one
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = current
                q.append(neighbor)
    return None


def dfs_search(source, destination, limit=None):
    stack = [(source, 0)]
    parents = {source: None}
    visited = set()

    while stack:
        current, depth = stack.pop()
        if current == destination:
            return reconstruct(parents, destination)
        if current in visited:
            continue
        visited.add(current)
        if limit is not None and depth > limit:
            continue
        for edge in highway_map.get(current, []):
            neighbor = edge.city_two if edge.city_one == current else edge.city_one
            if neighbor not in visited:
                parents[neighbor] = current
                stack.append((neighbor, depth + 1))
    return None


def ids_search(source, destination, max_depth=50):
    for depth in range(1, max_depth + 1):
        route = dfs_search(source, destination, depth)
        if route:
            return route
    return None

if source == destination:
    print("You are already at your destination!")
    sys.exit()

approx = displacement(source, destination)
print(f"Approximate distance: {approx:.2f} miles")
print(f"Approximate time: {approx / average_speed_limit:.2f} hours")
print("Hang On!!... Calibrating route")

# ---- Route Selection ----
if routing_algorithm == "astar":
    route = astar_search(source, destination)
elif routing_algorithm == "bfs":
    route = bfs_search(source, destination)
elif routing_algorithm == "dfs":
    route = dfs_search(source, destination)
elif routing_algorithm == "ids":
    route = ids_search(source, destination, 200)
else:
    print("Invalid algorithm.")
    sys.exit()

if not route:
    print("No route found.")
    sys.exit()

total_distance, total_time = get_overall_cost(route)
print(f"Overall distance: {total_distance:.2f} miles")
print(f"Overall time: {total_time:.2f} hours")
print(f"No of segments: {len(route) - 1}")

for i in range(len(route) - 1):
    c1, c2 = route[i], route[i + 1]
    for edge in highway_map[c1]:
        if edge.city_one == c2 or edge.city_two == c2:
            print(f"From {c1} go to {c2} on highway {edge.name} for {edge.distance} miles")
            break

print("\nPath:", " -> ".join(route))

if plot_flag:
    try:
        import matplotlib.pyplot as plt
        xs, ys, names = [], [], []
        for city_name in route:
            c = city_map.get(city_name)
            if c and c.latitude and c.longitude:
                xs.append(c.longitude)
                ys.append(c.latitude)
                names.append(city_name)

        if len(xs) > 1:
            plt.figure(figsize=(8, 6))
            plt.plot(xs, ys, '-o', color='blue')
            for i, name in enumerate(names):
                plt.text(xs[i], ys[i], name, fontsize=8)
            plt.title(f"Route from {source} to {destination}")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.grid(True)
            plt.show()
        else:
            print("Insufficient coordinate data to plot.")
    except Exception as e:
        print("Plotting failed:", e)

city_coords = {}
for entry in city:
    if len(entry) >= 3:
        try:
            lat = float(entry[1]) if entry[1] else 0.0
            lon = float(entry[2]) if entry[2] else 0.0
            if lat != 0.0 and lon != 0.0:
                city_coords[entry[0]] = (lat, lon)
        except ValueError:
            continue


def plot_route_on_map(route_cities, city_coords):
    coords = [city_coords[c] for c in route_cities if c in city_coords]
    if not coords:
        print("No valid coordinates found for plotting.")
        return

    avg_lat = sum(lat for lat, _ in coords) / len(coords)
    avg_lon = sum(lon for _, lon in coords) / len(coords)
    route_map = folium.Map(location=(avg_lat, avg_lon), zoom_start=6)

    folium.PolyLine(coords, color="red", weight=4, opacity=0.8).add_to(route_map)

    for i, city in enumerate(route_cities):
        if city in city_coords:
            lat, lon = city_coords[city]
            folium.Marker(
                [lat, lon],
                popup=city,
                tooltip=("Start" if i == 0 else "Destination" if i == len(route_cities) - 1 else city)
            ).add_to(route_map)

    route_map.save("route_map.html")
    print("Route map saved as route_map.html")

if plot_flag and folium:
    plot_route_on_map(route, city_coords)
    map_path = os.path.abspath("route_map.html")
    webbrowser.open(f"file://{map_path}")
