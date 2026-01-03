import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
st.write("VERSION CHECK: Trial benchmarking active")
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


def patient_weight_loss_curve(weekly_exposure, weeks, diabetes):
    """
    Patient-specific response using total weekly drug exposure.
    Supports microdosing.
    """
    max_weekly_dose = 15.0
    dose_effect = weekly_exposure / max_weekly_dose

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
st.subheader("Dosing strategy")

dosing_strategy = st.radio(
    "Select dosing approach",
    ["Microdosing (adaptive)", "Lilly reference dosing"]
)

if dosing_strategy == "Microdosing (adaptive)":
    st.subheader("Microdosing parameters")

    dose_per_injection = st.selectbox(
        "Dose per injection (mg)",
        [1.0, 1.25, 1.5, 2.0]
    )

    injections_per_week = st.selectbox(
        "Injections per week",
        [1, 2, 3, 4],
        index=3
    )

    weekly_exposure = dose_per_injection * injections_per_week

    st.caption(
        f"Total weekly exposure: {weekly_exposure} mg "
        f"({dose_per_injection} mg × {injections_per_week}/week)"
    )

else:
    st.subheader("Lilly reference dosing")

    weekly_exposure = st.selectbox(
        "Weekly dose (mg)",
        [2.5, 5.0, 10.0, 15.0]
    )

    st.caption("Standard once-weekly dosing based on Lilly trials")
current_week = st.slider(
    "Current week on therapy",
    min_value=1,
    max_value=72,
    value=12
)

st.subheader("Comorbidities")
diabetes = st.checkbox("Type 2 Diabetes")
pcos = st.checkbox("PCOS")
thyroid = st.checkbox("Hypothyroidism")

weeks = np.arange(0, 73)


trial_curve = trial_reference_weight_loss(weeks)
patient_curve = patient_weight_loss_curve(
    weekly_exposure, weeks, diabetes
)

trial_weights = baseline_weight * (1 - trial_curve)
patient_weights = baseline_weight * (1 - patient_curve)

delta_vs_trial = (
    patient_weights[current_week - 1]
    - trial_weights[current_week - 1]
)


fig, ax = plt.subplots()

# Observed patient trajectory (up to current week)
ax.plot(
    weeks[:current_week],
    patient_weights[:current_week],
    label="Observed patient trajectory",
    linewidth=2
)

# Projected patient trajectory (after current week)
ax.plot(
    weeks[current_week-1:],
    patient_weights[current_week-1:],
    linestyle=":",
    label="Projected patient trajectory"
)

# Lilly trial reference (benchmark)
ax.plot(
    weeks,
    trial_weights,
    linestyle="--",
    label="Lilly trial reference"
)

# Mark current week
ax.axvline(
    current_week,
    linestyle=":",
    color="grey",
    alpha=0.6,
    label="Current week"
)

ax.set_xlabel("Weeks on therapy")
ax.set_ylabel("Weight (kg)")
ax.set_title("Observed vs Projected Weight Trajectory")
ax.legend()

st.pyplot(fig)
st.subheader("Trial-relative performance")

if delta_vs_trial < -1:
    st.success("Patient is outperforming trial expectations at this dose")
elif abs(delta_vs_trial) <= 1:
    st.info("Patient is tracking close to trial expectations")
else:
    st.warning("Patient is lagging behind trial expectations")


st.subheader(f"Estimated outcomes at week {current_week}")

st.write(
    f"Estimated weight at week {current_week}: "
    f"{round(patient_weights[current_week - 1],1)} kg"
)

st.caption(
    f"Projected final weight at week 72: "
    f"{round(patient_weights[-1],1)} kg"
)


st.warning(
    "This tool provides trial-anchored simulations for clinical visualization only. "
    "It does not replace prescribing information or clinical judgment."
)
