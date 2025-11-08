# Architectural Diagrams for Dissertation Methods Section

This document provides detailed architectural diagrams for each phase of the research pipeline. These diagrams are suitable for inclusion in a dissertation methods section.

---

## Phase 1: Data Preparation

### 1.1 SysEngBench HuggingFace Download (`1.1_sysengbench_hf_download.ipynb`)

**Purpose**: Download the SysEngBench dataset from HuggingFace and store locally.

```mermaid
flowchart TD
    Start([Start]) --> LoadEnv[Load Environment Variables]
    LoadEnv --> GetToken[Retrieve HF_TOKEN]
    GetToken --> LoadDataset[Load Dataset from HuggingFace<br/>rabell/SysEngBench]
    LoadDataset --> ExtractTest[Extract Test Split<br/>1,144 MCQs]
    ExtractTest --> ConvertDF[Convert to Pandas DataFrame]
    ConvertDF --> Preview[Preview Data<br/>Question, Choices A-D, Answer]
    Preview --> SaveCSV[Save to Local CSV<br/>sysengbench.csv]
    SaveCSV --> End([End])

    style LoadDataset fill:#e1f5ff
    style SaveCSV fill:#c8e6c9
```

**Key Operations**:
- Environment: HuggingFace token authentication
- Data Source: `rabell/SysEngBench` repository
- Output: `sysengbench.csv` (1,144 rows × 11 columns)
- Schema: Question ID, Tags, INCOSE Category, Question, ChoiceA-D, Answer, Label, Justification

---

### 1.2 Benchmark Summary Statistics (`1.2_benchmark-summary.ipynb`)

**Purpose**: Analyze and visualize the distribution of questions across INCOSE Handbook categories.

```mermaid
flowchart TD
    Start([Start]) --> Load[Load sysengbench.csv or<br/>HuggingFace Dataset]
    Load --> Explode[Explode INCOSE Categories<br/>Split on newline]
    Explode --> ParseCat[Parse Category Structure<br/>Category / Sub-Category]
    ParseCat --> Stats[Calculate Statistics<br/>- Total Questions<br/>- Questions per Category<br/>- Questions per Sub-Category]
    Stats --> Viz1[Create Visualizations]

    Viz1 --> Pie1[Pie Chart: Sub-Categories]
    Viz1 --> Pie2[Pie Chart: Categories]
    Viz1 --> Bar1[Bar Chart: Sub-Categories<br/>Horizontal, Sorted]
    Viz1 --> Bar2[Bar Chart: Grouped by Category<br/>Color-coded]
    Viz1 --> Stack[Stacked Bar Chart<br/>Categories + Sub-Categories]

    Pie1 --> Output[Statistical Output<br/>& Visualizations]
    Pie2 --> Output
    Bar1 --> Output
    Bar2 --> Output
    Stack --> Output
    Output --> End([End])

    style Explode fill:#fff3e0
    style Stats fill:#e1f5ff
    style Output fill:#c8e6c9
```

**Statistical Outputs**:
- Total Unique MCQs: 1,144
- INCOSE Categories: 6 major categories
- INCOSE Sub-Categories: 20 sub-categories
- Distribution: Cross-Cutting Systems Engineering Methods (276), Specialty Engineering Activities (419), etc.

**Visualizations Generated**:
1. Pie chart showing percentage distribution across sub-categories
2. Pie chart with category-level aggregation
3. Horizontal bar chart ranked by question count
4. Grouped bar chart with category color coding
5. Stacked bar chart showing hierarchy

---

## Phase 2: MCQ to OSQ Conversion

### 2.1 Converting MCQ to OSQ (`2.1_Converting_MCQ_to_OSQ.ipynb`)

**Purpose**: Use an LLM to evaluate MCQ suitability and convert suitable questions to Open-ended Short-answer Questions (OSQ).

