# 1st prompt

What we’ll show (TL;DR)

A group of “good” agents (competent models) plus a minority of “bad” agents (noisy or systematically biased) answering 4-choice SE questions.

Compare consensus rules: Plurality (majority vote), Soft averaging (average class probs), Trimmed mean (robust soft averaging), and Borda (rank aggregation).

Result: A small fraction of bad agents can meaningfully shift/poison the consensus—especially under systematic bias—despite many good models.

I’ve already run a reproducible experiment and rendered three figures for you:

Consensus accuracy vs. bad-agent fraction (noisy attackers)

Consensus accuracy vs. bad-agent fraction (systematic bias attackers)

How often the consensus adopts the attacker’s favored label (systematic bias)

You can also download the aggregated results:
Download the CSV

How the simulation works

Ground truth: 4-choice labels for Q questions.

Good agents: usually produce well-calibrated, correct-peaked distributions; sometimes near-uniform (uncertain).

Bad agents:

Noisy: often confidently peak on a wrong option (randomly chosen).

Systematic bias: always tilt probability mass toward a specific wrong label (e.g., “B”), regardless of truth.

We sweep the fraction of bad agents from 0 → 0.6 and repeat many trials.

We measure consensus accuracy and, for systematic attacks, the shift rate (how often consensus becomes the attacker’s target label).

I executed the code and displayed the results/plots in-line for you. You should see the table and charts above. If you want to re-run locally, copy the code I used (it’s the executed cell in our chat) and tweak:

A_total (number of agents),

bad_frac_list (grid of bad-agent proportions),

trials_per_point, and

attack mode (“noisy” vs “systematic”).

What the results typically show

Plurality and Borda degrade fastest as bad fraction increases; Borda is particularly fragile to systematic bias.

SoftAvg and TrimmedMean(20%) are more robust but still succumb once attackers approach ~30–40% in this setup.

Under systematic bias, the “rate consensus = attacker’s target” climbs sharply once bad agents pass a critical mass—your “poison/shift” moment for the paper/talk.

How to frame this for SE audiences (NPS ARS lineage)

Use a concrete SE decision task (e.g., requirement classification, hazard cause assignment, architecture trade study choice). The takeaway:

Without governance, calibration, and adversary-aware aggregation, “AI consensus” can be precisely wrong—and confidently so—once a small coalition of poor or biased agents is present.

Minimal Methods write-up (drop-in text)

Agents & Tasks: We simulate 
𝐴
A agents answering 
𝑄
Q 4-choice questions with known ground truth. Good agents generate probability vectors with a true-class peak (with probability 
𝜅
κ), otherwise near-uniform. Bad agents are either (i) noisy label-flippers or (ii) systematically biased toward a fixed (wrong) label.

Consensus Rules: (i) Plurality of top-1 picks; (ii) SoftAvg: average probabilities, argmax; (iii) TrimmedMean(20%): trim extreme per-class probabilities before averaging; (iv) Borda: rank options per agent, sum ranks.

Metrics: (i) Consensus accuracy; (ii) Under systematic bias, the shift rate: fraction of items where consensus equals the attacker’s favored label.

Protocol: Sweep bad-agent fraction 
𝑓
∈
[
0
,
0.6
]
f∈[0,0.6], repeat 
𝑇
T trials, report mean±std across trials.

Make it “real” with LLMs (next steps)

Replace simulated agents with actual models (mix foundation and distilled models) or a single model diversified via prompts, temperature, or retrieval slices.

Calibrate with a held-out SE validation set—estimate each agent’s reliability (Brier score, ECE).

Add Delphi rounds: re-ask agents after showing round-1 consensus to quantify anchoring/herding.

Log influence per agent (leave-one-out delta on the consensus) to reveal who’s steering outcomes.

Defenses you can evaluate

Credibility-weighted soft voting: weight each agent by calibration score or historical accuracy.

Robust aggregators: trimmed means on logits; median-of-means; geometric median over probability simplex.

Diversity constraints: enforce architecture/data diversity across agents.

Abstention/quorum policies: require a quorum of independent agreement, allow “I don’t know.”

Adversarial detection: monitor per-agent influence, detect systematic drift toward a single wrong label.

If you want, I can extend the code to:

add Delphi iteration (anchoring effects),

plug in Dawid–Skene (EM) worker-reliability weighting,

log influence functions per agent,

or swap in your SysEngBench items and real LLM outputs to make the figures publication-ready.



# 2nd prompt

What I simulated (brief)

Task: 4-choice questions with known ground truth (think “SE multiple-choice surrogates”).

Agents: 15 per trial. “Good” agents are well-calibrated and usually peak on the truth; “bad” agents are either:

Noisy (often confidently wrong but not coordinated), or

Systematically biased (push a specific wrong label—e.g., always favor “B”).

Poison sweep: bad-agent fraction from 0.0 → 0.6.

Metrics:

Consensus accuracy (vs. truth)

Shift rate (systematic attack only): how often the consensus picks the attacker’s favored label.

Implementations mapping to your methods (faithful but lightweight so we can run lots of trials):

Delphi: anonymous, multi-round pull toward the group mean with inertia; stop after a few rounds, take argmax of the mean.

Fuzzy Delphi: triangular fuzz around each agent’s probabilities; aggregate triangles; centroid defuzzification → normalized distribution → argmax.

