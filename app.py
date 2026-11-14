import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from building_graph import create_building_graph, inject_emergency_scenario
from intelligence_engine import FuzzyRiskEvaluator, EmergencyExpertSystem
from search_algorithms import run_bfs, run_dfs, run_astar

st.set_page_config(page_title="Smart Evacuation AI", layout="wide")

st.title("🚨 Intelligent Emergency Response & Smart Evacuation Optimizer")
st.markdown("**Hybrid AI System:** IoT Simulation • Fuzzy Logic • Bayesian Risk • Rule-Based Expert System • Heuristic $A^*$ Search")

# --- SIDEBAR: IoT & SCENARIO CONTROLS ---
st.sidebar.header("1. Evacuation Parameters")
start_node = st.sidebar.selectbox(
    "Current Location (Start Node):",
    ["Class_101", "Class_102", "Corridor_1A", "Corridor_1B", "Lab_G1", "Lab_G2"]
)

mobility_mode = st.sidebar.radio(
    "AI Ethics & Accessibility Profile:",
    ["Standard", "Wheelchair / Assisted"]
)

st.sidebar.header("2. Emergency Scenario (IoT Feed)")
scenario = st.sidebar.selectbox(
    "Select Preset Emergency:",
    ["Normal (No Hazard)", "Fire in Corridor 1B", "Ground Floor Exit Blockage"]
)

st.sidebar.header("3. Live IoT Sensor Override")
st.sidebar.caption("Adjust Corridor 1A <-> 1B sensors dynamically:")
custom_temp = st.sidebar.slider("Corridor 1A-1B Temp (°C)", 20, 120, 25)
custom_smoke = st.sidebar.slider("Corridor 1A-1B Smoke (%)", 0, 100, 5)
custom_crowd = st.sidebar.slider("Corridor 1A-1B Crowd (%)", 0, 100, 10)

# --- INITIALIZE GRAPH & AI PIPELINE ---
G = create_building_graph()
if scenario != "Normal (No Hazard)":
    G = inject_emergency_scenario(G, scenario)

# Apply manual slider overrides if user moved them from defaults
if custom_temp != 25 or custom_smoke != 5 or custom_crowd != 10:
    G["Corridor_1A"]["Corridor_1B"].update({
        "temperature": float(custom_temp),
        "smoke_density": float(custom_smoke),
        "crowd_count": float(custom_crowd)
    })

fire_active = (scenario != "Normal (No Hazard)") or (custom_temp > 50 or custom_smoke > 40)

fuzzy_engine = FuzzyRiskEvaluator()
expert_system = EmergencyExpertSystem(fuzzy_engine)
G, audit_logs = expert_system.evaluate_building(G, fire_active=fire_active, mobility_mode=mobility_mode)

exits = [n for n, d in G.nodes(data=True) if d['type'] == 'exit']

# --- RUN ALL 4 SEARCH ALGORITHMS ---
res_bfs = run_bfs(G, start_node, exits)
res_dfs = run_dfs(G, start_node, exits)
res_std_astar = run_astar(G, start_node, exits, risk_aware=False)
res_safe_astar = run_astar(G, start_node, exits, risk_aware=True)

# --- TOP METRICS BANNER ---
col1, col2, col3, col4 = st.columns(4)
if res_safe_astar["found"]:
    col1.metric("Optimal Safe Exit", res_safe_astar["path"][-1])
    col2.metric("Safe Path Distance", f"{res_safe_astar['distance_m']} m")
    col3.metric("Cumulative Fuzzy Risk", res_safe_astar["total_risk_score"])
    col4.metric("Max Failure Probability", res_safe_astar["max_failure_prob"])
else:
    st.error("⚠️ CRITICAL ALERT: No safe unobstructed route found under current constraints! Dispatching rescue protocol.")

