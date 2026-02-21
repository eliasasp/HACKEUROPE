import pandas as pd
import numpy as np

from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster


def run_backtest(ys, horizon=24, start=100):

    errors = []
    coverage_count = 0
    total_tests = 0

    for t in range(start, len(ys) - horizon):

        # 1️ Fit filter on past data only
        lambda_estimates, final_particles = cyber_particle_filter(
            ys[:t],
            npart=500,
            kappa=0.2,      
            dt=1.0
        )

        # 2️ Forecast future
        forecaster = ThreatForecaster(
        kappa=0.2,
        theta=np.log(10),  
        sigma=0.3,
        dt=1.0
    )

        results = forecaster.simulate(
            log_particles=final_particles,
            steps=horizon,
            n_sim=1000
        )

        attack_paths = results["attack_paths"]

        # 3️ Compare forecast to actual future
        forecast_mean = np.mean(attack_paths[:, -1])
        actual_value = ys[t + horizon - 1]

        errors.append((forecast_mean - actual_value) ** 2)

        # 4️ Coverage test
        lower = np.percentile(attack_paths[:, -1], 5)
        upper = np.percentile(attack_paths[:, -1], 95)

        if lower <= actual_value <= upper:
            coverage_count += 1

        total_tests += 1

    mse = np.mean(errors)
    coverage_rate = coverage_count / total_tests

    print("\n--- BACKTEST RESULT ---")
    print(f"MSE: {mse:.3f}")
    print(f"95% Coverage: {coverage_rate:.2%}")

    return mse, coverage_rate


if __name__ == "__main__":

    df = pd.read_csv("test_data.csv")

    ys = df["failed_login"].values

    run_backtest(ys, horizon=24, start=100)