```mermaid
flowchart TD
    Start([Start]) --> Config[Configuration<br/>- Model: GPT-5 via OpenRouter<br/>- Temperature: 0.0<br/>- Threshold: 7/10]
    Config --> LoadCSV[Load sysengbench.csv<br/>1,144 MCQs]

    LoadCSV --> Classify{Classification Phase}

    Classify --> ForEach1[For Each MCQ]
    ForEach1 --> BuildPrompt1[Build Classifier Prompt<br/>5 Dimensions Assessment]
    BuildPrompt1 --> CallLLM1[LLM API Call<br/>JSON Response]
    CallLLM1 --> Parse1[Parse JSON<br/>- Suitability Score 1-10<br/>- Justification]
    Parse1 --> Log1[Log Raw Response]
    Log1 --> CheckThresh{Score ≥ 7?}

    CheckThresh -->|Yes| MarkSuitable[Mark osq_suitable = Yes]
    CheckThresh -->|No| MarkUnsuitable[Mark osq_suitable = No]

    MarkSuitable --> Next1{More MCQs?}
    MarkUnsuitable --> Next1
    Next1 -->|Yes| ForEach1
    Next1 -->|No| ClassifyDone[Classification Complete<br/>845/1144 Suitable 74%]

    ClassifyDone --> Convert{Conversion Phase}

    Convert --> ForEach2[For Each Suitable MCQ]
    ForEach2 --> BuildPrompt2[Build Converter Prompt<br/>Preserve Intent & Difficulty]
    BuildPrompt2 --> CallLLM2[LLM API Call<br/>JSON Response]
    CallLLM2 --> Parse2[Parse JSON<br/>- OSQ Prompt<br/>- Expected Answer<br/>- Rubric Full/Partial/No Credit<br/>- Bloom's Level + Justification]
    Parse2 --> Log2[Log Raw Response]
    Log2 --> Next2{More MCQs?}

    Next2 -->|Yes| ForEach2
    Next2 -->|No| SaveAll[Save Complete Dataset]

    SaveAll --> CSV[sysengbench_osq.csv<br/>All 1,144 rows with OSQ columns]
    SaveAll --> JSONL[sysengbench_osq.jsonl<br/>All 1,144 rows]
    CSV --> Filter[Filter Suitable Only]
    Filter --> CSVFiltered[sysengbench_osq_filtered.csv<br/>845 rows]
    CSVFiltered --> End([End])

    style BuildPrompt1 fill:#fff3e0
    style CallLLM1 fill:#e1f5ff
    style BuildPrompt2 fill:#fff3e0
    style CallLLM2 fill:#e1f5ff
    style CSVFiltered fill:#c8e6c9
```

**Two-Stage Pipeline**:

#### Stage 1: Classification
- **Input**: MCQ question text
- **Prompt**: Evaluate 5 dimensions (Assessability, Canonical Answer, Ambiguity, Scope, Intent Preservation)
- **Output**: Suitability score (1-10) + justification
- **Threshold**: Score ≥ 7 proceeds to conversion
- **Result**: 845/1144 (74%) deemed suitable

#### Stage 2: Conversion
- **Input**: Suitable MCQ with all fields
- **Prompt**: Convert while preserving construct and difficulty
- **Rules**:
  - Remove MCQ artifacts (A/B/C/D, "which of the following")
  - Maintain original intent (recall → recall, numeric → numeric)
  - Create canonical expected answer
  - Generate detailed grading rubric
  - Assign Bloom's taxonomy level
- **Output**: OSQ prompt, expected answer, rubric (full/partial/no credit), Bloom's level & justification

**Reliability Mechanisms**:
- Retry logic for JSON parsing failures
- Comprehensive logging (prompts + responses timestamped)
- Separate artifact directories for raw logs and parsed JSON

---

## Phase 3: MCQ Position Variants

### 3.1 MCQ Shift Golden Answer Location (`3.1_MCQ_Shift_Golden.ipynb`)

**Purpose**: Create 4 variants of the MCQ dataset with the correct answer rotated to positions A, B, C, and D to test for position bias.

