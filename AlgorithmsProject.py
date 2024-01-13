from dijkstra import *
from bellman_ford import *
import matplotlib.pyplot as plt
import pandas as pd
from mst import *
import time as tm

""" Loading the data """
# Read the Excel file
df = pd.read_excel("london_underground_data.xlsx")

""" Stripping empty spaces before and after the strings from the excel file"""
df['Line'] = df['Line'].str.strip()
df['Station'] = df['Station'].str.strip()
df['Connection'] = df['Connection'].str.strip()

filtered_dataset = df[df["Connection"].isna() & df['Time'].isna()]  # filtering for the stations without connections

i = 0
stations_to_int = {}  # mapping station names to int
int_to_stations = {}  # mapping int to station names
connections = []  # list to store all the connected stations and their time
vertices = []

""" mapping stations to int  """
for column, row in filtered_dataset.iterrows():
    if row.iloc[1].upper() in stations_to_int:
        continue
    if row.iloc[1].upper() not in stations_to_int:
        stations_to_int[row.iloc[1].upper()] = i
        vertices.append(row.iloc[1])
        i += 1

""" mapping the int to station names """
for key in stations_to_int:
    int_to_stations[stations_to_int[key]] = key
    # vertices.append(stations_to_int[key])

filtered_dataset = df[df["Connection"].notna() & df['Time'].notna()]

for column, row in filtered_dataset.iterrows():
    connections.append((row.iloc[1].upper(), row.iloc[2].upper(), int(row.iloc[3])))

""" Sorting the connections by their  travel time, this way the lowest time will be loaded."""
connections = sorted(connections, key=lambda conect: conect[2])

""" Loading  the graph and creating the edges """
graph1 = AdjacencyListGraph(len(stations_to_int), directed=False, weighted=True)  # edg weights as travel time
graph2 = AdjacencyListGraph(len(stations_to_int), directed=False, weighted=True)  # edge weigths as stops

for i in range(len(connections)):
    station = stations_to_int[connections[i][0]]
    connected_st = stations_to_int[connections[i][1]]
    time = connections[i][2]
    try:
        graph1.insert_edge(station, connected_st, time)
        graph2.insert_edge(station, connected_st, 1)
    except RuntimeError as e:
        continue


def backtracking(starting_point, destination, distance, pi):
    shortest_route = []  # list for storing shortest-route
    journey_time = distance[destination]
    while True:
        if pi[destination] is not None:
            shortest_route.append(destination)
            destination = pi[destination]
        else:
            shortest_route.append(starting_point)
            break
    shortest_route = shortest_route[::-1]
    return shortest_route, journey_time


"""" Computing all station pair combinations and storing a list with  all the station pairs, stops, travel times"""


def calculate_all_shortest_paths(graph, station_names_to_ids, station_ids_to_names, shortest_path_algo):
    all_paths = []
    all_stops = []
    total_time = []
    computed_paths = {}

    for starting_point_id, starting_point_name in station_ids_to_names.items():
        # run dijkstra with station id nr
        if shortest_path_algo == dijkstra:
            dist, pi = dijkstra(graph, starting_point_id)
        elif shortest_path_algo == bellman_ford:
            dist, pi, cycle = bellman_ford(graph, starting_point_id)

        for destination_point_id, destination_point_name in station_ids_to_names.items():
            if starting_point_id != destination_point_id:
                path_key = tuple(sorted((starting_point_id, destination_point_id)))
                if path_key not in computed_paths:
                    # backtracking all stations from this starting point
                    path_with_id, shortest_path_time = backtracking(starting_point_id, destination_point_id, dist, pi)
                    # Computing the path and storing it in a dictionary
                    computed_paths[path_key] = shortest_path_time
                    path_by_name = []
                    # Not using this loop, might delete!
                    for stop in path_with_id:
                        path_by_name.append(station_ids_to_names[stop])

                    all_paths.append((starting_point_name, destination_point_name))
                    all_stops.append(len(path_by_name) - 1)
                    # print(shortest_path_time)
                    total_time.append(shortest_path_time)
                    # print("start:", starting_point_name, "destination:",  destination_point_name,"time:", time)
    return all_paths, all_stops, total_time


