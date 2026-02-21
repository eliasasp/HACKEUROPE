import numpy as np
import matplotlib.pyplot as plt

from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster


# --------------------------------------------------
# 1. GENERATE SYNTHETIC DATA
# --------------------------------------------------

def generate_synthetic_attack_data(
    T=400,
    kappa=0.1,
    theta=np.log(5),
    sigma=0.25
):
    """
    Generate synthetic log-OU attack intensity
    with an escalation regime.
    """

    x = np.zeros(T)
    x[0] = theta

    for t in range(1, T):

        # Introduce attack surge between t=200 and t=300
        if 200 < t < 300:
            theta_shift = np.log(15)  # higher attack pressure
        else:
            theta_shift = theta

        x[t] = (
            x[t-1]
            + kappa * (theta_shift - x[t-1])
            + sigma * np.random.randn()
        )

    lambda_true = np.exp(x)
    observations = np.random.poisson(lambda_true)

    return x, lambda_true, observations


# --------------------------------------------------
# 2. VALIDATION PIPELINE
# --------------------------------------------------

def run_synthetic_validation():

    print("Running synthetic validation...")

    # Generate data
    x_true, lambda_true, ys = generate_synthetic_attack_data()

    # Run particle filter
    lambda_estimates, final_particles = cyber_particle_filter(
        ys,
        npart=500,
        kappa=0.1,
        dt=1.0
    )

    # Compute error
    mse = np.mean((lambda_estimates - lambda_true)**2)

    print(f"Mean Squared Error (Intensity): {mse:.4f}")

    # --------------------------------------------------
    # 3. Plot results
    # --------------------------------------------------

    plt.figure(figsize=(12,6))

    plt.plot(lambda_true, label="True Intensity", linewidth=2)
    plt.plot(lambda_estimates, label="Estimated Intensity", linewidth=2)
    plt.scatter(range(len(ys)), ys, s=10, alpha=0.3, label="Observed Attacks")

    plt.axvspan(200, 300, color='red', alpha=0.1, label="Attack Surge")

    plt.legend()
    plt.title("Synthetic Validation: True vs Estimated Attack Intensity")
    plt.xlabel("Time")
    plt.ylabel("Attack Intensity")
    plt.show()

    # --------------------------------------------------
    # 4. Forecast demonstration
    # --------------------------------------------------

    forecaster = ThreatForecaster(
        kappa=0.1,
        theta=np.log(5),
        sigma=0.25,
        dt=1.0
    )

    results = forecaster.simulate(
        log_particles=final_particles,
        steps=24,
        n_sim=2000
    )

    lambda_paths = results["lambda_paths"]

    forecast_mean = np.mean(lambda_paths[:, -1])
    print(f"Forecasted mean intensity (24h ahead): {forecast_mean:.2f}")


# --------------------------------------------------
# 5. Run directly
# --------------------------------------------------

if __name__ == "__main__":
    run_synthetic_validation()