```mermaid
flowchart TD
    Start([Start]) --> LoadHF[Load SysEngBench from HuggingFace<br/>rabell/SysEngBench<br/>1,144 MCQs]

    LoadHF --> CreateVariants{Create 4 Variants}

    CreateVariants --> VariantA[Variant A: Correct Answer at Position A]
    CreateVariants --> VariantB[Variant B: Correct Answer at Position B]
    CreateVariants --> VariantC[Variant C: Correct Answer at Position C]
    CreateVariants --> VariantD[Variant D: Correct Answer at Position D]

    VariantA --> RotateA[Rotate Choices<br/>Circular Shift Algorithm]
    VariantB --> RotateB[Rotate Choices<br/>Circular Shift Algorithm]
    VariantC --> RotateC[Rotate Choices<br/>Circular Shift Algorithm]
    VariantD --> RotateD[Rotate Choices<br/>Circular Shift Algorithm]

    RotateA --> UpdateA[Update Answer Field = A<br/>Update Label = 0]
    RotateB --> UpdateB[Update Answer Field = B<br/>Update Label = 1]
    RotateC --> UpdateC[Update Answer Field = C<br/>Update Label = 2]
    RotateD --> UpdateD[Update Answer Field = D<br/>Update Label = 3]

    UpdateA --> SaveA[Save sysengbench_a.csv]
    UpdateB --> SaveB[Save sysengbench_b.csv]
    UpdateC --> SaveC[Save sysengbench_c.csv]
    UpdateD --> SaveD[Save sysengbench_d.csv]

    SaveA --> Verify[Verification Step<br/>Preview First Row of Each Variant]
    SaveB --> Verify
    SaveC --> Verify
    SaveD --> Verify

    Verify --> End([End])

    style RotateA fill:#fff3e0
    style RotateB fill:#fff3e0
    style RotateC fill:#fff3e0
    style RotateD fill:#fff3e0
    style Verify fill:#c8e6c9
```

**Rotation Algorithm**:
```
def rotate(list, k):
    k = k % 4
    return list[-k:] + list[:-k]

Target Position | Current Position | Shift Amount
----------------|------------------|-------------
       A        |        A         |      0
       A        |        B         |      3
       A        |        C         |      2
       A        |        D         |      1
```

**Output Schema** (Same for all 4 variants):
- Columns: Question ID, Tags, INCOSE Category, Question, ChoiceA, ChoiceB, ChoiceC, ChoiceD, Answer, Label, Justification
- Rows: 1,144 (same questions, rotated choices)
- Semantic Equivalence: Maintained across all variants

**Purpose**: Enables detection of position bias by comparing model performance across variants where the only difference is the position of the correct answer.

---

## Phase 4: Model Inference

### 4.1 RunPod Infrastructure Setup (`runpod-on-vm-manual.ipynb`)

**Purpose**: Configure RunPod GPU instances with Ollama for running LLM evaluations.

```mermaid
flowchart TD
    Start([Start]) --> SelectGPU[Select RunPod GPU Pod<br/>A40 48GB VRAM]
    SelectGPU --> ConfigPod[Configure Pod<br/>- Template: PyTorch<br/>- Expose Port 11434<br/>- ENV: OLLAMA_HOST=0.0.0.0]
    ConfigPod --> SetStorage[Set Container & Volume Size<br/>Based on Model Requirements]
    SetStorage --> Deploy[Deploy Pod]

    Deploy --> SSHConnect[SSH into Pod]
    SSHConnect --> InstallDeps[Install Dependencies<br/>apt update && apt install lshw]
    InstallDeps --> InstallOllama[Install Ollama<br/>curl ollama.ai/install.sh | sh]
    InstallOllama --> StartOllama[Start Ollama Server<br/>ollama serve in SSH terminal]

    StartOllama --> JupyterSetup[Switch to Jupyter Interface]
    JupyterSetup --> InstallPython[Install Python Packages<br/>- lm_eval<br/>- ollama==0.3.3]

    InstallPython --> LoadModels{Model Loading Strategy}

    LoadModels --> Manual[Manual Array Definition<br/>Based on VRAM Requirements]
    LoadModels --> Excel[Excel Import<br/>Filter by Size < 48GB]

    Manual --> PullLoop[Model Pull Loop]
    Excel --> PullLoop

    PullLoop --> PullCmd[ollama pull model_name<br/>Sequential Downloads]
    PullCmd --> Verify[Verify Downloaded Models<br/>ollama.list]
    Verify --> APITest[API Connection Test<br/>OpenAI-Compatible Endpoint]
    APITest --> Ready[Ready for Inference]
    Ready --> End([End])

    style StartOllama fill:#fff3e0
    style PullLoop fill:#e1f5ff
    style Ready fill:#c8e6c9
```

**Infrastructure Configuration**:

