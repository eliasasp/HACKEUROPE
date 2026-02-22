import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster


def pro_backtest(ys, train_size=200, horizon=1):

    print("=== BACKTEST START ===")

    # ----------------------------
    # 1️ TRAIN / PARAMETER FIT
    # ----------------------------

    train_data = ys[:train_size]

    kappa = 0.05   # tune this later if needed
    theta_log = np.log(np.mean(train_data) + 1e-6)
    sigma = max(np.std(np.log(train_data + 1e-5)), 0.1)

    print("Calibrated parameters:")
    print("kappa:", kappa)
    print("theta:", theta_log)
    print("sigma:", sigma)

    # ----------------------------
    # 2️ TEST LOOP
    # ----------------------------

    forecast_means = []
    lowers = []
    uppers = []
    actuals = []
    naive_forecasts = []

    for t in range(train_size, train_size + 300):

        # Filtering using past data only
        _, final_particles = cyber_particle_filter(
            ys[:t],
            npart=200,
            kappa=kappa,
            dt=1.0 
        )

        # Monte Carlo forecast
        forecaster = ThreatForecaster(
            kappa=kappa,
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

        forecast_mean = np.mean(attack_paths[:, -1])
        lower = np.percentile(attack_paths[:, -1], 2.5)
        upper = np.percentile(attack_paths[:, -1], 97.5)

        actual_value = ys[t + horizon - 1]
        naive_forecast = ys[t - 1]   # baseline: last observed value

        forecast_means.append(forecast_mean)
        lowers.append(lower)
        uppers.append(upper)
        actuals.append(actual_value)
        naive_forecasts.append(naive_forecast)

    # ----------------------------
    # 3️ METRICS
    # ----------------------------

    forecast_means = np.array(forecast_means)
    actuals = np.array(actuals)
    lowers = np.array(lowers)
    uppers = np.array(uppers)
    naive_forecasts = np.array(naive_forecasts)

    errors = forecast_means - actuals
    naive_errors = naive_forecasts - actuals

    mse = np.mean(errors**2)
    mae = np.mean(np.abs(errors))
    bias = np.mean(errors)
    coverage = np.mean((actuals >= lowers) & (actuals <= uppers))

    naive_mse = np.mean(naive_errors**2)

    print("\n=== RESULTS ===")
    print("Model MSE:", mse)
    print("Model MAE:", mae)
    print("Model Bias:", bias)
    print("Model Coverage (95%):", coverage)
    print("Naive MSE:", naive_mse)

    # ----------------------------
    # 4️ PLOT
    # ----------------------------

    plt.figure(figsize=(12,6))
    plt.plot(actuals, label="Actual", linewidth=2)
    plt.plot(forecast_means, label="Model Forecast")
    plt.plot(naive_forecasts, label="Naive Forecast", linestyle="--")
    plt.fill_between(range(len(actuals)), lowers, uppers,
                     alpha=0.3, label="95% Interval")

    plt.legend()
    plt.title("Backtest: Model vs Naive")
    plt.xlabel("Time (Test Period)")
    plt.ylabel("Hack Attempts")
    plt.show()

    print("=== BACKTEST COMPLETE ===")


if __name__ == "__main__":
    df = pd.read_csv("formatted_hourly.csv")
    ys = df["attack_count"].values
    pro_backtest(ys, train_size=200, horizon=1)