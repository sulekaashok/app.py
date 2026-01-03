import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
# ============================
# Trial reference curve (SURMOUNT-style)
# ============================

def trial_reference_weight_loss(weeks):
    """
    Normalized trial-average % weight loss curve.
    Reference only, not a target.
    """
    max_loss = 0.21  # conservative SURMOUNT-1 mean
    return max_loss / (1 + np.exp(-0.1 * (weeks - 28)))

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
    def patient_weight_loss_curve(dose, weeks, diabetes):
    """
    Patient-specific response using dose exposure.
    Enables microdosing and trial comparison.
    """
    dose_effect = dose / 15  # normalize vs max dose
    base_response = 0.21 * dose_effect

    if diabetes:
        base_response *= 0.65

    return base_response / (1 + np.exp(-0.1 * (weeks - 30)))


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

trial_curve = trial_reference_weight_loss(weeks)
patient_curve = patient_weight_loss_curve(dose, weeks, diabetes)

trial_weights = baseline_weight * (1 - trial_curve)
patient_weights = baseline_weight * (1 - patient_curve)

delta_vs_trial = patient_weights[-1] - trial_weights[-1]


fig, ax = plt.subplots()

ax.plot(weeks, patient_weights, label="Patient trajectory", linewidth=2)
ax.plot(weeks, trial_weights, linestyle="--", label="Lilly trial reference")

ax.set_xlabel("Weeks on therapy")
ax.set_ylabel("Weight (kg)")
ax.set_title("Patient vs Trial Reference Trajectory")
ax.legend()

st.pyplot(fig)
st.subheader("Trial-relative performance")

if delta_vs_trial < -1:
    st.success("Patient is outperforming trial expectations at this dose")
elif abs(delta_vs_trial) <= 1:
    st.info("Patient is tracking close to trial expectations")
else:
    st.warning("Patient is lagging behind trial expectations")


st.subheader("Estimated outcomes at 72 weeks")
st.write(f"Mean expected weight loss: {round(adjusted_loss*100,1)}%")
st.write(f"Estimated final weight: {round(weights[-1],1)} kg")

st.warning(
    "This tool provides trial-anchored simulations for clinical visualization only. "
    "It does not replace prescribing information or clinical judgment."
)