**GPU Selection**:
- Single A40 (48GB VRAM): Models up to ~43GB
- 2× A40 (96GB VRAM): Models up to ~90GB
- 3× A40 (144GB VRAM): Largest models (~141GB)

**Software Stack**:
- Base: PyTorch template
- Server: Ollama (local LLM serving)
- Evaluation: lm-evaluation-harness
- API: OpenAI-compatible endpoint at `http://localhost:11434/v1/chat/completions`

**Model Management**:
- Pull models sequentially via `ollama pull`
- Verify with `ollama list()`
- Test with chat completions API before benchmarking

---

### 4.2 Batch Inference Execution (`keep-ollama-running-process.ipynb`)

**Purpose**: Execute lm-evaluation-harness across all models and benchmark variants with error handling and progress tracking.

```mermaid
flowchart TD
    Start([Start]) --> InitLog[Initialize Timestamped Log File<br/>progress_log_TIMESTAMP.txt]
    InitLog --> ServerCheck{Ollama Server Running?}

    ServerCheck -->|No| StartServer[Start Ollama Server<br/>Max 3 Retries, 10s Wait]
    ServerCheck -->|Yes| ModelLoop
    StartServer --> ServerReady{Server Ready?}
    ServerReady -->|No| Fail([Exit: Server Failed])
    ServerReady -->|Yes| ModelLoop

    ModelLoop[For Each Model in model_list] --> LogStart[Log: Processing Model X/N<br/>Timestamp + Model Name]

    LogStart --> PreCheck{Server Still Running?}
    PreCheck -->|No| Restart[Restart Ollama Server]
    PreCheck -->|Yes| BuildCmd
    Restart --> RetryCheck{Restart Successful?}
    RetryCheck -->|No| LogError[Log Error & Skip Model]
    RetryCheck -->|Yes| BuildCmd

    BuildCmd[Build lm_eval Command<br/>--model local-chat-completions<br/>--tasks TASK_NAME<br/>--output OUTPUT_DIR<br/>--log_samples<br/>--batch_size auto<br/>--gen_kwargs temperature=0.0] --> RunEval[Execute lm_eval via subprocess]

    RunEval --> Success{Evaluation Succeeded?}

    Success -->|Yes| LogSuccess[Log: Successfully Processed<br/>Timestamp]
    Success -->|No| CheckError{Server Error?}

    CheckError -->|Yes| RetryOnce[Restart Server & Retry Once]
    CheckError -->|No| LogFailure[Log Failure & Add to failed_models]

    RetryOnce --> RetryResult{Retry Succeeded?}
    RetryResult -->|Yes| LogSuccess
    RetryResult -->|No| LogFailure

    LogSuccess --> MoreModels{More Models?}
    LogFailure --> AddFailed[Append to failed_models list]
    AddFailed --> MoreModels
    LogError --> MoreModels

    MoreModels -->|Yes| ModelLoop
    MoreModels -->|No| Summary[Write Summary to Log<br/>- Total Models<br/>- Failed Count<br/>- Failed List]

    Summary --> End([End])

    style ServerCheck fill:#fff3e0
    style RunEval fill:#e1f5ff
    style LogSuccess fill:#c8e6c9
    style LogFailure fill:#ffcdd2
```

**Evaluation Configuration** (for each benchmark variant):

**MCQ Tasks** (SysEngBench, SysEngBench-A/B/C/D):
```yaml
task: sysengbench[-a/-b/-c/-d]
output_type: generate_until
doc_to_text: "Given the following question and four candidate answers..."
generation_kwargs:
  temperature: 0.0
  max_tokens: 20
  until: ["</s>", "\n"]
filter_list:
  - regex: "([ABCD])"
  - take_first
metric: exact_match
```

**OSQ Task** (SysEngBench-OSQ):
```yaml
task: sysengbench-osq
output_type: generate_until
doc_to_text: "{osq_prompt}"
generation_kwargs:
  temperature: 0.0
  max_tokens: 2000-10000 (model dependent)
  until: ["</s>"]
# No automatic grading - responses logged for Phase 5 LLM-as-judge
```

**Error Handling**:
- Server health checks before each model
- Automatic restart on connection errors
- Single retry per model on failure
- Comprehensive logging with timestamps
- Failed models tracked separately

