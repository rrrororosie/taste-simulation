import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- UI Sidebar ---
st.sidebar.title("Simulation Settings")
relapse_chance = st.sidebar.slider("Relapse Chance (Daily)", 0.0, 1.0, 0.1, step=0.01)
relapse_impact = st.sidebar.slider("Relapse Impact", 0.0, 3.0, 1.5, step=0.1)
decay_rate = st.sidebar.slider("Base Decay Rate", 0.01, 0.2, 0.05, step=0.01)
final_sweetness = st.sidebar.slider("Target Sweetness", 0.0, 5.0, 2.0, step=0.5)
days = st.sidebar.slider("Simulation Days", 30, 120, 60)

# --- User Profiles ---
user_profiles = {
    "High Dependency": st.sidebar.slider("Initial - High Dependency", 5.0, 10.0, 10.0),
    "Moderate Dependency": st.sidebar.slider("Initial - Moderate Dependency", 3.0, 9.0, 7.0),
    "Health Conscious": st.sidebar.slider("Initial - Health Conscious", 1.0, 7.0, 4.0),
}

# --- Constants ---
max_red_hearts = 5
give_up_threshold = 8

# --- Simulation Function ---
def simulate_user(initial_pref, dynamic=False):
    sweetness = []
    red_hearts = max_red_hearts
    relapse_streak = 0
    current_pref = initial_pref
    decay = decay_rate
    gave_up = False

    for day in range(days):
        if dynamic and (relapse_streak >= 2 or red_hearts <= 1):
            decay = decay_rate * 2
        else:
            decay = decay_rate

        if np.random.rand() < relapse_chance:
            current_pref += relapse_impact
            red_hearts -= 1
            relapse_streak += 1
        else:
            relapse_streak = 0
            current_pref -= decay * (current_pref - final_sweetness)

        current_pref = max(0, min(current_pref, 10))

        if relapse_streak >= 3 or red_hearts <= 0 or (day > 10 and current_pref > give_up_threshold):
            gave_up = True
            sweetness.extend([current_pref] * (days - len(sweetness)))
            break

        sweetness.append(current_pref)

    if not gave_up:
        sweetness += [current_pref] * (days - len(sweetness))

    return sweetness

# --- Run Simulation ---
st.title("Interactive Taste Preference Simulation")
st.write("Adjust parameters from the sidebar to test different interventions")

fig, ax = plt.subplots(figsize=(12, 6))
results = {}

for profile, start in user_profiles.items():
    static_curve = simulate_user(start, dynamic=False)
    dynamic_curve = simulate_user(start, dynamic=True)
    ax.plot(static_curve, linestyle='--', label=f"{profile} - Static")
    ax.plot(dynamic_curve, linestyle='-', label=f"{profile} - Dynamic")
    results[f"{profile}_Static"] = static_curve
    results[f"{profile}_Dynamic"] = dynamic_curve

ax.axhline(y=final_sweetness, color='gray', linestyle='--', label='Target Sweetness')
ax.set_title("Sweetness Preference Over Time")
ax.set_xlabel("Days")
ax.set_ylabel("Sweetness Preference (0-10)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# --- Export Data ---
st.write("## Export Simulation Results")
df = pd.DataFrame(results)
df["Day"] = np.arange(1, days + 1)
st.dataframe(df.set_index("Day"))
st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name="taste_simulation.csv", mime="text/csv")
