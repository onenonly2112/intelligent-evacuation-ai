import heapq
import math
import time
from collections import deque

def euclidean_heuristic(G, node, goal_nodes):
    """
    Admissible 3D Euclidean distance heuristic h(n) to the nearest valid exit.
    Never overestimates true path cost, guaranteeing A* optimality.
    """
    x1, y1, z1 = G.nodes[node]['pos']
    min_dist = float('inf')
    for goal in goal_nodes:
        x2, y2, z2 = G.nodes[goal]['pos']
        # Scale floor difference (z) by 8m (average stair length)
        dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + ((z1 - z2) * 8.0)**2)
        if dist < min_dist:
            min_dist = dist
    return min_dist


def calculate_path_metrics(G, path, nodes_expanded, exec_time_ms):
    """
    Evaluates a found path on physical distance, fuzzy hazard exposure, and safety.
    """
    if not path or len(path) < 2:
        return {
            "path": [],
            "found": False,
            "distance_m": 0,
            "total_risk_score": 0,
            "max_failure_prob": 0,
            "nodes_expanded": nodes_expanded,
            "time_ms": round(exec_time_ms, 3)
        }

    total_dist = 0.0
    total_risk = 0.0
    max_fail = 0.0

    for i in range(len(path) - 1):
        edge = G[path[i]][path[i+1]]
        total_dist += edge['distance']
        total_risk += edge['fuzzy_risk']
        max_fail = max(max_fail, edge['failure_prob'])

    return {
        "path": path,
        "found": True,
        "distance_m": round(total_dist, 1),
        "total_risk_score": round(total_risk, 2),
        "max_failure_prob": f"{max_fail * 100:.0f}%",
        "nodes_expanded": nodes_expanded,
        "time_ms": round(exec_time_ms, 3)
    }


def run_bfs(G, start, exits):
    """Uninformed Breadth-First Search (ignores edge weights & hazards)."""
    t0 = time.perf_counter()
    queue = deque([[start]])
    visited = {start}
    nodes_expanded = 0

    while queue:
        path = queue.popleft()
        curr = path[-1]
        nodes_expanded += 1

        if curr in exits:
            return calculate_path_metrics(G, path, nodes_expanded, (time.perf_counter() - t0) * 1000)

        for neighbor in G.neighbors(curr):
            edge = G[curr][neighbor]
            if not edge.get('blocked', False) and neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return calculate_path_metrics(G, [], nodes_expanded, (time.perf_counter() - t0) * 1000)


def run_dfs(G, start, exits):
    """Uninformed Depth-First Search (often produces sub-optimal, winding paths)."""
    t0 = time.perf_counter()
    stack = [[start]]
    visited = set()
    nodes_expanded = 0

    while stack:
        path = stack.pop()
        curr = path[-1]

        if curr in visited:
            continue
        visited.add(curr)
        nodes_expanded += 1

        if curr in exits:
            return calculate_path_metrics(G, path, nodes_expanded, (time.perf_counter() - t0) * 1000)

        for neighbor in G.neighbors(curr):
            edge = G[curr][neighbor]
            if not edge.get('blocked', False) and neighbor not in visited:
                stack.append(path + [neighbor])

    return calculate_path_metrics(G, [], nodes_expanded, (time.perf_counter() - t0) * 1000)


def run_astar(G, start, exits, risk_aware=True):
    """
    A* Search:
    - If risk_aware=False: Minimizes pure physical distance g(n) + h(n).
    - If risk_aware=True:  Minimizes Fuzzy + Bayesian safe_weight g_safe(n) + h(n).
    """
    t0 = time.perf_counter()
    weight_key = 'safe_weight' if risk_aware else 'distance'

    # Priority queue entries: (f_score, g_score, current_node, path)
    open_set = [(euclidean_heuristic(G, start, exits), 0.0, start, [start])]
    best_g = {start: 0.0}
    nodes_expanded = 0

    while open_set:
        f, g, curr, path = heapq.heappop(open_set)
        nodes_expanded += 1

        if curr in exits:
            return calculate_path_metrics(G, path, nodes_expanded, (time.perf_counter() - t0) * 1000)

        if g > best_g.get(curr, float('inf')):
            continue

        for neighbor in G.neighbors(curr):
            edge = G[curr][neighbor]
            if edge.get('blocked', False):
                continue

            tentative_g = g + edge[weight_key]
            if tentative_g < best_g.get(neighbor, float('inf')):
                best_g[neighbor] = tentative_g
                h = euclidean_heuristic(G, neighbor, exits)
                heapq.heappush(open_set, (tentative_g + h, tentative_g, neighbor, path + [neighbor]))

    return calculate_path_metrics(G, [], nodes_expanded, (time.perf_counter() - t0) * 1000)