def display_histogram(histogram_data, bins, title, xlabel):
    plt.hist(histogram_data, bins=bins, edgecolor='black')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.show()


def user_input_route():
    """ Collection user input """
    starting_point = input("Please enter your first station:").upper()
    starting_point = stations_to_int[starting_point]
    destination = input("Please enter your destination station:").upper()
    destination = stations_to_int[destination]
    print("")  # console space
    return starting_point, destination


""" Task 1"""
print("Task 1")
# Subtask 1a
start = tm.time()

starting_point, destination = user_input_route()
d, pi = dijkstra(graph1, starting_point)

user_shortest_rt, shortest_path_time = backtracking(starting_point, destination, d, pi)
print("Your shortest route is:")
for station in user_shortest_rt:
    print("->", int_to_stations[station])

print("")
print(f"You have {len(user_shortest_rt) - 1} stops until you reach your destination")
print(f"Your expected journey time is {shortest_path_time} minutes")
print("")
end = tm.time()
task1a_time = end - start
print("The time to run task 1a in seconds is: ", str(round(task1a_time, 2)), "seconds")
# Subtask 1b
start = tm.time()
station_pairs, stops, total_travel_times = calculate_all_shortest_paths(graph1, stations_to_int, int_to_stations,
                                                                        dijkstra)

# print(total_travel_times)
""" Delete these 2 lines after testing """
print("Max Dijkstra:", max(stops))
print("Average Dijkstra", sum(stops) / len(stops), "\n ")

bins = []
print("Number of station pairs", len(stops))
for i in range(0, max(total_travel_times) + 1, 2):
    bins.append(i)

display_histogram(total_travel_times, bins, 'Travel Time Between Each Station Pair (Dijkstra)', 'Travel Time Range')

end = tm.time()
task1b_time = end- start
print("The time to run task 1b in seconds is: ", str(round(task1b_time, 2)), "seconds")

""" Task 2 """
print("Task 2")
# Subtask 2a
start = tm.time()
# starting_point, destination = user_input_route()

""" IDK if i need to run it again for this task if i have the data from Task 1???"""
d, pi = dijkstra(graph2, starting_point)
user_shortest_rt, shortest_path_time = backtracking(starting_point, destination, d, pi)

print("Your shortest route with the least number of stops is:")
for station in user_shortest_rt:
    print("->", int_to_stations[station])

print("")
print(f"You have {len(user_shortest_rt) - 1} stops until you reach your destination")
print("")
end = tm.time()
task2a_time = end - start

# Subtask 2a
station_pairs, stops, total_travel_times = calculate_all_shortest_paths(graph2, stations_to_int, int_to_stations,
                                                                        dijkstra)
print("The time to run task 1b in seconds is: ", str(round(task2a_time, 2)), "seconds")
# print("STOPS", max(stops))
# print("Time", max(total_travel_times))
start = tm.time()
bins = []
for i in range(max(stops) + 1):
    bins.append(i)

display_histogram(stops, bins, 'Number Of Stops Between Each Station Pair (Dijkstra)', 'Nr of Stops range')

end = tm.time()
task2b_time = end - start
print("The time to run task 2b in seconds is: ", str(round(task2b_time, 2)), "seconds")

""" Task 3 """
print("Task 3")
start = tm.time()
# Subtask 3a
d, pi, cycle = bellman_ford(graph2, starting_point)
user_shortest_rt, shortest_path_time = backtracking(starting_point, destination, d, pi)
shortest_rt = []  # list for storing shortest-route
if cycle is False:
    i = 0
    while i <= len(pi):
        shortest_rt.append(destination)
        destination = pi[destination]
        i += 1
    print("Can't find shortest route, graph has a negative cycle")
    print("the negative cycle is between:", int_to_stations[shortest_rt[-1]], "-", int_to_stations[shortest_rt[-2]])
else:
    user_shortest_rt, shortest_path_time = backtracking(starting_point, destination, d, pi)

