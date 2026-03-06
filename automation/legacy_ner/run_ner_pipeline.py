from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_cmd(args: list[str]) -> None:
    print('+', ' '.join(args))
    subprocess.run(args, check=True)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, list):
        raise ValueError('manifest must be a JSON list')
    out: list[dict[str, Any]] = []
    for item in obj:
        if isinstance(item, dict):
            out.append(item)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description='Run NER data pipeline: import external -> merge -> split.')
    ap.add_argument('--manifest', default=None, help='JSON manifest for external raw datasets to import')
    ap.add_argument('--internal-input', action='append', default=[], help='Existing internal JSONL inputs (repeatable)')
    ap.add_argument('--external-converted', action='append', default=[], help='Already converted external JSONL inputs (repeatable)')
    ap.add_argument('--work-dir', default='data/ner/pipeline', help='Working directory for merged/split outputs')
    ap.add_argument('--group-key', default='company_name', help='Split grouping field')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--train-ratio', type=float, default=0.8)
    ap.add_argument('--valid-ratio', type=float, default=0.1)
    ap.add_argument('--test-ratio', type=float, default=0.1)
    ap.add_argument('--min-entities', type=int, default=1, help='Min entities required in merge output')
    args = ap.parse_args()

    work_dir = Path(args.work_dir)
    converted_dir = work_dir / 'converted'
    merged_path = work_dir / 'merged.jsonl'
    split_dir = work_dir / 'split'
    converted_dir.mkdir(parents=True, exist_ok=True)

    converted_inputs = [Path(p) for p in args.external_converted]

    if args.manifest:
        manifest = load_manifest(Path(args.manifest))
        for item in manifest:
            input_path = Path(str(item['input']))
            dataset_name = str(item['dataset_name'])
            out_name = str(item.get('output_name') or f'{dataset_name}_converted.jsonl')
            out_path = converted_dir / out_name
            cmd = [
                sys.executable,
                'automation/legacy_ner/import_external_ner.py',
                '--input', str(input_path),
                '--output', str(out_path),
                '--dataset-name', dataset_name,
                '--annotation-status', str(item.get('annotation_status') or 'converted'),
                '--default-source-field', str(item.get('default_source_field') or 'description_text'),
            ]
            if item.get('label_map'):
                cmd.extend(['--label-map', str(item['label_map'])])
            if item.get('id_prefix'):
                cmd.extend(['--id-prefix', str(item['id_prefix'])])
            if item.get('max_records') is not None:
                cmd.extend(['--max-records', str(int(item['max_records']))])
            run_cmd(cmd)
            converted_inputs.append(out_path)

    merge_cmd = [sys.executable, 'automation/legacy_ner/merge_ner_datasets.py']
    for p in args.internal_input:
        merge_cmd.extend(['--input', p])
    for p in converted_inputs:
        merge_cmd.extend(['--input', str(p)])
    merge_cmd.extend([
        '--output', str(merged_path),
        '--min-entities', str(args.min_entities),
        '--require-nonempty-text',
    ])
    run_cmd(merge_cmd)

    split_cmd = [
        sys.executable,
        'automation/legacy_ner/split_ner_dataset.py',
        '--input', str(merged_path),
        '--output-dir', str(split_dir),
        '--train-ratio', str(args.train_ratio),
        '--valid-ratio', str(args.valid_ratio),
        '--test-ratio', str(args.test_ratio),
        '--group-key', args.group_key,
        '--seed', str(args.seed),
    ]
    run_cmd(split_cmd)

    print(f'Merged dataset: {merged_path}')
    print(f'Split directory: {split_dir}')


if __name__ == '__main__':
    main()
