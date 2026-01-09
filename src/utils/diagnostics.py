"""
Diagnostics utilities for conformational diversity and RMSD checks.

Usage example:

from src.utils.diagnostics import diagnose_conformational_diversity
coords = predictions[target_id]  # shape (L, 5, 3)
coords_list = [coords[:, k, :] for k in range(coords.shape[1])]
diagnose_conformational_diversity(coords_list, target_id=target_id, expected_scales=[0.0, 5.0, 10.0, 15.0, 20.0])
"""

from typing import List, Optional
import numpy as np


def compute_rmsd(a: np.ndarray, b: np.ndarray) -> float:
    """Compute RMSD between two coordinate sets of shape (L, 3)."""
    if a.shape != b.shape:
        raise ValueError(f"RMSD shape mismatch: {a.shape} vs {b.shape}")
    return float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))


def diagnose_conformational_diversity(
    coords_list: List[np.ndarray],
    target_id: str = "sample",
    expected_scales: Optional[List[float]] = None,
    print_pairwise: bool = True,
) -> None:
    """
    Print RMSD diagnostics across a list of conformations.

    Args:
        coords_list: list of 5 arrays, each (L, 3)
        target_id: label for display
        expected_scales: expected RMSD values to base conformation (conf 0)
        print_pairwise: whether to compute and print average pairwise RMSD
    """
    if expected_scales is None:
        expected_scales = [0.0, 5.0, 10.0, 15.0, 20.0]

    k = len(coords_list)
    if k == 0:
        print(f"No conformations provided for {target_id}")
        return

    print(f"\nDiversity diagnostics for {target_id} ({k} conformations)")
    base = coords_list[0]
    rmsds_to_base: List[float] = []
    pairwise: List[float] = []

    for i, conf in enumerate(coords_list):
        rmsd = compute_rmsd(base, conf)
        rmsds_to_base.append(rmsd)
        print(f"  conf {i} → RMSD to base = {rmsd:.3f} Å")
        if print_pairwise:
            for j in range(i):
                pw = compute_rmsd(coords_list[j], conf)
                pairwise.append(pw)

    if print_pairwise and len(pairwise) > 0:
        mean_pairwise = float(np.mean(pairwise))
        print(f"  Average pairwise RMSD (all pairs) = {mean_pairwise:.3f} Å")

    print("  Expected vs Observed RMSD to base:")
    for i, (got, want) in enumerate(zip(rmsds_to_base, expected_scales)):
        if want > 0:
            ratio = got / want
            print(f"    scale {want:4.1f} → observed {got:5.2f} Å (ratio ≈ {ratio:.2f})")
        else:
            print(f"    scale {want:4.1f} → observed {got:5.2f} Å (base)")