# --- VISUAL FLOOR PLAN MAP ---
st.subheader("🗺️ Multi-Floor Building Graph & Optimal Evacuation Route")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
floors = [(1, "First Floor (Level 1)"), (0, "Ground Floor (Level 0)")]
optimal_edges = set()
if res_safe_astar["found"]:
    p = res_safe_astar["path"]
    optimal_edges = {(p[i], p[i+1]) for i in range(len(p)-1)} | {(p[i+1], p[i]) for i in range(len(p)-1)}

for ax, (floor_num, title) in zip(axes, floors):
    floor_nodes = [n for n, d in G.nodes(data=True) if d['pos'][2] == floor_num]
    subG = G.subgraph(floor_nodes)
    pos_2d = {n: (G.nodes[n]['pos'][0], G.nodes[n]['pos'][1]) for n in floor_nodes}

    # Color nodes by role
    node_colors = []
    for n in floor_nodes:
        if n == start_node:
            node_colors.append("#FFD700")  # Gold = Start
        elif G.nodes[n]['type'] == 'exit':
            node_colors.append("#2ECC71")  # Green = Exit
        elif G.nodes[n]['type'] == 'stairs':
            node_colors.append("#3498DB")  # Blue = Stairs
        elif G.nodes[n]['type'] == 'elevator':
            node_colors.append("#95A5A6")  # Grey = Elevator
        else:
            node_colors.append("#ECF0F1")  # Light = Room/Corridor

    # Color edges by status
    edge_colors = []
    edge_widths = []
    for u, v in subG.edges():
        if (u, v) in optimal_edges:
            edge_colors.append("#27AE60")  # Bright Green = Chosen Safe Path
            edge_widths.append(4.0)
        elif G[u][v].get('blocked', False):
            edge_colors.append("#E74C3C")  # Red = Blocked / Extreme Hazard
            edge_widths.append(3.0)
        elif G[u][v]['fuzzy_risk'] > 0.4:
            edge_colors.append("#F39C12")  # Orange = Elevated Risk
            edge_widths.append(2.5)
        else:
            edge_colors.append("#BDC3C7")  # Grey = Normal
            edge_widths.append(1.5)

    plt.sca(ax)
    nx.draw(
        subG, pos_2d, ax=ax, with_labels=True,
        node_color=node_colors, node_size=1100, font_size=8, font_weight="bold",
        edge_color=edge_colors, width=edge_widths
    )
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlim(-2, 14)
    ax.set_ylim(-2, 12)

st.pyplot(fig)
st.caption("Legend: 🟡 Start Node | 🟢 Safe Exit / Optimal Route | 🔵 Stairs | 🔴 Blocked / Extreme Hazard | 🟠 Medium Fuzzy Risk")

# --- ALGORITHM COMPARISON TABLE ---
st.subheader("📊 Syllabus Algorithm Comparison (Live Benchmark)")
comparison_data = [
    {"Algorithm": "BFS (Uninformed)", **res_bfs, "Route": " → ".join(res_bfs["path"])},
    {"Algorithm": "DFS (Uninformed)", **res_dfs, "Route": " → ".join(res_dfs["path"])},
    {"Algorithm": "Standard A* (Distance Only)", **res_std_astar, "Route": " → ".join(res_std_astar["path"])},
    {"Algorithm": "Risk-Weighted A* (Proposed AI)", **res_safe_astar, "Route": " → ".join(res_safe_astar["path"])},
]
df = pd.DataFrame(comparison_data)[
    ["Algorithm", "found", "distance_m", "total_risk_score", "max_failure_prob", "nodes_expanded", "time_ms", "Route"]
]
df.columns = ["Algorithm", "Success", "Distance (m)", "Cumulative Fuzzy Risk", "Max Failure Prob", "Nodes Expanded", "Time (ms)", "Evacuation Path"]
st.dataframe(df, use_container_width=True)

# --- EXPERT SYSTEM & XAI AUDIT LOGS ---
st.subheader("🧠 Expert System Rules & Explainable AI (XAI) Audit Log")
if audit_logs:
    for log in audit_logs:
        st.info(log)
else:
    st.success("All building corridors operating within nominal safety thresholds. No emergency overrides triggered.")