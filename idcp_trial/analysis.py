"""Validate matched-task records and summarize coordination time, not total labor."""
import csv
import hashlib
import math
import platform
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from . import __version__

COLUMNS = ("pair_id", "baseline_minutes", "idcp_minutes", "correction_minutes", "idcp_outcome", "evidence_complete")

@dataclass(frozen=True)
class Pair:
    pair_id: str
    baseline_minutes: float
    idcp_minutes: float
    correction_minutes: float
    idcp_outcome: str
    evidence_complete: bool

    @property
    def total_idcp_minutes(self):
        return self.idcp_minutes + self.correction_minutes

def read_pairs(path):
    rows, seen = [], set()
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(COLUMNS):
            raise ValueError("CSV header must be: " + ",".join(COLUMNS))
        for number, record in enumerate(reader, start=2):
            if None in record or any(value is None for value in record.values()):
                raise ValueError(f"Row {number}: wrong number of columns")
            values = {key: value.strip() for key, value in record.items()}
            key = values["pair_id"]
            if not key or key in seen:
                raise ValueError(f"Row {number}: missing or duplicate pair_id")
            seen.add(key)
            try:
                times = [float(values[col]) for col in COLUMNS[1:4]]
            except ValueError as error:
                raise ValueError(f"Row {number}: time must be numeric") from error
            if not all(math.isfinite(value) for value in times) or times[0] <= 0 or times[1] <= 0 or times[2] < 0:
                raise ValueError(f"Row {number}: times must be finite; baseline and IDCP positive, correction nonnegative")
            if values["idcp_outcome"] not in {"accepted", "failed"}:
                raise ValueError(f"Row {number}: outcome must be accepted or failed")
            if values["evidence_complete"] not in {"true", "false"}:
                raise ValueError(f"Row {number}: evidence_complete must be true or false")
            rows.append(Pair(key, *times, values["idcp_outcome"], values["evidence_complete"] == "true"))
    if not rows:
        raise ValueError("CSV must contain at least one matched pair")
    return rows

def summarize(pairs, input_path):
    baseline = median(pair.baseline_minutes for pair in pairs)
    assisted = median(pair.total_idcp_minutes for pair in pairs)
    paired_reductions = [(pair.baseline_minutes - pair.total_idcp_minutes) / pair.baseline_minutes * 100 for pair in pairs]
    return {
        "module_version": __version__,
        "python_version": platform.python_version(),
        "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        "pair_count": len(pairs),
        "baseline_median_minutes": round(baseline, 6),
        "idcp_with_correction_median_minutes": round(assisted, 6),
        "reduction_of_medians_percent": round((baseline - assisted) / baseline * 100, 6),
        "median_paired_reduction_percent": round(median(paired_reductions), 6),
        "accepted_count": sum(pair.idcp_outcome == "accepted" for pair in pairs),
        "failed_count": sum(pair.idcp_outcome == "failed" for pair in pairs),
        "evidence_complete_percent": round(sum(pair.evidence_complete for pair in pairs) / len(pairs) * 100, 6),
        "interpretation": "Descriptive coordination-time comparison; failed tasks remain included. No causal claim, total labor saving or ROI is inferred.",
    }

def svg_chart(pairs):
    from html import escape
    width, row_height = 880, 48
    height = 115 + len(pairs) * row_height
    maximum = max(max(pair.baseline_minutes, pair.total_idcp_minutes) for pair in pairs)
    scale = 540 / maximum
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', '<g font-family="Arial,sans-serif" font-size="14" fill="#222">', '<text x="20" y="25">Matched coordination tasks (minutes; correction time included)</text>', '<rect x="20" y="40" width="15" height="12" fill="#527fa2"/><text x="42" y="51">Baseline</text>', '<rect x="170" y="40" width="15" height="12" fill="#b6673e"/><text x="192" y="51">IDCP + correction</text>']
    for index, pair in enumerate(pairs):
        y = 75 + index * row_height
        elements.extend([f'<text x="20" y="{y+19}">{escape(pair.pair_id)}</text>', f'<rect x="125" y="{y}" width="{pair.baseline_minutes*scale:.3f}" height="16" fill="#527fa2"/>', f'<rect x="125" y="{y+20}" width="{pair.total_idcp_minutes*scale:.3f}" height="16" fill="#b6673e"/>', f'<text x="{135+pair.baseline_minutes*scale:.3f}" y="{y+13}">{pair.baseline_minutes:g}</text>', f'<text x="{135+pair.total_idcp_minutes*scale:.3f}" y="{y+33}">{pair.total_idcp_minutes:g}</text>'])
    elements.append('</g></svg>')
    return "\n".join(elements)
