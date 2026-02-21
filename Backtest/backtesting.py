import numpy as np
from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster


def run_backtest(ys, horizon=24, start=200):

    errors = []
    coverage_count = 0
    total_tests = 0

    for t in range(start, len(ys) - horizon):

        # 1. Fit filter on past data only
        lambda_estimates, final_particles = cyber_particle_filter(
            ys[:t],
            npart=500,
            kappa=0.1,
            dt=1.0
        )

        # 2. Forecast future
        forecaster = ThreatForecaster(
            kappa=0.1,
            theta=np.log(np.mean(ys[:t]) + 1e-6),
            sigma=0.25,
            dt=1.0
        )

        results = forecaster.simulate(
            log_particles=final_particles,
            steps=horizon,
            n_sim=1000
        )

        attack_paths = results["attack_paths"]

        # 3. Compare mean forecast to actual future value
        forecast_mean = np.mean(attack_paths[:, -1])
        actual_value = ys[t + horizon - 1]

        errors.append((forecast_mean - actual_value) ** 2)

        # 4. Check probabilistic coverage (95%)
        lower = np.percentile(attack_paths[:, -1], 5)
        upper = np.percentile(attack_paths[:, -1], 95)

        if lower <= actual_value <= upper:
            coverage_count += 1

        total_tests += 1

    mse = np.mean(errors)
    coverage_rate = coverage_count / total_tests

    print(f"Backtest MSE: {mse:.3f}")
    print(f"95% Coverage: {coverage_rate:.2%}")

    return mse, coverage_rate

if __name__ == "__main__":

    import pandas as pd

    # Ladda data
    df = pd.read_csv("synthetic_ai_attack_timeseries.csv")
    ys = df["attack_count"].values

    run_backtest(ys, horizon=24, start=200)