def anti_thetic_sampling(f, n_samples):
    X = np.random.uniform(0, 1, n_samples)
    X_ha t = 1-X
    temp_list = []
    for i, (lam, k) in enumerate(params.T):
        v = weibull_inverse(k, lam, X)
        v_hat = weibull_inverse(k, lam, X_hat)

        y = f(v)
        y_hat = f(v_hat)
        pair_values = 0.5 * (y + y_hat)
        mu = np.mean(pair_values)
        sem = np.std(pair_values, ddof=1) / np.sqrt(n_samples)
        ci_lower, ci_upper = stats.norm.interval(0.95, loc=mu, scale=sem)
        temp_list.append([ci_lower, ci_upper])
        print(f"Mean power (Antithetic): {mu:.2f}, 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
    return temp_list

confidence_levels_methods.append(anti_thetic_sampling(power_curve, n_samples))