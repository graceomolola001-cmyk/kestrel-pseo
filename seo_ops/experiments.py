"""Fixed-horizon binary conversion experiment calculator. Educational, not a test runner."""
from __future__ import annotations

from math import ceil, erf, sqrt
from statistics import NormalDist


def plan_sample_size(baseline_rate: float, relative_mde: float, power=0.80, alpha=0.05) -> int:
    """Normal-approximation sample size per arm for a two-sided test."""
    if not 0 < baseline_rate < 1 or relative_mde <= 0 or not 0 < power < 1 or not 0 < alpha < 1:
        raise ValueError('Invalid probability, relative MDE, alpha or power')
    p1 = baseline_rate; p2 = baseline_rate * (1 + relative_mde)
    if p2 >= 1:
        raise ValueError('MDE increases conversion probability beyond 100%')
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    pooled = (p1 + p2) / 2
    n = ((z_alpha * sqrt(2 * pooled * (1 - pooled)) + z_power * sqrt(p1 * (1-p1) + p2 * (1-p2))) ** 2) / ((p2-p1) ** 2)
    return ceil(n)


def evaluate(control_visitors: int, control_conversions: int, variant_visitors: int,
             variant_conversions: int, preregistered_min_per_arm: int, alpha=0.05) -> dict:
    if any(not isinstance(n, int) for n in (control_visitors,control_conversions,variant_visitors,variant_conversions,preregistered_min_per_arm)):
        raise ValueError('Counts and preregistered sample size must be integers')
    if min(control_visitors, variant_visitors, preregistered_min_per_arm) <= 0 or min(control_conversions, variant_conversions) < 0:
        raise ValueError('Visitor counts and planned sample must be positive; conversion counts non-negative')
    if control_conversions > control_visitors or variant_conversions > variant_visitors or not 0 < alpha < 1:
        raise ValueError('Conversions cannot exceed visitors; alpha must be between 0 and 1')
    p1 = control_conversions/control_visitors; p2 = variant_conversions/variant_visitors
    pooled = (control_conversions+variant_conversions)/(control_visitors+variant_visitors)
    se = sqrt(pooled*(1-pooled)*(1/control_visitors+1/variant_visitors))
    z = (p2-p1)/se if se else 0.0
    p_value = 2*(1-NormalDist().cdf(abs(z))) if se else 1.0
    complete = min(control_visitors, variant_visitors) >= preregistered_min_per_arm
    return {'control_rate': round(p1,5), 'variant_rate': round(p2,5),
            'absolute_lift': round(p2-p1,5), 'relative_lift': round((p2/p1-1),5) if p1 else None,
            'p_value': round(p_value,6), 'sample_requirement_met': complete,
            'conclusion': ('inconclusive: sample size not reached' if not complete else
                           'statistically significant difference' if p_value < alpha else
                           'inconclusive: no significant difference detected'),
            'note': 'Fixed-horizon approximation; assumes independent visitors and no repeated peeking.'}