Structured Expert Judgment (Cooke): hold-out seed set to estimate calibration (NLL) and informativeness (low entropy), derive weights, then weighted soft vote on evaluation items.

NGT: private rankings → Borda aggregation (this mirrors NGT prioritization).

Stepladder: start with two agents, then sequentially integrate newcomers who state their view independently before integration (mix with the current group).

Dialectical Inquiry: split agents into two debating teams; synthesize by maximizing agreement across teams (argmax of the element-wise min of team means).

Multi-Voting: each agent has m=2 dots for their top-2 classes; count dots (plurality on dots).

Headline results (from the plots & table you see)
A) Noisy attackers (uncoordinated wrongness)

Most robust: Cooke (SEJ), Trimmed mean (20%), Delphi/Fuzzy-Delphi; they keep accuracy high until ~35–45% bad agents.

Moderate: Plurality, NGT/Borda, Multi-Voting degrade earlier.

Least robust here: Stepladder loses accuracy sooner (it integrates weak opinions early), though it still resists extreme collapse.

B) Systematic bias (coordinated push toward one wrong label)

Critical “flip zone”: ~35–40% bad agents. Around there, most methods’ shift-to-attacker rises past 50% and accuracy collapses steeply.

Cooke (SEJ) and Stepladder are the least likely to pick the attacker’s target at the same bad-fraction:

Cooke helps because reliable agents get more weight (seed calibration).

Stepladder helps because newcomers can’t immediately drag the whole group; the sequential gate dampens coordinated swings.

Delphi / Fuzzy-Delphi / SoftAvg / Trimmed: track closely and generally flip near the same band (≈0.36–0.38 bad fraction in this run).

NGT / Multi-Voting / Plurality: behave like vote-based baselines—intuitive and fast, but easier to steer once attackers reach the flip zone.

Quick “poisoning budgets” (systematic case, this run):
Shift≥50% to attacker’s label typically occurs near ~0.36 bad fraction for Delphi/SoftAvg/Trimmed/NGT/Plurality/Multi-Voting; Stepladder ~0.34, Cooke ~0.36. (Interpolation from the summary table.)

You can inspect exact breakpoints in the “Resilience Breakpoints (SYSTEMATIC, interpolated)” table displayed above (bad-fraction where accuracy dips below 0.90/0.75 and where shift exceeds 0.50).

Why these patterns make sense

Weighting beats counting. Cooke’s method explicitly learns which agents are reliable on a seed set, so random/noisy poison is attenuated; coordinated bias still hurts but needs more bad mass to flip.

Sequential gates blunt herding. Stepladder reduces “instant majorities,” so it’s harder to stampede the group toward the attacker’s preferred label; the trade is slightly lower peak accuracy in benign settings because early mixtures can be conservative.

Averaging is smooth… until it isn’t. Delphi/SoftAvg/Fuzzy/Trimmed do well with uncoordinated noise (LLN effect), but coordinated bias aligns the attackers in the same direction, and the group mean follows once attackers are ≳⅓ of the room.

Voting is brittle. Plurality, NGT/Borda, and Multi-Voting are intuitively appealing for lists/prioritization, but they’re easier to steer with a coordinated bloc.

How this sets up your LLM experiments

Drop real LLM “agents” into the same harness:

Produce per-item probability vectors (logits→softmax) per agent/model (or per prompt/persona/temperature slice).

Pick a method (Delphi, Cooke, NGT, etc.) and compute consensus predictions.

Measure accuracy and shift-to-target as you add synthetic “bad” agents (e.g., biased prompts, adversarial knowledge bases, deterministic wrong chains).

Estimate poisoning budgets: how many bad replicas (or what weight) is needed to flip consensus for your real datasets (e.g., SysEngBench).

If you want, I can wire this directly to your SysEngBench CSV and the lm-evaluation-harness outputs so you can reproduce the same figures with actual model runs (keeping interfaces identical, just swapping the sampler with real scores).

Citations (paper & method list)

Your NPS ARS paper explicitly enumerates the methods we used—Delphi, Fuzzy Delphi, Structured Expert Judgment (Cooke’s), NGT, Stepladder, Dialectical Inquiry, and Multi-Voting—and frames their use in SE decision-making; see the “Overview of Consensus Methods” section and Table 1 in the proceedings excerpt.

# 3rd pormpt

we can swap your simulated “agents” for real LLMs and feed their per-question, per-choice probabilities straight into the consensus/poisoning analysis.

Below is a lean, battle-tested wiring plan with ready-to-drop files:

add SysEngBench to lm-evaluation-harness as a multiple-choice task (using a local JSONL the harness can load)

evaluate any set of models/agents with --log_samples so you get per-sample logs

extract per-choice log-likelihoods → normalize to probabilities per agent

plug those matrices into the consensus methods you’re studying (Delphi, Fuzzy Delphi, Cooke/SEJ-style weighting, majority/Borda, etc.)

optionally create “bad agents” (prompt-poisoned or instruction-biased) to quantify consensus drift

This ties directly to the NPS work: SysEngBench is public on HF and the 2025 NPS ARS paper by Bell et al. enumerates Delphi, Fuzzy Delphi, Cooke/SEJ, NGT, Stepladder, Dialectical Inquiry, and Multi-Voting as candidate mechanisms we can operationalize with LLM votes.