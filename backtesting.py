import pandas as pd
import numpy as np

from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster


def run_backtest(ys, horizon=1, start=100):

    errors = []
    coverage_count = 0
    total_tests = 0

    for t in range(start, len(ys) - horizon):

        # 1️ Kör filter på historisk data
        lambda_estimates, final_particles = cyber_particle_filter(
            ys[:t],
            npart=500,
            kappa=0.5,     
            dt=1.0
        )

        # 2️ Forecast med samma struktur som filtret använder
        theta_log = np.log(np.mean(ys[:t]) + 1e-6)
        sigma = max(np.std(np.log(ys[:t] + 1e-5)), 0.1)

        forecaster = ThreatForecaster(
            kappa=0.5,
            theta=theta_log,
            sigma=sigma,
            dt=1.0
        )

        results = forecaster.simulate(
            log_particles=final_particles,
            steps=horizon,
            n_sim=1000
        )

        attack_paths = results["attack_paths"]

        # 3️ Jämför forecast med verkligt värde
        forecast_mean = np.mean(attack_paths[:, -1])
        actual_value = ys[t + horizon - 1]

        errors.append((forecast_mean - actual_value) ** 2)

        # 4️ Coverage-test
        lower = np.percentile(attack_paths[:, -1], 2.5)
        upper = np.percentile(attack_paths[:, -1], 97.5)

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

    df = pd.read_csv("testdata.csv")
    ys = df["failed_login"].values

    run_backtest(ys, horizon=1, start=100)