print("Your shortest route with the least number of stops is:")
for station in user_shortest_rt:
    print("->", int_to_stations[station])

print("")
print(f"You have {len(user_shortest_rt) - 1} stops until you reach your destination")
print("")
end = tm.time()
task3a_time = end - start
print("The time to run task 3a in seconds is: ", str(round(task3a_time, 2)), "seconds")
# Subtask 3b
start = tm.time()
bf_station_pairs, bf_stops, bf_total_travel_times = calculate_all_shortest_paths(graph2, stations_to_int,
                                                                                 int_to_stations, bellman_ford)
bins = []
# print("STOPS", max(bf_stops))
# print("Time:", max(total_travel_times))
for i in range(max(bf_stops) + 2):
    bins.append(i)

display_histogram(bf_stops, bins, 'Number Of Stops Between Each Station Pair (Bellman-Ford)', 'Nr Of Stops Range')
end = tm.time()
task3b_time = end - start
print("The time to run task 3b in seconds is: ", str(round(task3b_time, 2)), "seconds")

""" Task 4 """
print("Task 4")
start = tm.time()
# Subtask 4a
mst_travel_time = kruskal(graph1)
mst_no_of_stops = kruskal(graph2)

full_edge_list = set(graph1.get_edge_list())
max_closure = set(mst_travel_time.get_edge_list())
deleted_edges = full_edge_list.difference(max_closure)

print("London Underground will have the following connections closed down:")
for closed_edges in deleted_edges:
    station, connection = int_to_stations[closed_edges[0]], int_to_stations[closed_edges[1]]

    deleted_edges_lines = {}

    line = None
    for i, row in filtered_dataset.iterrows():
        if (row['Station'].upper() == station and row['Connection'].upper() == connection) or \
           (row['Station'].upper() == connection and row['Connection'].upper() == station):
            line = row['Line']
            break

    if line not in deleted_edges_lines:
        deleted_edges_lines[line] = []
    deleted_edges_lines[line].append((station, connection))

    for line, closed_edges in deleted_edges_lines.items():
        for station, connection in closed_edges:
            print("Stations closed on: ", line.upper(), "LINE: ", station, "<-->", connection)
end = tm.time()
task4a_time = end - start
print("The time to run task 4a in seconds is: ", str(round(task4a_time, 2)), "seconds")
# Subtask 4b
station_pairs, stops, total_travel_times = calculate_all_shortest_paths(mst_travel_time, stations_to_int,
                                                                        int_to_stations, dijkstra)

# print(max(total_travel_times))
bins = []
for i in range(0, max(total_travel_times) + 1, 2):
    bins.append(i)

display_histogram(total_travel_times, bins, "Travel Time Between Each Station Pair After Closure (Kruskal)",
                  "Travel Time Range")

# print(max(stops))
bins = []
for i in range(max(stops) + 1):
    bins.append(i)

display_histogram(stops, bins, 'Number Of Stops Between Each Station Pair After Closure (MST-Kruskal)',
                  'No of Stops Range')
station_pairs, stops, total_travel_times = calculate_all_shortest_paths(mst_no_of_stops, stations_to_int,
                                                                        int_to_stations, dijkstra)

print("Connections Initial vs MST")
print(graph1.get_card_E())
mst_travel_time = kruskal(graph1)
print(mst_travel_time.get_card_E())

print("No. of Stations initial vs MST")
print(graph1.get_card_V())
print(mst_travel_time.get_card_V())
print("Deleted connections")
print(graph1.get_card_E() - mst_travel_time.get_card_E())

print("Dijkstra again with MST")

d, pi = dijkstra(mst_travel_time, starting_point)
user_shortest_rt, shortest_path_time = backtracking(starting_point, destination, d, pi)
print("Your shortest route is:")
for station in user_shortest_rt:
    print("->", int_to_stations[station])

print("")
print(f"You have {len(user_shortest_rt) - 1} stops until you reach your destination")
print(f"Your expected journey time is {shortest_path_time} minutes")
print("")
