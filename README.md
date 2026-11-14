# 🚨 Intelligent Emergency Response & Smart Evacuation Route Optimizer

A Hybrid AI evacuation system combining **IoT Sensor Simulation**, **Mamdani Fuzzy Logic**, **Bayesian Probabilistic Reasoning**, a **Rule-Based Expert System**, and **Risk-Weighted A\* Heuristic Search** with **AI Ethics & Accessibility** constraints.

## 👨‍💻 Team Members
* **Fiza Mehta** (CSE-AI, IGDTUW)
* **Garry Sidhu** (CSE-AI, IGDTUW)

## 🧠 AI Syllabus Architecture
| AI Concept | Implementation |
| :--- | :--- |
| **IoT Simulation** | Real-time edge attributes for Temperature ($^\circ\text{C}$), Smoke Density ($\%$), Crowd Count ($\%$), and Structural Damage |
| **Fuzzy Logic** | `scikit-fuzzy` Mamdani controller converting noisy sensor readings into a continuous Corridor Risk Score ($0.0 - 1.0$) |
| **Probabilistic Reasoning** | Bayesian Noisy-OR inference estimating $P(\text{Route Failure} \mid \text{Sensor Evidence})$ |
| **Heuristic Search** | Side-by-side benchmark of BFS, DFS, Standard $A^*$, and Risk-Weighted $A^*$ using admissible 3D Euclidean distance |
| **Expert System & Ethics** | Forward-chaining `IF-THEN` safety rules (elevator lockouts, wheelchair stair exclusions, XAI audit logs) |

## 🚀 How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py