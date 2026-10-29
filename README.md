# IDCP Trial Analysis

A small research tool for Assignment 3, connected to the dissertation topic
**Optimization of Software Development Team Business Processes Using Artificial Intelligence**.
It compares matched coordination tasks before and with the Intelligent Development Context Platform (IDCP).

## Scope and data

The tool measures coordination time: finding task context and checking delivery.
It does not analyze an entire work month, infer causation or calculate financial ROI.
Correction time is included. Failed attempts remain in the comparison.
The eight pairs in `data/example_pairs.csv` are **synthetic demonstration data**, not measured developer results.
Keep private task content, names, tokens and company records out of this public repository.

## Requirements and quick start

Python 3.11 or later. There are no runtime or test dependencies beyond the Python standard library.
Git is needed to clone the repository.

```bash
git clone https://github.com/Jasulan273/idcp-trial-analysis.git
cd idcp-trial-analysis
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows alternative: .venv\Scripts\activate
python -m idcp_trial data/example_pairs.csv --output results
python -m unittest discover -s tests -v
```

The CLI writes `summary.json` and `comparison.svg`. Open the SVG in a browser.
Optional: `python -m pip install -e .` enables the `idcp-trial` command.

The repository includes the input and generated demonstration outputs:

- [Input CSV](data/example_pairs.csv)
- [Calculated summary](results/summary.json)
- [Comparison chart](results/comparison.svg)

These outputs were generated from the synthetic example using Python 3.12.14.
Running the command again replaces them; the recorded Python version reflects your environment.

## Input contract

The CSV must have these columns, in this order:

| Column | Meaning |
| --- | --- |
| pair_id | Unique anonymized ID for a matched pair of comparable tasks |
| baseline_minutes | Positive time before using IDCP |
| idcp_minutes | Positive time using IDCP, excluding corrections |
| correction_minutes | Nonnegative correction/review time |
| idcp_outcome | `accepted` or `failed` |
| evidence_complete | `true` or `false` |

Reject malformed rows, missing columns, duplicate IDs, nonfinite times and unknown labels.
For real trials, predefine comparability, record unsuccessful attempts, and save the task selection rules.

## Calculations

Total IDCP time = IDCP time + correction time.
Reduction of medians = (median baseline - median total IDCP) / median baseline * 100.
Median paired reduction = median of each pair's percentage reduction.
These measures differ; both are reported with explicit names.
Evidence completeness is the share of records with `true` in `evidence_complete`.

The example yields baseline median **27 minutes**, IDCP median including corrections **23 minutes**,
reduction of medians **14.814815%**, two failed attempts and **87.5%** evidence completeness.
The summary stores the exact input SHA-256, Python version and module version.
It contains no timestamps or absolute input paths. The chart escapes input labels.

## Organization and technology choices

- `idcp_trial/analysis.py`: input validation, calculation and SVG generation.
- `idcp_trial/__main__.py`: command-line interface and output files.
- `tests/`: automated unit and CLI tests.
- `data/`: public synthetic example.
- `.github/workflows/ci.yml`: CI tests and delivery workflow.

Python suits CSV-based research data. `csv`, `statistics`, `json`, `hashlib` and `unittest`
provide the needed operations without dependency setup. Direct SVG output keeps the visualization portable.
Pandas and Matplotlib would be useful for larger datasets or richer plots, but are unnecessary here.

## Git and collaboration

Use a short feature branch, make focused commits, open a pull request and review the tests before merging.
Track bugs and improvements in GitHub Issues. This repository includes an issue template,
a license and contributor instructions. A release tag identifies the exact delivered source version.

## CI and delivery

The [workflow](.github/workflows/ci.yml) runs on pushes to `main`, pull requests, version tags and manual dispatch.
It tests Python 3.11, 3.12 and 3.13, compiles the module, runs the example and uploads generated results.
For a maintainer-created `v*` tag, a job waits for all tests to pass, packages the source and publishes a GitHub release.
Normal tests have read-only permissions; the release job has repository write access.
This is delivery of a versioned research tool, not a hosted web application deployment.

## Limits and next work

Matched tasks must be selected by the researcher; the program cannot verify their comparability.
Small samples do not establish a general productivity effect. Training, order effects and task difficulty
can confound a before/after comparison. Real data collection, confidence intervals and IDCP export integration
are future work and are not represented as implemented features.

## Assignment 5 Docker and Jenkins

The research analysis remains separate from the IDCP platform. Assignment 5 adds
a containerized execution environment and an actual local Jenkins pipeline.
See [setup and limits](jenkins/README.md), [Dockerfile](Dockerfile) and [Jenkinsfile](Jenkinsfile).
Actual screenshots, the successful SCM-triggered build log and generated outputs
are retained in [Assignment 5 evidence](docs/assignment5/README.md).

```sh
docker build --target test -t idcp-trial-analysis:test .
docker run --rm --network none idcp-trial-analysis:test
docker build -t idcp-trial-analysis:local .
docker run --rm --network none idcp-trial-analysis:local
```

The example still uses synthetic data. A successful pipeline verifies software
execution; it does not demonstrate a real productivity improvement.

## License
MIT. See [LICENSE](LICENSE).