**Output Structure**:
```
output/
├── sysengbench/
│   ├── results_TIMESTAMP.json
│   └── samples_TIMESTAMP.jsonl
├── sysengbench-a/
├── sysengbench-b/
├── sysengbench-c/
├── sysengbench-d/
└── sysengbench-osq/
    ├── results_TIMESTAMP.json
    └── samples_TIMESTAMP.jsonl  # Raw responses for judging
```

---

## Phase 5: LLM-as-a-Judge

### 5.1 LLM Judge Evaluation (`llm-judge.ipynb`)

**Purpose**: Score OSQ responses using LLM judges with academically-validated rubrics.

```mermaid
flowchart TD
    Start([Start]) --> Config[Configuration<br/>- Judge Model: GPT-4o / GPT-4o-mini<br/>- Temperature: 0.0<br/>- Rubric Variants]

    Config --> LoadResponses[Load OSQ Response Data<br/>From phase4 sysengbench-osq/*.jsonl]

    LoadResponses --> PromptSelect{Select Judging Approach}

    PromptSelect --> Binary[Binary Correct/Incorrect]
    PromptSelect --> Rubric1[Rubric 1: From MCQ→OSQ Conversion<br/>Full/Partial/No Credit]
    PromptSelect --> Rubric2[Rubric 2: Multi-Dimensional<br/>5 Dimensions × 0-10 Scale]
    PromptSelect --> CoT[Chain-of-Thought Scoring<br/>Step-by-step Reasoning]

    Binary --> BuildPrompts[Build Judge Prompts]
    Rubric1 --> BuildPrompts
    Rubric2 --> BuildPrompts
    CoT --> BuildPrompts

    BuildPrompts --> ForEach[For Each Model Response]
    ForEach --> CheckProgress{Resume from Last Position?}

    CheckProgress -->|Yes| FindLast[Read Existing JSONL<br/>Skip Completed Samples]
    CheckProgress -->|No| StartFresh[Start from Sample 0]

    FindLast --> NextSample[Get Next Unprocessed Sample]
    StartFresh --> NextSample

    NextSample --> BuildJudgePrompt[Build Judge Prompt<br/>- Original Question<br/>- Expected Answer<br/>- Model Response<br/>- Rubric Criteria]

    BuildJudgePrompt --> CallJudge[LLM Judge API Call<br/>JSON Response]
    CallJudge --> ParseScore[Parse JSON<br/>- Score/Judgment<br/>- Reasoning<br/>- Dimension Breakdown]

    ParseScore --> AppendSample[Append to samples_judged.jsonl<br/>Immediate Write]
    AppendSample --> UpdateProgress[Update Progress Bar]

    UpdateProgress --> MoreSamples{More Samples?}
    MoreSamples -->|Yes| NextSample
    MoreSamples -->|No| Organize[Organize Output by Task/Model<br/>Match phase4 Directory Structure]

    Organize --> SaveFinal[Save Final JSONL<br/>task/model/samples_judged.jsonl]
    SaveFinal --> End([End])

    style BuildJudgePrompt fill:#fff3e0
    style CallJudge fill:#e1f5ff
    style AppendSample fill:#c8e6c9
```

**Judging Approaches**:

#### 1. Binary Correct/Incorrect
- Simple yes/no judgment
- Fast baseline assessment
- Limited nuance

#### 2. Rubric-Based (from Conversion)
- Uses rubric generated in Phase 2
- Full credit: Meets all criteria
- Partial credit: Meets some criteria
- No credit: Fails key requirements

#### 3. Multi-Dimensional Scoring (Lin & Chen 2023)
- **Technical Accuracy** (0-10): Correctness of facts, principles, terminology
- **Conceptual Understanding** (0-10): Depth of systems thinking
- **Completeness** (0-10): Coverage of required elements
- **Clarity** (0-10): Communication quality
- **Professional Relevance** (0-10): Real-world applicability
- **Aggregate**: Mean or weighted average

#### 4. Chain-of-Thought (Zheng et al. 2023, G-Eval)
- Judge explains reasoning step-by-step
- Identifies strengths and weaknesses
- Provides final score with justification
- Higher human agreement (~85-98%)

**Academic Foundations**:
- Based on peer-reviewed methodologies
- Validated against human expert agreement
- Bias mitigation strategies (position, length)
- Integration with Bloom's taxonomy

