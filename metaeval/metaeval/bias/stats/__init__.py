"""Statistical tests and effect sizes for position bias analysis.

Note: Only methods used in the dissertation pipeline are exported here.
Additional methods (kruskal_wallis_test, mcnemar_test, pairwise_mcnemar,
anova_test, epsilon_squared, etc.) remain available via direct import
from their respective modules for advanced use or future versions.
"""

from metaeval.bias.stats.tests import (
    chi_square_test,
    friedman_test,
)
from metaeval.bias.stats.effects import (
    cramers_v,
    kendalls_w,
    interpret_effect_size,
)

__all__ = [
    # Tests (aligned with dissertation methodology)
    "chi_square_test",
    "friedman_test",
    # Effect sizes
    "cramers_v",
    "kendalls_w",
    "interpret_effect_size",
]
