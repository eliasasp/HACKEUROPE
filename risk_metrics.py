import numpy as np


def expected_attacks(attack_paths):
    return np.mean(attack_paths[:, -1])


def escalation_probability(lambda_paths, threshold):
    return np.mean(lambda_paths[:, -1] > threshold)


def percentile_attack_risk(attack_paths, percentile=0.95):
    return np.quantile(attack_paths[:, -1], percentile)


def cumulative_attacks(attack_paths):
    return np.mean(np.sum(attack_paths, axis=1))