**Reliability Features**:
- Resume capability: Reads existing JSONL to skip completed samples
- Incremental writes: Each sample written immediately (crash-safe)
- Progress tracking: tqdm progress bar with ETA
- Directory organization: Matches phase4 structure for easy merging

**Output Format** (per sample in JSONL):
```json
{
  "task": "sysengbench-osq",
  "doc_id": 42,
  "question": "...",
  "expected_answer": "...",
  "model_response": "...",
  "judge_model": "gpt-4o",
  "judgment": {
    "score": 8.5,
    "reasoning": "...",
    "technical_accuracy": 9,
    "conceptual_understanding": 8,
    "completeness": 9,
    "clarity": 8,
    "professional_relevance": 9
  }
}
```

---

## Phase 6: Results Processing & Analysis

### 6.1 Comprehensive Results Analysis (`results-processing.ipynb`)

**Purpose**: Aggregate results from all phases, perform statistical analysis, and generate visualizations for position bias, format comparison, and tokenomics.

```mermaid
flowchart TD
    Start([Start]) --> Inventory[File Inventory Check<br/>Discover all results.json & samples.jsonl<br/>Tasks: sysengbench, a, b, c, d, osq]

    Inventory --> LoadMCQ[Load MCQ Results<br/>sysengbench + variants a/b/c/d]
    Inventory --> LoadOSQ[Load OSQ Judged Results<br/>sysengbench-osq]

    LoadMCQ --> ParseMCQ[Parse MCQ Samples<br/>Extract: doc_id, response, target, correct]
    LoadOSQ --> ParseOSQ[Parse OSQ Samples<br/>Extract: doc_id, response, judgment, score]

    ParseOSQ --> CalcOSQ[Calculate OSQ Metrics<br/>Aggregate scores per model]
    CalcOSQ --> MergeOSQ[Merge with MCQ Data]
    ParseMCQ --> MergeOSQ

    MergeOSQ --> ThinkingFilter{Detect Thinking Models?}
    ThinkingFilter -->|Yes| StripThink[Strip think tags<br/>Extract reasoning tokens]
    ThinkingFilter -->|No| AnalysisBranch
    StripThink --> AnalysisBranch

    AnalysisBranch --> Analysis1[Position Bias Analysis]
    AnalysisBranch --> Analysis2[MCQ vs OSQ Comparison]
    AnalysisBranch --> Analysis3[Tokenomics & Cost Analysis]
    AnalysisBranch --> Analysis4[Statistical Testing]

    Analysis1 --> PosBias[Position Bias Detection<br/>- Chi-Square Test<br/>- Kruskal-Wallis H<br/>- Friedman Test<br/>- Pairwise McNemar<br/>- Cramér's V Effect Size]

    Analysis2 --> FormatComp[Format Comparison<br/>- Accuracy: MCQ vs OSQ<br/>- Correlation Analysis<br/>- Question-Level Consistency]

    Analysis3 --> Tokenomics[Tokenomics Analysis<br/>- Token Usage per Sample<br/>- Cost per Sample<br/>- Accuracy per Dollar<br/>- ROI: Thinking vs Standard<br/>- Break-even Analysis]

    Analysis4 --> StatTests[Statistical Test Suite<br/>- Normality Tests Shapiro-Wilk, Jarque-Bera<br/>- Effect Sizes Cohen's d, Hedges' g<br/>- Bootstrap CI 10k resamples<br/>- Q-Q Plots]

    PosBias --> Viz1[Visualizations: Position Bias<br/>- Bar charts by position<br/>- Heatmaps<br/>- Deviation from expected]
    FormatComp --> Viz2[Visualizations: Format Comparison<br/>- MCQ vs OSQ accuracy<br/>- Scatter plots<br/>- Correlation matrices]
    Tokenomics --> Viz3[Visualizations: Tokenomics<br/>- Cost vs Accuracy<br/>- Efficiency Frontiers<br/>- ROI Curves<br/>- Break-even Points]
    StatTests --> Viz4[Statistical Plots<br/>- Q-Q Plots<br/>- Bootstrap Distributions<br/>- Effect Size Visualizations]

    Viz1 --> ExportCSV[Export Analysis CSVs<br/>- position_bias_analysis.csv<br/>- mcq_vs_osq_analysis.csv<br/>- model_detailed.csv per model]
    Viz2 --> ExportCSV
    Viz3 --> ExportCSV
    Viz4 --> ExportCSV

    ExportCSV --> ExportViz[Export Visualizations<br/>- position_bias_analysis.png<br/>- mcq_vs_osq_analysis.png<br/>- tokenomics_analysis.png<br/>- statistical_tests.png]

    ExportViz --> Summary[Generate Summary Report<br/>Key Insights:<br/>- Position bias quantification<br/>- Format preference<br/>- Cost-effectiveness thresholds<br/>- Statistical significance]

    Summary --> End([End])

    style PosBias fill:#fff3e0
    style FormatComp fill:#fff3e0
    style Tokenomics fill:#e1f5ff
    style StatTests fill:#e1f5ff
    style Summary fill:#c8e6c9
```

