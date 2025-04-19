# Multi-run average taste preference simulator with intervention strategies
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.sidebar.title("Simulation Settings")
relapse_chance = st.sidebar.slider("Relapse Chance (Daily)", 0.0, 1.0, 0.1, step=0.01)
relapse_impact = st.sidebar.slider("Relapse Impact", 0.0, 3.0, 1.5, step=0.1)
decay_rate = st.sidebar.slider("Base Decay Rate", 0.01, 0.2, 0.05, step=0.01)
final_sweetness = st.sidebar.slider("Target Sweetness", 0.0, 5.0, 2.0, step=0.5)
days = st.sidebar.slider("Simulation Days", 30, 120, 60)
num_runs = st.sidebar.slider("Number of Runs (Averaged)", 1, 100, 20)

user_profiles = {
    "High Dependency": st.sidebar.slider("Initial - High Dependency", 5.0, 10.0, 10.0),
    "Moderate Dependency": st.sidebar.slider("Initial - Moderate Dependency", 3.0, 9.0, 7.0),
    "Health Conscious": st.sidebar.slider("Initial - Health Conscious", 1.0, 7.0, 4.0),
}

st.sidebar.title("Intervention Strategy")
strategy = st.sidebar.selectbox("Select Strategy", ["Reward-Based", "Punishment-Based", "Companion-Based"])

max_red_hearts = 5
give_up_threshold = 8

# Simulation for one run
def simulate_user_once(initial_pref, strategy):
    sweetness = []
    red_hearts = max_red_hearts
    relapse_streak = 0
    current_pref = initial_pref

    for day in range(days):
        decay = decay_rate

        if strategy == "Reward-Based" and relapse_streak == 0:
            decay *= 1.5
        elif strategy == "Punishment-Based" and (relapse_streak >= 2 or red_hearts <= 1):
            decay *= 2.0
        elif strategy == "Companion-Based" and relapse_streak >= 2:
            relapse_streak = 0
            continue

        if np.random.rand() < relapse_chance:
            current_pref += relapse_impact
            red_hearts -= 1
            relapse_streak += 1
        else:
            relapse_streak = 0
            current_pref -= decay * (current_pref - final_sweetness)

        current_pref = max(0, min(current_pref, 10))

        if relapse_streak >= 3 or red_hearts <= 0 or (day > 10 and current_pref > give_up_threshold):
            sweetness.extend([current_pref] * (days - len(sweetness)))
            break

        sweetness.append(current_pref)

    if len(sweetness) < days:
        sweetness += [current_pref] * (days - len(sweetness))

    return np.array(sweetness)

# Average over multiple runs
def simulate_user_avg(initial_pref, strategy):
    all_runs = np.zeros(days)
    for _ in range(num_runs):
        all_runs += simulate_user_once(initial_pref, strategy)
    return all_runs / num_runs

# Run simulation
st.title("Taste Preference Simulation: Intervention Strategy Comparison")
st.write(f"### Strategy: {strategy} (Averaged over {num_runs} runs)")

fig, ax = plt.subplots(figsize=(12, 6))
results = {}

for profile, start in user_profiles.items():
    avg_curve = simulate_user_avg(start, strategy)
    ax.plot(avg_curve, label=f"{profile} - {strategy}")
    results[profile] = avg_curve

ax.axhline(y=final_sweetness, color='gray', linestyle='--', label='Target Sweetness')
ax.set_title("Average Sweetness Preference Over Time")
ax.set_xlabel("Days")
ax.set_ylabel("Sweetness Preference (0-10)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Export results
df = pd.DataFrame(results)
df["Day"] = np.arange(1, days + 1)
st.dataframe(df.set_index("Day"))
st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name="avg_strategy_simulation.csv", mime="text/csv")
