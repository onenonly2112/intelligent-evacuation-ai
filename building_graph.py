import networkx as nx
import random

def create_building_graph():
    """
    Creates a realistic 2-floor building graph with coordinates (x, y, floor)
    and simulated IoT sensor readings on each edge (corridor/stair).
    """
    G = nx.Graph()

    # Define Nodes: (x, y, floor, node_type)
    nodes = {
        # Ground Floor (floor = 0)
        "Lab_G1":      {"pos": (0, 10, 0), "type": "room"},
        "Lab_G2":      {"pos": (10, 10, 0), "type": "room"},
        "Corridor_G1": {"pos": (0, 5, 0),  "type": "corridor"},
        "Corridor_G2": {"pos": (5, 5, 0),  "type": "corridor"},
        "Corridor_G3": {"pos": (10, 5, 0), "type": "corridor"},
        "Stairs_West_G": {"pos": (0, 0, 0), "type": "stairs"},
        "Stairs_East_G": {"pos": (10, 0, 0), "type": "stairs"},
        "Exit_Main":   {"pos": (5, 0, 0),  "type": "exit"},
        "Exit_East":   {"pos": (12, 0, 0), "type": "exit"},

        # First Floor (floor = 1)
        "Class_101":   {"pos": (0, 10, 1), "type": "room"},
        "Class_102":   {"pos": (10, 10, 1), "type": "room"},
        "Corridor_1A": {"pos": (0, 5, 1),  "type": "corridor"},
        "Corridor_1B": {"pos": (5, 5, 1),  "type": "corridor"},
        "Corridor_1C": {"pos": (10, 5, 1), "type": "corridor"},
        "Stairs_West_1": {"pos": (0, 0, 1), "type": "stairs"},
        "Stairs_East_1": {"pos": (10, 0, 1), "type": "stairs"},
        "Elevator_1":  {"pos": (5, 2, 1),  "type": "elevator"},
        "Elevator_G":  {"pos": (5, 2, 0),  "type": "elevator"},
    }

    for node_id, attrs in nodes.items():
        G.add_node(node_id, **attrs)

    # Define Edges: (node1, node2, distance_meters, edge_type)
    edges = [
        # First Floor Connections
        ("Class_101", "Corridor_1A", 5, "hallway"),
        ("Class_102", "Corridor_1C", 5, "hallway"),
        ("Corridor_1A", "Corridor_1B", 5, "hallway"),
        ("Corridor_1B", "Corridor_1C", 5, "hallway"),
        ("Corridor_1A", "Stairs_West_1", 5, "hallway"),
        ("Corridor_1C", "Stairs_East_1", 5, "hallway"),
        ("Corridor_1B", "Elevator_1", 3, "hallway"),

        # Vertical Connections (Floor 1 <-> Ground Floor)
        ("Stairs_West_1", "Stairs_West_G", 8, "stairs"),
        ("Stairs_East_1", "Stairs_East_G", 8, "stairs"),
        ("Elevator_1", "Elevator_G", 6, "elevator"),

        # Ground Floor Connections
        ("Lab_G1", "Corridor_G1", 5, "hallway"),
        ("Lab_G2", "Corridor_G3", 5, "hallway"),
        ("Corridor_G1", "Corridor_G2", 5, "hallway"),
        ("Corridor_G2", "Corridor_G3", 5, "hallway"),
        ("Corridor_G1", "Stairs_West_G", 5, "hallway"),
        ("Corridor_G3", "Stairs_East_G", 5, "hallway"),
        ("Elevator_G", "Corridor_G2", 3, "hallway"),
        ("Stairs_West_G", "Exit_Main", 5, "hallway"),
        ("Corridor_G2", "Exit_Main", 5, "hallway"),
        ("Stairs_East_G", "Exit_East", 3, "hallway"),
    ]

    for u, v, dist, etype in edges:
        # Default safe IoT sensor baseline
        G.add_edge(
            u, v,
            distance=dist,
            edge_type=etype,
            temperature=25.0,     # Celsius
            smoke_density=5.0,    # Percentage (0-100%)
            crowd_count=10.0,     # Percentage capacity (0-100%)
            structural_damage=False
        )

    return G

def inject_emergency_scenario(G, scenario="Fire in Corridor 1B"):
    """
    Simulates real-time IoT sensor spikes for specific emergencies.
    """
    if scenario == "Fire in Corridor 1B":
        # Severe fire near Corridor_1B and Stairs_West
        G["Corridor_1A"]["Corridor_1B"].update({
            "temperature": 88.0, "smoke_density": 85.0, "crowd_count": 70.0
        })
        G["Corridor_1B"]["Corridor_1C"].update({
            "temperature": 75.0, "smoke_density": 65.0, "crowd_count": 50.0
        })
        G["Corridor_1B"]["Elevator_1"].update({
            "temperature": 92.0, "smoke_density": 90.0, "crowd_count": 20.0
        })

    elif scenario == "Ground Floor Exit Blockage":
        # Heavy smoke & crowd congestion near Exit_Main
        G["Corridor_G2"]["Exit_Main"].update({
            "temperature": 68.0, "smoke_density": 78.0, "crowd_count": 95.0, "structural_damage": True
        })
        G["Stairs_West_G"]["Exit_Main"].update({
            "temperature": 55.0, "smoke_density": 60.0, "crowd_count": 88.0
        })

    return G