**Analysis Outputs**:

### Position Bias Analysis
- **Metrics**: Accuracy by position (A, B, C, D)
- **Tests**:
  - Chi-Square test for independence
  - Kruskal-Wallis H (non-parametric ANOVA)
  - Friedman test (repeated measures)
  - Pairwise McNemar tests
  - Cramér's V for effect size
- **Outputs**:
  - CSV with per-model position preferences
  - Visualization showing accuracy deviation by position
  - Statistical significance indicators

### MCQ vs OSQ Comparison
- **Metrics**:
  - Overall accuracy: MCQ vs OSQ
  - Per-model correlation
  - Question-level consistency
- **Outputs**:
  - Scatter plots: MCQ accuracy vs OSQ accuracy
  - Correlation matrices
  - CSV with comparative statistics

### Tokenomics & Cost Analysis
- **Metrics**:
  - Average tokens per sample
  - Cost per sample (based on model pricing)
  - Accuracy per dollar (efficiency metric)
  - ROI for thinking models vs standard models
  - Break-even analysis (at what scale does extra accuracy justify extra cost?)
- **Example Insights**:
  ```
  Model            Accuracy  Avg_Tokens  Cost/Sample  Acc/$
  deepseek-r1:7b   0.78      3,245       $0.00097     803
  llama3.2:3b      0.61      187         $0.00002     30,500

  At 10,000 samples:
  - Extra cost: $24.50
  - Extra correct: 1,700
  - Cost per extra correct: $0.0144
  ```
- **Outputs**:
  - Cost vs accuracy scatter plots
  - Efficiency frontier curves
  - ROI curves for different sample sizes
  - CSV with full tokenomics data

### Statistical Testing
- **Normality Tests**: Shapiro-Wilk, D'Agostino's K², Jarque-Bera
- **Effect Sizes**: Cohen's d, Glass's Δ, Hedges' g
- **Confidence Intervals**: Bootstrap with 10,000 resamples
- **Visualizations**: Q-Q plots, distribution plots, effect size charts
- **Interpretation Guidelines**: Negligible/Small/Medium/Large effects

**Final Deliverables**:
1. **CSV Files**: Detailed results for each analysis dimension
2. **Visualizations**: Publication-ready plots in PNG format
3. **Summary Report**: Markdown document with key findings and statistical significance
4. **Decision Framework**: Recommendations for:
   - When to use thinking models
   - Position bias mitigation strategies
   - MCQ vs OSQ format selection
   - Sample size optimization for cost-effectiveness

---

## Data Flow Summary

```mermaid
flowchart LR
    P1[Phase 1<br/>Download &amp; Summarize<br/>1,144 MCQs] --> P2A[Phase 2<br/>MCQ→OSQ Conversion<br/>845 OSQs]
    P1 --> P3[Phase 3<br/>Position Variants<br/>4 × 1,144 MCQs]

    P3 --> P4A[Phase 4<br/>MCQ Inference<br/>5 Tasks]
    P2A --> P4B[Phase 4<br/>OSQ Inference<br/>1 Task]

    P4A --> P6[Phase 6<br/>Analysis &amp; Results]
    P4B --> P5[Phase 5<br/>LLM-as-Judge<br/>Score OSQ Responses]

    P5 --> P6

    P6 --> OUT1[Position Bias<br/>Metrics &amp; Viz]
    P6 --> OUT2[MCQ vs OSQ<br/>Comparison]
    P6 --> OUT3[Tokenomics<br/>ROI Analysis]
    P6 --> OUT4[Statistical<br/>Significance]

    style P1 fill:#e1f5ff
    style P2A fill:#fff3e0
    style P3 fill:#fff3e0
    style P4A fill:#e1f5ff
    style P4B fill:#e1f5ff
    style P5 fill:#fff3e0
    style P6 fill:#c8e6c9
    style OUT1 fill:#c8e6c9
    style OUT2 fill:#c8e6c9
    style OUT3 fill:#c8e6c9
    style OUT4 fill:#c8e6c9
```

