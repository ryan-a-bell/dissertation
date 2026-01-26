"""Statistical tests and effect sizes for position bias analysis."""

from metaeval.bias.stats.tests import (
    chi_square_test,
    kruskal_wallis_test,
    friedman_test,
    mcnemar_test,
    pairwise_mcnemar,
    anova_test,
)
from metaeval.bias.stats.effects import (
    cramers_v,
    kendalls_w,
    epsilon_squared,
    interpret_effect_size,
    compute_all_effect_sizes,
)

__all__ = [
    # Tests
    "chi_square_test",
    "kruskal_wallis_test",
    "friedman_test",
    "mcnemar_test",
    "pairwise_mcnemar",
    "anova_test",
    # Effect sizes
    "cramers_v",
    "kendalls_w",
    "epsilon_squared",
    "interpret_effect_size",
    "compute_all_effect_sizes",
]
