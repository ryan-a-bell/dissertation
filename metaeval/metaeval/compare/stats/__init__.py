"""Statistical tests for format comparison."""

from metaeval.compare.stats.correlation import (
    pearson_correlation,
    spearman_correlation,
    correlation_matrix,
)
from metaeval.compare.stats.paired import (
    wilcoxon_signed_rank,
    paired_t_test,
    sign_test,
)
from metaeval.compare.stats.effects import (
    cohens_d,
    hedges_g,
    glass_delta,
    common_language_effect_size,
)
from metaeval.compare.stats.bootstrap import (
    bootstrap_ci,
    bootstrap_difference,
    bootstrap_correlation,
)

__all__ = [
    # Correlation
    "pearson_correlation",
    "spearman_correlation",
    "correlation_matrix",
    # Paired tests
    "wilcoxon_signed_rank",
    "paired_t_test",
    "sign_test",
    # Effect sizes
    "cohens_d",
    "hedges_g",
    "glass_delta",
    "common_language_effect_size",
    # Bootstrap
    "bootstrap_ci",
    "bootstrap_difference",
    "bootstrap_correlation",
]