---

## Notebook Processing Order

**Sequential Dependencies**:

1. **Phase 1.1** → **Phase 1.2** (download before summarize)
2. **Phase 1** → **Phase 2** (base data before conversion)
3. **Phase 1** → **Phase 3** (base data before variants)
4. **Phases 2 & 3** → **Phase 4** (datasets ready before inference)
5. **Phase 4 (OSQ)** → **Phase 5** (responses ready before judging)
6. **Phases 4 & 5** → **Phase 6** (all results ready before analysis)

**Parallelizable**:
- Phase 2 and Phase 3 can run in parallel (independent of each other)
- Phase 4 inference across different tasks can run in parallel (separate evaluation runs)
- Phase 5 judging can process multiple models in parallel (independent samples)

---

## Key Design Patterns Across All Phases

### 1. **Artifact-Based Communication**
- Each phase produces well-defined outputs (CSV, JSONL, YAML)
- Enables phase independence and re-execution
- Clear schema definitions for data interchange

### 2. **Robust Error Handling**
- Retry logic for API calls
- Comprehensive logging with timestamps
- Progress tracking and resume capabilities
- Failed item tracking for post-analysis

### 3. **Academic Rigor**
- Peer-reviewed methodologies referenced
- Statistical significance testing
- Multiple evaluation approaches for validation
- Bloom's taxonomy integration

### 4. **Cost Awareness**
- Token tracking throughout pipeline
- Economic analysis at multiple scales
- ROI modeling for decision support
- Break-even calculations

### 5. **Reproducibility**
- Fixed random seeds where applicable
- Temperature = 0.0 for deterministic outputs
- Versioned datasets on HuggingFace
- Complete configuration documentation

---

## Technical Stack

**Languages & Frameworks**:
- Python 3.11+
- Pandas (data manipulation)
- Datasets (HuggingFace)
- lm-evaluation-harness (benchmarking)
- Matplotlib/Seaborn (visualization)
- SciPy/NumPy (statistical analysis)

**Infrastructure**:
- RunPod (GPU compute)
- Ollama (local LLM serving)
- OpenRouter API (cloud LLM access)
- HuggingFace Hub (dataset hosting)

**Development Environment**:
- Jupyter Notebooks (interactive analysis)
- Git (version control)
- .env (secrets management)

---

## Appendix: File Locations

**Phase 1**:
- `src/phase1_prep/1.1_sysengbench_hf_download.ipynb`
- `src/phase1_prep/1.2_benchmark-summary.ipynb`
- `src/phase1_prep/sysengbench.csv`

**Phase 2**:
- `src/phase2_conversion/2.1_Converting_MCQ_to_OSQ.ipynb`
- `src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq.csv`
- `src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv`

**Phase 3**:
- `src/phase3_variants/3.1_MCQ_Shift_Golden.ipynb`
- `src/phase3_variants/sysengbench_{a,b,c,d}.csv`

**Phase 4**:
- `src/phase4_inference/runpod-on-vm-manual.ipynb`
- `src/phase4_inference/keep-ollama-running-process.ipynb`
- `src/phase4_inference/*.yaml` (task configurations)
- `src/phase4_inference/output/` (results directories)

**Phase 5**:
- `src/phase5_llm_as_a_judge/llm-judge.ipynb`
- `src/phase5_llm_as_a_judge/sysengbench-osq/` (judged outputs)

**Phase 6**:
- `src/phase6_analysis/results-processing.ipynb`
- Output CSVs and visualizations

---

*This document was generated for dissertation methods section inclusion. All diagrams use Mermaid syntax for easy rendering in Markdown-compatible environments.*
