#!/usr/bin/env python3
"""
Quick test script to validate conformational diversity and RMSD.
Run this to check your model generates diverse conformations before submitting to Kaggle.

Usage:
    python test_diversity.py                    # Test with sample sequences
    python test_diversity.py --verbose          # Show detailed output
    python test_diversity.py --length 100       # Test with specific sequence length
"""

import sys
from pathlib import Path
import numpy as np
import argparse

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.modeling.rna_model import RNAStructureModel
from src.utils.diagnostics import diagnose_conformational_diversity, compute_rmsd


def create_test_sequence(length: int = 50, base_type: str = "random") -> str:
    """Create a test RNA sequence"""
    if base_type == "random":
        bases = ['A', 'U', 'G', 'C']
        rng = np.random.default_rng(42)
        return ''.join(rng.choice(bases, size=length))
    elif base_type == "simple":
        # Simple repeating pattern
        pattern = "GGCGUAGUCC"
        return (pattern * (length // len(pattern) + 1))[:length]
    else:
        raise ValueError(f"Unknown base_type: {base_type}")


def test_conformational_diversity(config=None, verbose: bool = False):
    """Test that the model generates diverse conformations"""
    if config is None:
        config = get_config()
    
    print("\n" + "="*70)
    print("CONFORMATIONAL DIVERSITY TEST")
    print("="*70)
    print(f"Configuration:")
    print(f"  - Noise scales: {config.noise_scales}")
    print(f"  - Max refinement steps: {config.max_refinement_steps}")
    print(f"  - Num conformations: {config.num_conformations}")
    print("="*70 + "\n")
    
    # Create model
    model = RNAStructureModel(config)
    
    # Test sequences of different lengths
    test_cases = [
        ("Short (10nt)", create_test_sequence(10, "simple")),
        ("Medium (50nt)", create_test_sequence(50, "random")),
        ("Long (100nt)", create_test_sequence(100, "random")),
    ]
    
    all_passed = True
    
    for name, sequence in test_cases:
        print(f"\n{'─'*70}")
        print(f"Test case: {name}")
        print(f"Sequence: {sequence[:30]}{'...' if len(sequence) > 30 else ''}")
        print(f"Length: {len(sequence)} residues")
        print(f"{'─'*70}")
        
        # Predict structure
        coords = model.predict(sequence)  # (L, K, 3)
        
        # Convert to list of conformations
        coords_list = [coords[:, k, :] for k in range(coords.shape[1])]
        
        # Run diagnostics
        diagnose_conformational_diversity(
            coords_list,
            target_id=name,
            expected_scales=config.noise_scales,
            print_pairwise=True
        )
        
        # Check if diversity is sufficient
        base = coords_list[0]
        rmsds = [compute_rmsd(base, coords_list[i]) for i in range(len(coords_list))]
        
        # Expected RMSDs should increase roughly linearly with noise scales
        # Allow some tolerance (ratio between 0.5 and 2.0)
        passed = True
        for i, (rmsd, expected) in enumerate(zip(rmsds, config.noise_scales)):
            if expected > 0:
                ratio = rmsd / expected
                if not (0.5 <= ratio <= 2.0):
                    print(f"  ⚠️  RMSD ratio out of range for conf {i}: {ratio:.2f}")
                    passed = False
        
        # Check average pairwise RMSD
        pairwise_rmsds = []
        for i in range(len(coords_list)):
            for j in range(i+1, len(coords_list)):
                pairwise_rmsds.append(compute_rmsd(coords_list[i], coords_list[j]))
        
        avg_pairwise = np.mean(pairwise_rmsds)
        
        # For good diversity, average pairwise should be > 10Å
        if avg_pairwise < 10.0:
            print(f"  ⚠️  Low average pairwise RMSD: {avg_pairwise:.2f}Å (expected > 10Å)")
            passed = False
        
        if passed:
            print(f"\n  ✅ {name} PASSED - Good conformational diversity!")
        else:
            print(f"\n  ❌ {name} FAILED - Insufficient diversity")
            all_passed = False
        
        if verbose:
            print(f"\n  Detailed statistics:")
            print(f"    - Coordinate range: [{coords.min():.2f}, {coords.max():.2f}]")
            print(f"    - Mean coordinate: {coords.mean():.2f}")
            print(f"    - Std coordinate: {coords.std():.2f}")
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Model generates diverse conformations!")
        print("="*70 + "\n")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check configuration and model")
        print("="*70 + "\n")
        print("Troubleshooting tips:")
        print("  1. Check config.noise_scales in src/config.py")
        print("  2. Verify centering is disabled in build_submission_dataframe")
        print("  3. Ensure max_refinement_steps = 0 in config")
        print("  4. Check that fresh noise is generated per conformation")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Test conformational diversity")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--length", type=int, default=50, help="Test sequence length")
    args = parser.parse_args()
    
    # Get config
    config = get_config()
    
    # Run tests
    exit_code = test_conformational_diversity(config, verbose=args.verbose)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
