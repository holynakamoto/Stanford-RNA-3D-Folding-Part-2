"""
MSA (Multiple Sequence Alignment) loading and processing
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import re
import os


def read_msa_file(msa_path: Path) -> Optional[List[Tuple[str, str]]]:
    """
    Read MSA file in FASTA format.
    
    Args:
        msa_path: Path to MSA file
    
    Returns:
        List of (header, sequence) tuples, or None if file not found
    """
    if not msa_path.exists():
        return None
    
    alignments = []
    current_header = None
    current_sequence = []
    
    with open(msa_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('>'):
                # Save previous alignment
                if current_header and current_sequence:
                    alignments.append((current_header, ''.join(current_sequence)))
                
                current_header = line[1:]  # Remove '>'
                current_sequence = []
            else:
                current_sequence.append(line)
        
        # Save last alignment
        if current_header and current_sequence:
            alignments.append((current_header, ''.join(current_sequence)))
    
    return alignments


def parse_msa_header(header: str) -> Dict[str, str]:
    """
    Parse MSA header to extract metadata.
    
    Headers have format like:
    "source|chain=A|copies=1"
    
    Args:
        header: MSA header string
    
    Returns:
        Dictionary with parsed metadata
    """
    metadata = {}
    
    # Split by |
    parts = header.split('|')
    metadata['source'] = parts[0] if parts else ''
    
    # Parse key=value pairs
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            metadata[key] = value
    
    return metadata


def msa_to_array(alignments: List[Tuple[str, str]], max_seqs: Optional[int] = None) -> np.ndarray:
    """
    Convert MSA alignments to numpy array.
    
    Args:
        alignments: List of (header, sequence) tuples
        max_seqs: Maximum number of sequences to include (None for all)
    
    Returns:
        Array of shape (num_seqs, seq_length) with character codes
    """
    if not alignments:
        return np.array([])
    
    # Get alignment length (assuming all sequences have same length)
    seq_length = len(alignments[0][1])
    
    # Limit number of sequences
    if max_seqs:
        alignments = alignments[:max_seqs]
    
    # Convert to array
    msa_array = np.zeros((len(alignments), seq_length), dtype=np.int8)
    
    # Base to index mapping
    base_to_idx = {'A': 0, 'U': 1, 'G': 2, 'C': 3, '-': 4, 'N': 5}
    
    for i, (header, sequence) in enumerate(alignments):
        for j, char in enumerate(sequence):
            msa_array[i, j] = base_to_idx.get(char.upper(), 5)
    
    return msa_array


def extract_msa_features(msa_array: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Extract features from MSA array.
    
    Args:
        msa_array: MSA array of shape (num_seqs, seq_length)
    
    Returns:
        Dictionary of extracted features
    """
    features = {}
    
    # Conservation score (entropy at each position)
    # Higher entropy = less conserved
    num_seqs = msa_array.shape[0]
    seq_length = msa_array.shape[1]
    
    conservation = np.zeros(seq_length)
    
    for pos in range(seq_length):
        # Count base frequencies at this position
        unique, counts = np.unique(msa_array[:, pos], return_counts=True)
        # Exclude gaps (index 4)
        mask = unique != 4
        if np.any(mask):
            counts = counts[mask]
            probs = counts / counts.sum()
            # Shannon entropy
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            conservation[pos] = 1 - entropy / np.log(4)  # Normalize to [0, 1]
    
    features['conservation'] = conservation
    
    # Gap frequency at each position
    gap_freq = np.mean(msa_array == 4, axis=0)
    features['gap_frequency'] = gap_freq
    
    return features


def load_msa_for_target(target_id: str, msa_dir: Path = Path("data/msa")) -> Optional[np.ndarray]:
    """
    Load MSA for a specific target.
    
    Args:
        target_id: Target identifier
        msa_dir: Directory containing MSA files
    
    Returns:
        MSA array or None if not found
    """
    msa_paths = [
        msa_dir / f"{target_id}.MSA.fasta",
        Path(f"MSA/{target_id}.MSA.fasta"),
        Path(f"/kaggle/input/stanford-rna-3d-folding-2/MSA/{target_id}.MSA.fasta"),
    ]
    
    for msa_path in msa_paths:
        if msa_path.exists():
            alignments = read_msa_file(msa_path)
            if alignments:
                return msa_to_array(alignments)
    
    return None
