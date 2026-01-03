import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ============================
# Trial-anchored prediction logic
# ============================

def base_trial_weight_loss(dose):
    return {
        5: 0.15,
        10: 0.19,
        15: 0.22
    }[dose]

def apply_comorbidity_adjustments(base_loss, diabetes, pcos, thyroid):
    if diabetes:
        base_loss *= 0.65
    if pcos:
        base_loss *= 1.05
    if thyroid:
        base_loss *= 0.90
    return base_loss

def trial_time_curve(total_loss, weeks):
    return total_loss / (1 + np.exp(-0.1 * (weeks - 30)))

# ============================
# Streamlit UI
# ============================

st.set_page_config(page_title="GLP-1 Clinical Simulator")

st.title("Tirzepatide (Mounjaro) – Clinical Outcome Simulator")
st.caption("Conservative trial-average projections for clinician use")

age = st.number_input("Age", 18, 80, 40)

baseline_weight = st.number_input(
    "Baseline weight (kg)", 40.0, 250.0, 100.0
)

dose = st.selectbox("Weekly dose (mg)", [5, 10, 15])

st.subheader("Comorbidities")
diabetes = st.checkbox("Type 2 Diabetes")
pcos = st.checkbox("PCOS")
thyroid = st.checkbox("Hypothyroidism")

weeks = np.arange(0, 73)

base_loss = base_trial_weight_loss(dose)
adjusted_loss = apply_comorbidity_adjustments(
    base_loss, diabetes, pcos, thyroid
)

curve = trial_time_curve(adjusted_loss, weeks)
weights = baseline_weight * (1 - curve)

fig, ax = plt.subplots()
ax.plot(weeks, weights)
ax.set_xlabel("Weeks on therapy")
ax.set_ylabel("Weight (kg)")
ax.set_title("Expected Weight Trajectory")

st.pyplot(fig)

st.subheader("Estimated outcomes at 72 weeks")
st.write(f"Mean expected weight loss: {round(adjusted_loss*100,1)}%")
st.write(f"Estimated final weight: {round(weights[-1],1)} kg")

st.warning(
    "This tool provides trial-anchored simulations for clinical visualization only. "
    "It does not replace prescribing information or clinical judgment."
)
