"""Test with a control group on synthetic data.

Random assignment by last digit of the ID, then payment rate in
treatment against control, with a 95% confidence interval.
"""
import math
import random

random.seed(7)

# Base payment rate and true effect of the action, per portfolio (invented).
PORTFOLIOS = {
    "A": {"customers": 10000, "base_rate": 0.030, "lift": 0.030},
    "B": {"customers": 10000, "base_rate": 0.050, "lift": 0.002},
}
CONTROL_DIGIT = 0  # IDs ending in 0 go to control: about 10%


def simulate(name, cfg):
    rows = []
    for _ in range(cfg["customers"]):
        customer_id = random.randint(10_000_000, 45_000_000)
        group = "control" if customer_id % 10 == CONTROL_DIGIT else "treatment"
        rate = cfg["base_rate"] + (cfg["lift"] if group == "treatment" else 0)
        paid = random.random() < rate
        rows.append((name, customer_id, group, paid))
    return rows


def rate(rows, group):
    sel = [r for r in rows if r[2] == group]
    n = len(sel)
    paid = sum(1 for r in sel if r[3])
    return paid / n, n


def report(name, rows):
    p_t, n_t = rate(rows, "treatment")
    p_c, n_c = rate(rows, "control")
    diff = p_t - p_c
    se = math.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    low, high = diff - 1.96 * se, diff + 1.96 * se
    verdict = "effect" if low > 0 or high < 0 else "no effect shown"
    print(f"Portfolio {name}")
    print(f"  treatment: {p_t:.2%} of {n_t}   control: {p_c:.2%} of {n_c}")
    print(f"  difference: {diff * 100:+.2f} points  (95% CI {low * 100:+.2f} to {high * 100:+.2f})")
    print(f"  ratio: {p_t / p_c:.2f}x   ->  {verdict}")
    print()


if __name__ == "__main__":
    for name, cfg in PORTFOLIOS.items():
        report(name, simulate(name, cfg))
