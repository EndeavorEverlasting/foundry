# SysAdminSuite Mainline Promotion Insights

Date: 2026-05-26
Source workflow: SysAdminSuite Live Serial Probe V1 promotion
Visibility: public-safe, no operational hostnames, serials, MACs, users, rooms, departments, or generated field artifacts

## Why This Note Exists

This note captures promotion lessons from a SysAdminSuite workflow where reviewed logic was moved from quarantine/archive branches into a clean product branch based on current `origin/main`.

The key lesson is simple: active product work must converge on main. Archive branches may preserve history, but they should not become product lanes.

## Branch Doctrine

Use this branch posture model:

```text
origin/main
  -> fresh product branch
  -> selectively promoted reviewed files
  -> offline tests
  -> local generated outputs removed
  -> PR back to main
```

Avoid this pattern for active product work:

```text
old divergent feature branch
  -> merge current main into it
  -> continue product work there
```

That approach can preserve too much stale branch sediment. It is useful for forensics, not clean promotion.

## Archive vs Product Branches

| Branch Type | Allowed to Diverge? | Purpose |
| --- | --- | --- |
| Archive / quarantine | Yes | Preserve prior work, branch deltas, experiments, and recovery material. |
| Analysis / forensics | Yes, within reason | Record conclusions and rejected approaches. |
| Active product branch | No | Carry a small reviewed payload from current `origin/main` toward PR. |
| Release branch | No | Stabilize a known target, not accumulate unrelated branch history. |

## Promotion Rules

1. Cut a fresh branch from current `origin/main` for active product promotion.
2. Copy only reviewed files from archive, quarantine, or old feature branches.
3. Do not merge quarantine branches wholesale.
4. Do not promote generated CSV, HTML, XLSX, logs, or screenshots containing real operational data.
5. Run offline tests before live or field behavior is trusted.
6. Remove generated outputs before commit.
7. Confirm the branch is ahead of main and behind by zero before PR.

## Concrete Pattern Observed

The successful SysAdminSuite Live Serial Probe V1 promotion ended with:

- one clean product commit on top of current `origin/main`
- no generated output committed
- sanitized fixtures only
- public-safe documentation language only
- no real hostnames, serials, MACs, users, rooms, departments, or locations
- branch ready for PR into main

The useful verification commands were:

```bash
git status --short --branch
git log --oneline --decorate --max-count=8
git diff --name-status origin/main..HEAD
git diff --cached --check
```

Public-safety grep pattern used before commit:

```bash
grep -RInE "WMH|WNH|W[A-Z]{2}[0-9]{3}OPR|MEDNM|MEDSG|Northwell|Marcus|LIJ|NSUH" \
  <reviewed-files> || true
```

The grep may return policy language such as warnings not to commit real data. That is acceptable. It must not return real hostnames, serials, MACs, rooms, departments, users, or generated field artifacts.

## Evidence Lane Lesson

Ping is only one witness. It must not be the judge.

A future evidence model should preserve distinct paths such as:

- ping reachable
- DNS only / no ping
- nmap observed / no ping
- identity observed / no ping
- offline fixture
- unreachable or filtered
- manual review for conflicts

Flattening all non-ping cases into `unreachable` destroys useful operational evidence.

## Foundry Product Implication

Foundry should make this visible as branch intelligence, not tribal memory.

Useful Foundry concepts to model:

- `archive_branch`
- `active_product_branch`
- `mainline_convergent`
- `divergent_source_branch`
- `promotion_payload`
- `generated_artifact_risk`
- `public_safe_fixture`
- `offline_test_required`
- `evidence_path_preserved`

A branch should be treated as PR-ready only when:

- it is based on current main or behind by zero
- its payload is small and explainable
- generated artifacts are absent
- public-safety checks pass
- tests relevant to the promoted payload pass

## Short Rule

Archive branches can be museums.

Product branches must be roads.
