"""
Phase 6 Analysis - Data Parsers for MCQ and OSQ Results

This module provides functions to parse Phase 4 MCQ inference results
and Phase 5 LLM-as-judge OSQ results into structured dataframes.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re


def parse_timestamp(filename: str) -> datetime:
    """
    Parse timestamp from filename.

    Args:
        filename: Filename containing timestamp (e.g., 'results_2025-09-25T04-03-54.642579.json')

    Returns:
        datetime object
    """
    # Extract timestamp: 2025-09-25T04-03-54.642579
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})', filename)
    if match:
        timestamp_str = match.group(1)
        # Convert time hyphens to colons
        date_part, time_part = timestamp_str.split('T')
        time_part = time_part.replace('-', ':')
        iso_str = f"{date_part}T{time_part}"
        return datetime.fromisoformat(iso_str)
    return datetime.min


def get_latest_file(files: List[Path]) -> Optional[Path]:
    """
    Get the most recent file from a list based on timestamp in filename.

    Args:
        files: List of Path objects

    Returns:
        Most recent file or None if list is empty
    """
    if not files:
        return None

    file_times = [(f, parse_timestamp(f.name)) for f in files]
    file_times.sort(key=lambda x: x[1], reverse=True)
    return file_times[0][0]


def parse_mcq_samples(phase4_dir: Path, use_latest: bool = True) -> List[Dict]:
    """
    Parse MCQ samples from Phase 4 inference outputs.

    Args:
        phase4_dir: Path to phase4_inference/downloaded_output directory
        use_latest: If True, use only the most recent file when duplicates exist

    Returns:
        List of dictionaries with parsed MCQ data
    """
    mcq_data = []

    # Expected variants (excluding OSQ for now)
    mcq_variants = ['sysengbench', 'sysengbench-a', 'sysengbench-b',
                    'sysengbench-c', 'sysengbench-d']

    for variant_name in mcq_variants:
        variant_dir = phase4_dir / variant_name
        if not variant_dir.exists():
            print(f"⚠️  Warning: Variant directory not found: {variant_dir}")
            continue

        for model_dir in variant_dir.iterdir():
            if not model_dir.is_dir():
                continue

            model_name = model_dir.name

            # Get samples files
            samples_files = list(model_dir.glob("samples_*.jsonl"))

            if not samples_files:
                print(f"⚠️  Warning: No samples file found for {variant_name}/{model_name}")
                continue

            # Select file (latest or all)
            if use_latest:
                samples_file = get_latest_file(samples_files)
                samples_files = [samples_file] if samples_file else []

            # Parse each samples file
            for samples_file in samples_files:
                print(f"📖 Parsing {variant_name}/{model_name}/{samples_file.name}")

                with open(samples_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            sample = json.loads(line.strip())

                            # Extract key fields
                            doc = sample.get('doc', {})
                            question_id = doc.get('Question ID')
                            category = doc.get('INCOSE Handbook Category', '')
                            tags = doc.get('Tags', '')
                            question_text = doc.get('question', '')

                            # Correct answer
                            correct_answer = sample.get('target', doc.get('answer', ''))

                            # Model's answer
                            filtered_resps = sample.get('filtered_resps', [])
                            model_answer = filtered_resps[0] if filtered_resps else ''

                            # Raw response
                            resps = sample.get('resps', [[]])
                            raw_response = resps[0][0] if resps and resps[0] else ''

                            # Correctness
                            is_correct = sample.get('exact_match', 0.0) == 1.0

                            # Extract variant letter (a/b/c/d) or 'base' for sysengbench
                            if variant_name == 'sysengbench':
                                variant_letter = 'random'  # Randomized positions
                            else:
                                variant_letter = variant_name.split('-')[-1]  # a, b, c, or d

                            mcq_data.append({
                                'model': model_name,
                                'question_id': question_id,
                                'variant': variant_letter,
                                'variant_full': variant_name,
                                'category': category,
                                'tags': tags,
                                'question': question_text,
                                'correct_answer': correct_answer,
                                'model_answer': model_answer,
                                'raw_response': raw_response,
                                'is_correct': is_correct,
                                'doc_id': sample.get('doc_id'),
                                'file': samples_file.name
                            })

                        except json.JSONDecodeError as e:
                            print(f"   ⚠️  JSON decode error at line {line_num}: {e}")
                        except Exception as e:
                            print(f"   ⚠️  Error processing line {line_num}: {e}")

    print(f"✅ Parsed {len(mcq_data)} MCQ samples")
    return mcq_data


def parse_osq_judged_samples(phase5_dir: Path, use_latest: bool = True) -> List[Dict]:
    """
    Parse judged OSQ samples from Phase 5 LLM-as-a-judge outputs.

    Args:
        phase5_dir: Path to phase5_llm_as_a_judge directory
        use_latest: If True, use only the most recent file when duplicates exist

    Returns:
        List of dictionaries with parsed OSQ data
    """
    osq_data = []

    # Look for judged results
    judge_dir = phase5_dir / "sysengbench-osq-llm-judge"

    if not judge_dir.exists():
        print(f"⚠️  Warning: Judge directory not found: {judge_dir}")
        return osq_data

    for model_dir in judge_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name

        # Get judged samples files (format: samples_*__<judge>.jsonl)
        judged_files = list(model_dir.glob("samples_*__*.jsonl"))

        if not judged_files:
            print(f"⚠️  Warning: No judged samples file found for {model_name}")
            continue

        # Select file (latest or all)
        if use_latest:
            judged_file = get_latest_file(judged_files)
            judged_files = [judged_file] if judged_file else []

        # Parse each judged file
        for judged_file in judged_files:
            # Extract judge name and prompt ID from filename
            # Pattern: samples_*__openai_gpt-5-p1.jsonl -> judge=openai_gpt-5, prompt=p1
            judge_match = re.search(r'__(.+)-(p\d+)\.jsonl$', judged_file.name)
            if judge_match:
                judge_name = judge_match.group(1)
                prompt_id = judge_match.group(2)
            else:
                # Fallback for old format without prompt ID
                judge_match_old = re.search(r'__(.+)\.jsonl$', judged_file.name)
                judge_name = judge_match_old.group(1) if judge_match_old else 'unknown'
                prompt_id = 'unknown'

            print(f"📖 Parsing {model_name}/{judged_file.name} (judge: {judge_name}, prompt: {prompt_id})")

            with open(judged_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        sample = json.loads(line.strip())

                        # Extract from phase4_row
                        phase4_row = sample.get('phase4_row', {})
                        doc = phase4_row.get('doc', {})

                        question_id = doc.get('Question ID')
                        category = doc.get('INCOSE Handbook Category', '')
                        tags = doc.get('Tags', '')
                        osq_prompt = doc.get('osq_prompt', '')
                        expected_answer = doc.get('expected_answer', '')
                        blooms_level = doc.get('blooms_level', '')

                        # Model's response
                        filtered_resps = phase4_row.get('filtered_resps', [])
                        model_response = filtered_resps[0] if filtered_resps else ''

                        # Judge scores
                        judge = sample.get('judge', {})
                        fields = judge.get('fields', {})

                        technical_accuracy = fields.get('technical_accuracy', {}).get('score', 0)
                        conceptual_understanding = fields.get('conceptual_understanding', {}).get('score', 0)
                        completeness = fields.get('completeness', {}).get('score', 0)
                        clarity_organization = fields.get('clarity_organization', {}).get('score', 0)
                        professional_relevance = fields.get('professional_relevance', {}).get('score', 0)

                        # Calculate total_score and percentage
                        total_score = (technical_accuracy + conceptual_understanding +
                                     completeness + clarity_organization + professional_relevance)
                        max_score = 100  # 5 fields × 20 points each
                        percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

                        # Determine correctness (>= 70/100)
                        is_correct = total_score >= 70

                        osq_data.append({
                            'model': model_name,
                            'question_id': question_id,
                            'category': category,
                            'tags': tags,
                            'osq_prompt': osq_prompt,
                            'expected_answer': expected_answer,
                            'model_response': model_response,
                            'blooms_level': blooms_level,
                            'judge_model': judge_name,
                            'prompt_id': prompt_id,
                            'technical_accuracy': technical_accuracy,
                            'conceptual_understanding': conceptual_understanding,
                            'completeness': completeness,
                            'clarity_organization': clarity_organization,
                            'professional_relevance': professional_relevance,
                            'total_score': total_score,
                            'percentage': percentage,
                            'is_correct': is_correct,
                            'sample_id': sample.get('sample_id'),
                            'file': judged_file.name
                        })

                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  JSON decode error at line {line_num}: {e}")
                    except Exception as e:
                        print(f"   ⚠️  Error processing line {line_num}: {e}")

    print(f"✅ Parsed {len(osq_data)} OSQ judged samples")
    return osq_data


def detect_thinking_model(model_name: str, response_text: str) -> Dict[str, bool]:
    """
    Detect if a model is a thinking model and analyze its response.

    Args:
        model_name: Name of the model
        response_text: The model's response text

    Returns:
        Dictionary with thinking model flags:
            - is_thinking_model: True if model is a known thinking model
            - has_think_tags: True if response contains <think> tags
            - appears_truncated: True if response appears cut off
    """
    # Known thinking models
    thinking_models = [
        'deepseek-r1',
        'deepseek-r1:7b',
        'qwq',
        'qwq:32b'
    ]

    model_lower = model_name.lower()
    is_thinking = any(tm in model_lower for tm in thinking_models)

    # Check for thinking tags
    has_think_tags = '<think>' in response_text or '</think>' in response_text

    # Check for truncation indicators
    appears_truncated = (
        len(response_text) >= 1900 and  # Near 2000 token limit
        not response_text.rstrip().endswith(('.', '!', '?', '</think>'))  # Doesn't end properly
    )

    return {
        'is_thinking_model': is_thinking,
        'has_think_tags': has_think_tags,
        'appears_truncated': appears_truncated
    }


def filter_osq_data(osq_data: List[Dict],
                   judge_model: Optional[str] = None,
                   prompt_id: Optional[str] = None) -> List[Dict]:
    """
    Filter OSQ data by judge model and/or prompt ID.

    Args:
        osq_data: List of OSQ samples from parse_osq_judged_samples()
        judge_model: Judge model to filter by (e.g., 'openai_gpt-5'). None = all judges
        prompt_id: Prompt ID to filter by (e.g., 'p1'). None = all prompts

    Returns:
        Filtered list of OSQ records
    """
    filtered = osq_data

    if judge_model is not None:
        filtered = [r for r in filtered if r.get('judge_model') == judge_model]

    if prompt_id is not None:
        filtered = [r for r in filtered if r.get('prompt_id') == prompt_id]

    return filtered


def get_available_judges_and_prompts(osq_data: List[Dict]) -> Dict[str, List[str]]:
    """
    Get list of available judges and prompts from OSQ data.

    Args:
        osq_data: List of OSQ samples from parse_osq_judged_samples()

    Returns:
        Dictionary with 'judges' and 'prompts' keys containing unique values
    """
    judges = sorted(set(r.get('judge_model', 'unknown') for r in osq_data))
    prompts = sorted(set(r.get('prompt_id', 'unknown') for r in osq_data))

    return {
        'judges': judges,
        'prompts': prompts
    }


def align_mcq_osq_results(mcq_data: List[Dict], osq_data: List[Dict],
                         missing_data_strategy: str = 'drop') -> List[Dict]:
    """
    Align MCQ and OSQ results by question_id and model.

    Creates one row per (model, question_id) with MCQ results across all variants
    and corresponding OSQ results.

    Args:
        mcq_data: List of MCQ samples from parse_mcq_samples()
        osq_data: List of OSQ samples from parse_osq_judged_samples()
        missing_data_strategy: 'drop' (remove incomplete) or 'impute' (fill with None)

    Returns:
        List of aligned records
    """
    aligned = []

    # Group MCQ data by (model, question_id)
    mcq_grouped = {}
    for record in mcq_data:
        key = (record['model'], record['question_id'])
        if key not in mcq_grouped:
            mcq_grouped[key] = {
                'model': record['model'],
                'question_id': record['question_id'],
                'category': record['category'],
                'tags': record['tags'],
                'question': record['question'],
                'mcq_random_correct': None,
                'mcq_a_correct': None,
                'mcq_b_correct': None,
                'mcq_c_correct': None,
                'mcq_d_correct': None
            }

        # Assign to appropriate variant
        variant = record['variant']
        if variant == 'random':
            mcq_grouped[key]['mcq_random_correct'] = record['is_correct']
        elif variant == 'a':
            mcq_grouped[key]['mcq_a_correct'] = record['is_correct']
        elif variant == 'b':
            mcq_grouped[key]['mcq_b_correct'] = record['is_correct']
        elif variant == 'c':
            mcq_grouped[key]['mcq_c_correct'] = record['is_correct']
        elif variant == 'd':
            mcq_grouped[key]['mcq_d_correct'] = record['is_correct']

    # Group OSQ data by (model, question_id)
    osq_grouped = {}
    for record in osq_data:
        key = (record['model'], record['question_id'])
        osq_grouped[key] = {
            'osq_total_score': record['total_score'],
            'osq_percentage': record['percentage'],
            'osq_is_correct': record['is_correct'],
            'osq_technical_accuracy': record['technical_accuracy'],
            'osq_conceptual_understanding': record['conceptual_understanding'],
            'osq_completeness': record['completeness'],
            'osq_clarity_organization': record['clarity_organization'],
            'osq_professional_relevance': record['professional_relevance'],
            'blooms_level': record['blooms_level'],
            'judge_model': record['judge_model'],
            'prompt_id': record['prompt_id']
        }

    # Merge MCQ and OSQ
    all_keys = set(mcq_grouped.keys()) | set(osq_grouped.keys())

    for key in all_keys:
        model, question_id = key

        # Start with MCQ data
        if key in mcq_grouped:
            record = mcq_grouped[key].copy()
        else:
            record = {
                'model': model,
                'question_id': question_id,
                'category': None,
                'tags': None,
                'question': None,
                'mcq_random_correct': None,
                'mcq_a_correct': None,
                'mcq_b_correct': None,
                'mcq_c_correct': None,
                'mcq_d_correct': None
            }

        # Add OSQ data
        if key in osq_grouped:
            record.update(osq_grouped[key])
        else:
            record.update({
                'osq_total_score': None,
                'osq_percentage': None,
                'osq_is_correct': None,
                'osq_technical_accuracy': None,
                'osq_conceptual_understanding': None,
                'osq_completeness': None,
                'osq_clarity_organization': None,
                'osq_professional_relevance': None,
                'blooms_level': None,
                'judge_model': None,
                'prompt_id': None
            })

        # Calculate MCQ average (across fixed position variants a/b/c/d, excluding random)
        mcq_scores = [
            record['mcq_a_correct'],
            record['mcq_b_correct'],
            record['mcq_c_correct'],
            record['mcq_d_correct']
        ]
        mcq_scores_valid = [s for s in mcq_scores if s is not None]
        record['mcq_avg_correct'] = (
            sum(mcq_scores_valid) / len(mcq_scores_valid)
            if mcq_scores_valid else None
        )

        # Apply missing data strategy
        if missing_data_strategy == 'drop':
            # Drop if missing both MCQ and OSQ data
            has_mcq = record['mcq_avg_correct'] is not None
            has_osq = record['osq_total_score'] is not None
            if not (has_mcq or has_osq):
                continue

        aligned.append(record)

    print(f"✅ Aligned {len(aligned)} records (strategy: {missing_data_strategy})")
    return aligned


if __name__ == '__main__':
    # Test the parsers
    print("=" * 80)
    print("TESTING PARSERS")
    print("=" * 80)

    phase4_dir = Path("src/phase4_inference/downloaded_output")
    phase5_dir = Path("src/phase5_llm_as_a_judge")

    # Test MCQ parser
    print("\n--- Testing MCQ Parser ---")
    mcq_data = parse_mcq_samples(phase4_dir, use_latest=True)
    if mcq_data:
        print(f"\nSample MCQ record:")
        for k, v in list(mcq_data[0].items()):
            print(f"  {k}: {v}")

    # Test OSQ parser
    print("\n--- Testing OSQ Parser ---")
    osq_data = parse_osq_judged_samples(phase5_dir, use_latest=True)
    if osq_data:
        print(f"\nSample OSQ record:")
        for k, v in list(osq_data[0].items()):
            print(f"  {k}: {v}")

    # Test alignment
    print("\n--- Testing Alignment ---")
    aligned = align_mcq_osq_results(mcq_data, osq_data, missing_data_strategy='drop')
    if aligned:
        print(f"\nSample aligned record:")
        for k, v in list(aligned[0].items()):
            print(f"  {k}: {v}")
