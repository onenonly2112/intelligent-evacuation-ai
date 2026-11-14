import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyRiskEvaluator:
    """
    Mamdani Fuzzy Inference System to compute corridor risk score (0 to 1)
    from Temperature, Smoke Density, and Crowd Congestion.
    """
    def __init__(self):
        # 1. Define Antecedents (Inputs)
        self.temp = ctrl.Antecedent(np.arange(0, 121, 1), 'temperature')
        self.smoke = ctrl.Antecedent(np.arange(0, 101, 1), 'smoke')
        self.crowd = ctrl.Antecedent(np.arange(0, 101, 1), 'crowd')

        # 2. Define Consequent (Output)
        self.risk = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'risk')

        # 3. Membership Functions
        self.temp['safe'] = fuzz.trimf(self.temp.universe, [0, 20, 45])
        self.temp['warm'] = fuzz.trimf(self.temp.universe, [35, 55, 75])
        self.temp['extreme'] = fuzz.trimf(self.temp.universe, [65, 95, 120])

        self.smoke['clear'] = fuzz.trimf(self.smoke.universe, [0, 0, 30])
        self.smoke['hazy'] = fuzz.trimf(self.smoke.universe, [20, 50, 75])
        self.smoke['dense'] = fuzz.trimf(self.smoke.universe, [60, 85, 100])

        self.crowd['low'] = fuzz.trimf(self.crowd.universe, [0, 0, 40])
        self.crowd['moderate'] = fuzz.trimf(self.crowd.universe, [30, 55, 80])
        self.crowd['congested'] = fuzz.trimf(self.crowd.universe, [70, 90, 100])

        self.risk['low'] = fuzz.trimf(self.risk.universe, [0.0, 0.15, 0.35])
        self.risk['medium'] = fuzz.trimf(self.risk.universe, [0.25, 0.50, 0.75])
        self.risk['high'] = fuzz.trimf(self.risk.universe, [0.65, 0.85, 1.0])

        # 4. Fuzzy Rule Base
        rules = [
            ctrl.Rule(self.temp['extreme'] | self.smoke['dense'], self.risk['high']),
            ctrl.Rule(self.temp['warm'] & self.smoke['hazy'], self.risk['high']),
            ctrl.Rule(self.smoke['hazy'] & self.crowd['congested'], self.risk['high']),
            ctrl.Rule(self.temp['warm'] & self.smoke['clear'], self.risk['medium']),
            ctrl.Rule(self.crowd['moderate'] & self.smoke['clear'], self.risk['medium']),
            ctrl.Rule(self.temp['safe'] & self.smoke['clear'] & self.crowd['low'], self.risk['low']),
        ]

        self.risk_ctrl = ctrl.ControlSystem(rules)
        self.simulator = ctrl.ControlSystemSimulation(self.risk_ctrl)

    def compute_risk(self, temperature, smoke_density, crowd_count):
        self.simulator.input['temperature'] = min(max(temperature, 0), 120)
        self.simulator.input['smoke'] = min(max(smoke_density, 0), 100)
        self.simulator.input['crowd'] = min(max(crowd_count, 0), 100)
        self.simulator.compute()
        return round(float(self.simulator.output['risk']), 3)


def bayesian_failure_probability(temp, smoke, structural_damage):
    """
    Bayesian Inference estimating P(Route_Failure | Evidence).
    Uses conditional probability tables (CPTs) for probabilistic reasoning.
    """
    # Prior probability of corridor failure under normal conditions
    p_fail = 0.02

    # Likelihood multipliers based on observed sensor evidence
    if structural_damage:
        p_fail = 0.95
    else:
        # Bayesian update using noisy-OR combination of independent hazard causes
        p_heat_fail = 0.75 if temp > 70 else (0.25 if temp > 45 else 0.01)
        p_smoke_fail = 0.80 if smoke > 70 else (0.30 if smoke > 40 else 0.01)
        p_fail = 1.0 - ((1.0 - p_fail) * (1.0 - p_heat_fail) * (1.0 - p_smoke_fail))

    return round(min(p_fail, 0.99), 3)


class EmergencyExpertSystem:
    """
    Rule-Based Expert System + AI Ethics Enforcement Engine.
    Evaluates graph edges and generates human-readable XAI audit logs.
    """
    def __init__(self, fuzzy_engine):
        self.fuzzy_engine = fuzzy_engine
        self.audit_logs = []

    def evaluate_building(self, G, fire_active=True, mobility_mode="Standard"):
        self.audit_logs = []

        # Global Safety Rules
        if fire_active:
            self.audit_logs.append(
                "[RULE-01 SAFETY]: Fire protocol active -> All elevators locked and marked impassable."
            )
        if mobility_mode == "Wheelchair / Assisted":
            self.audit_logs.append(
                "[RULE-02 AI ETHICS]: Accessibility priority enabled -> Penalizing/avoiding steep stairs where ramp/refuge exists."
            )

        for u, v, data in G.edges(data=True):
            # 1. Compute Fuzzy Risk
            f_risk = self.fuzzy_engine.compute_risk(
                data['temperature'], data['smoke_density'], data['crowd_count']
            )
            # 2. Compute Bayesian Failure Probability
            b_prob = bayesian_failure_probability(
                data['temperature'], data['smoke_density'], data['structural_damage']
            )

            data['fuzzy_risk'] = f_risk
            data['failure_prob'] = b_prob
            data['blocked'] = False

            # 3. Production Rules (IF-THEN)
            if fire_active and data['edge_type'] == 'elevator':
                data['blocked'] = True

            elif data['structural_damage'] or f_risk >= 0.80 or b_prob >= 0.85:
                data['blocked'] = True
                self.audit_logs.append(
                    f"[RULE-03 HAZARD]: Blocked edge ({u} <-> {v}) | Fuzzy Risk={f_risk}, Failure Prob={b_prob*100:.0f}%."
                )

            elif mobility_mode == "Wheelchair / Assisted" and data['edge_type'] == 'stairs':
                # In ethics mode, flag stairs as high-assistance/restricted unless emergency refuge
                data['blocked'] = True
                self.audit_logs.append(
                    f"[RULE-04 ACCESSIBILITY]: Excluded stairs ({u} <-> {v}) for wheelchair user safety."
                )

            # 4. Calculate Composite Safe Edge Weight for Risk-Weighted A*
            # Formula: Cost = Distance * (1 + alpha * Fuzzy_Risk + beta * Failure_Prob)
            alpha, beta = 4.0, 5.0
            data['safe_weight'] = round(
                data['distance'] * (1.0 + alpha * f_risk + beta * b_prob), 2
            )

        return G, self.audit_logs