# Training Data Audit Report

## Dataset Overview

| Metric | Value |
|--------|-------|
| Total examples | 1342 |
| Total entities | 422 |
| Total relations | 408 |
| Total facts | 944 |
| Empty outputs | 398 (29%) |
| Total issues found | 86 |

## Per-file Summary

| File | Examples | Issues |
|------|----------|--------|
| s1_v4_full_training.jsonl | 604 | 38 |
| s1_v4_full_validation.jsonl | 67 | 5 |
| v4_g1_json_discipline.jsonl | 150 | 4 |
| v4_g2_numeric_facts.jsonl | 120 | 0 |
| v4_g3_empty_output.jsonl | 89 | 39 |
| v4_g4_relations.jsonl | 102 | 0 |
| v4_g5_topic_changes.jsonl | 60 | 0 |
| v4_g6_dedup_corrections.jsonl | 60 | 0 |
| v4_g7_multi_entity.jsonl | 30 | 0 |
| v4_g8_intent_balance.jsonl | 60 | 0 |

## Entity Type Distribution

| Type | Count |
|------|-------|
| technology | 144 |
| person | 126 |
| concept | 64 |
| project | 62 |
| document | 16 |
| event | 10 |

## Relation Distribution

| Relation | Count |
|----------|-------|
| uses_technology | 100 |
| maintains | 92 |
| part_of | 48 |
| deployed_on | 36 |
| located_in | 30 |
| works_at | 20 |
| created_by | 14 |
| member_of | 12 |
| serves | 10 |
| depends_on | 10 |
| documented_in | 8 |
| alternative_to | 6 |
| resulted_in | 6 |
| produces | 6 |
| participated_in | 6 |
| triggered_by | 4 |

## Intent Distribution

| Intent | Count |
|--------|-------|
| specific | 1058 |
| chat | 218 |
| overview | 36 |
| followup | 30 |

## Topic Action Distribution

| Action | Count |
|--------|-------|
| same | 1206 |
| changed | 96 |
| subtopic | 40 |

## Issues by Category

| Category | Count |
|----------|-------|
| MISSING_FIELD | 84 |
| MISSING_EXISTING_ID | 2 |

## Detailed Issues

### MISSING_FIELD (84 issues)

- `s1_v4_full_training.jsonl:47` -- topic.label is empty
- `s1_v4_full_training.jsonl:57` -- topic.label is empty
- `s1_v4_full_training.jsonl:66` -- topic.label is empty
- `s1_v4_full_training.jsonl:89` -- topic.label is empty
- `s1_v4_full_training.jsonl:100` -- topic.label is empty
- `s1_v4_full_training.jsonl:110` -- topic.label is empty
- `s1_v4_full_training.jsonl:145` -- topic.label is empty
- `s1_v4_full_training.jsonl:146` -- topic.label is empty
- `s1_v4_full_training.jsonl:213` -- topic.label is empty
- `s1_v4_full_training.jsonl:224` -- topic.label is empty
- `s1_v4_full_training.jsonl:225` -- topic.label is empty
- `s1_v4_full_training.jsonl:266` -- topic.label is empty
- `s1_v4_full_training.jsonl:279` -- topic.label is empty
- `s1_v4_full_training.jsonl:297` -- topic.label is empty
- `s1_v4_full_training.jsonl:314` -- topic.label is empty
- `s1_v4_full_training.jsonl:316` -- topic.label is empty
- `s1_v4_full_training.jsonl:329` -- topic.label is empty
- `s1_v4_full_training.jsonl:344` -- topic.label is empty
- `s1_v4_full_training.jsonl:352` -- topic.label is empty
- `s1_v4_full_training.jsonl:355` -- topic.label is empty
- ... and 64 more

### MISSING_EXISTING_ID (2 issues)

- `s1_v4_full_training.jsonl:318` -- Entity 'svelte' matches existing node but existing_id is null
- `v4_g1_json_discipline.jsonl:19` -- Entity 'svelte' matches existing node but existing_id is null

