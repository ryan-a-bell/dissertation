"""Statistical tests for format comparison.

Note: Only methods used in the dissertation pipeline are exported here.
Additional methods (paired_t_test, sign_test, hedges_g, glass_delta,
common_language_effect_size, correlation_matrix, bootstrap_ci, etc.)
remain available via direct import from their respective modules for
advanced use or future versions.
"""

from metaeval.compare.stats.correlation import (
    pearson_correlation,
    spearman_correlation,
)
from metaeval.compare.stats.paired import (
    wilcoxon_signed_rank,
)
from metaeval.compare.stats.effects import (
    cohens_d,
)
from metaeval.compare.stats.bootstrap import (
    bootstrap_difference,
    bootstrap_correlation,
)

__all__ = [
    # Correlation (aligned with dissertation methodology)
    "pearson_correlation",
    "spearman_correlation",
    # Paired tests
    "wilcoxon_signed_rank",
    # Effect sizes
    "cohens_d",
    # Bootstrap
    "bootstrap_difference",
    "bootstrap_correlation",
]
