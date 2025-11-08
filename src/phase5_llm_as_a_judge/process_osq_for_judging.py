"""
Script to process OSQ outputs to a final output JSON file that matches the MCQ format
for phase 5 LLM-as-judge grading.

This script:
1. Reads OSQ response samples from phase 4 output
2. Reformats them to match the structure expected by the LLM judge
3. Outputs a standardized JSON/JSONL file ready for grading

Author: Claude
Date: 2025-11-08
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime


class OSQOutputProcessor:
    """Process OSQ outputs from phase 4 for phase 5 LLM judging."""

    def __init__(self,
                 osq_output_dir: str = "src/phase4_inference/downloaded_output/sysengbench-osq",
                 osq_csv_path: str = "src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv",
                 output_dir: str = "src/phase5_llm_as_a_judge/processed_osq_outputs"):
        """
        Initialize the processor.

        Args:
            osq_output_dir: Directory containing phase 4 OSQ outputs (organized by model)
            osq_csv_path: Path to the OSQ metadata CSV with expected answers, rubrics, etc.
            output_dir: Directory to save processed outputs
        """
        self.osq_output_dir = Path(osq_output_dir)
        self.osq_csv_path = Path(osq_csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load OSQ metadata (expected answers, rubrics, etc.)
        print(f"Loading OSQ metadata from {self.osq_csv_path}")
        self.osq_metadata = pd.read_csv(self.osq_csv_path)
        print(f"Loaded {len(self.osq_metadata)} OSQ questions")

    def load_model_osq_responses(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Load all OSQ responses for a given model.

        Args:
            model_name: Name of the model directory

        Returns:
            List of parsed JSONL records
        """
        model_dir = self.osq_output_dir / model_name
        if not model_dir.exists():
            print(f"Warning: Model directory not found: {model_dir}")
            return []

        # Find the samples JSONL file
        jsonl_files = list(model_dir.glob("samples_*.jsonl"))
        if not jsonl_files:
            print(f"Warning: No samples JSONL found in {model_dir}")
            return []

        # Use the most recent file if multiple exist
        jsonl_file = sorted(jsonl_files, key=lambda x: x.stat().st_mtime)[-1]
        print(f"  Loading responses from: {jsonl_file.name}")

        responses = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    responses.append(json.loads(line))

        return responses

    def process_single_response(self, response: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Process a single OSQ response to match the format expected by the LLM judge.

        Args:
            response: Raw response from phase 4 output
            model_name: Name of the model that generated the response

        Returns:
            Processed response record for judging
        """
        doc_id = response['doc_id']
        doc = response['doc']

        # Get model response (from filtered_resps)
        model_response = response['filtered_resps'][0] if response['filtered_resps'] else ""

        # Get expected answer and rubric from metadata
        question_id = doc.get('Question ID', doc_id + 1)
        metadata_row = self.osq_metadata[self.osq_metadata['Question ID'] == question_id]

        if metadata_row.empty:
            print(f"Warning: No metadata found for Question ID {question_id}")
            expected_answer = doc.get('expected_answer', '')
            full_credit = partial_credit = no_credit = blooms = ""
        else:
            metadata_row = metadata_row.iloc[0]
            expected_answer = metadata_row.get('expected_answer', '')
            full_credit = metadata_row.get('full_credit_criteria', '')
            partial_credit = metadata_row.get('partial_credit_criteria', '')
            no_credit = metadata_row.get('no_credit_criteria', '')
            blooms = metadata_row.get('blooms_level', '')

        # Build the processed record
        processed = {
            "task": "sysengbench-osq",
            "doc_id": doc_id,
            "question_id": question_id,
            "model": model_name,
            "question": doc.get('question', ''),
            "osq_prompt": doc.get('osq_prompt', ''),
            "expected_answer": expected_answer,
            "model_response": model_response,
            "rubric": {
                "full_credit_criteria": full_credit,
                "partial_credit_criteria": partial_credit,
                "no_credit_criteria": no_credit
            },
            "blooms_level": blooms,
            "incose_category": doc.get('INCOSE Handbook Category', ''),
            "tags": doc.get('Tags', ''),
            # Preserve original fields for reference
            "original_doc": doc,
            "doc_hash": response.get('doc_hash', ''),
            "prompt_hash": response.get('prompt_hash', '')
        }

        return processed

    def process_model(self, model_name: str) -> None:
        """
        Process all responses for a single model.

        Args:
            model_name: Name of the model to process
        """
        print(f"\nProcessing model: {model_name}")

        # Load responses
        responses = self.load_model_osq_responses(model_name)
        if not responses:
            return

        print(f"  Found {len(responses)} responses")

        # Process each response
        processed_responses = []
        for response in responses:
            processed = self.process_single_response(response, model_name)
            processed_responses.append(processed)

        # Create output directory for this model
        model_output_dir = self.output_dir / model_name
        model_output_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSONL (one record per line for easy streaming)
        output_file = model_output_dir / f"osq_for_judging_{model_name}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in processed_responses:
                f.write(json.dumps(record) + '\n')

        print(f"  Saved {len(processed_responses)} processed responses to: {output_file}")

        # Also save as single JSON for convenience
        output_json = model_output_dir / f"osq_for_judging_{model_name}.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(processed_responses, f, indent=2)

        print(f"  Also saved as JSON: {output_json}")

    def process_all_models(self) -> None:
        """Process all models found in the OSQ output directory."""
        if not self.osq_output_dir.exists():
            print(f"Error: OSQ output directory not found: {self.osq_output_dir}")
            return

        # Get all model directories
        model_dirs = [d for d in self.osq_output_dir.iterdir() if d.is_dir()]

        if not model_dirs:
            print(f"Warning: No model directories found in {self.osq_output_dir}")
            return

        print(f"Found {len(model_dirs)} model directories")

        for model_dir in sorted(model_dirs):
            self.process_model(model_dir.name)

        print(f"\n✓ Processing complete! Output saved to: {self.output_dir}")

    def generate_summary_report(self) -> None:
        """Generate a summary report of processed outputs."""
        report_path = self.output_dir / "processing_summary.txt"

        model_dirs = [d for d in self.output_dir.iterdir() if d.is_dir()]

        with open(report_path, 'w') as f:
            f.write(f"OSQ Output Processing Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"="* 80 + "\n\n")

            f.write(f"Total models processed: {len(model_dirs)}\n\n")

            for model_dir in sorted(model_dirs):
                jsonl_file = model_dir / f"osq_for_judging_{model_dir.name}.jsonl"
                if jsonl_file.exists():
                    with open(jsonl_file, 'r') as jf:
                        count = sum(1 for _ in jf)
                    f.write(f"  {model_dir.name}: {count} responses\n")

        print(f"\n✓ Summary report saved to: {report_path}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process OSQ outputs for Phase 5 LLM-as-judge grading"
    )
    parser.add_argument(
        "--osq-output-dir",
        default="src/phase4_inference/downloaded_output/sysengbench-osq",
        help="Directory containing phase 4 OSQ outputs"
    )
    parser.add_argument(
        "--osq-csv",
        default="src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv",
        help="Path to OSQ metadata CSV"
    )
    parser.add_argument(
        "--output-dir",
        default="src/phase5_llm_as_a_judge/processed_osq_outputs",
        help="Output directory for processed files"
    )
    parser.add_argument(
        "--model",
        help="Process only this specific model (otherwise processes all)"
    )

    args = parser.parse_args()

    # Initialize processor
    processor = OSQOutputProcessor(
        osq_output_dir=args.osq_output_dir,
        osq_csv_path=args.osq_csv,
        output_dir=args.output_dir
    )

    # Process
    if args.model:
        processor.process_model(args.model)
    else:
        processor.process_all_models()

    # Generate summary
    processor.generate_summary_report()


if __name__ == "__main__":
    main()
