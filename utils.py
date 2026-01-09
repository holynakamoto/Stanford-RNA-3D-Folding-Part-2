"""
Utility functions for RNA 3D structure prediction
"""

import numpy as np
import pandas as pd
import os
import re
from typing import List, Tuple, Dict, Optional


SUBMISSION_COLUMNS = [
    'ID', 'resname', 'resid',
    'x_1', 'y_1', 'z_1', 'x_2', 'y_2', 'z_2',
    'x_3', 'y_3', 'z_3', 'x_4', 'y_4', 'z_4',
    'x_5', 'y_5', 'z_5'
]


def read_test_sequences(file_path: str = "test_sequences.csv") -> pd.DataFrame:
    """
    Read the test sequences CSV file.
    
    Expected format (from competition):
    - target_id: Identifier (e.g., pdb_id_chain_id)
    - sequence: RNA sequence string (concatenated chains)
    - temporal_cutoff: Publication date
    - description: Entry description
    - stoichiometry: Chain information
    - all_sequences: FASTA-formatted sequences
    - ligand_ids: Ligand identifiers
    - ligand_SMILES: Ligand SMILES strings
    
    Returns:
        DataFrame with sequences
    """
    # Try multiple possible paths for Kaggle environment
    possible_paths = [
        file_path,
        f"/kaggle/input/stanford-rna-3d-folding-2/{os.path.basename(file_path)}",
        f"/kaggle/working/{file_path}",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df
    
    raise FileNotFoundError(f"Could not find test_sequences.csv. Tried: {possible_paths}")


def parse_fasta(fasta_string: str) -> Dict[str, str]:
    """
    Parse FASTA-formatted string into a dictionary of chain:sequence.
    
    This replicates the functionality of extra/parse_fasta_py.py
    
    Args:
        fasta_string: FASTA-formatted string with headers and sequences
    
    Returns:
        Dictionary mapping chain IDs to sequences
    """
    chains = {}
    current_header = None
    current_sequence = []
    
    for line in fasta_string.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('>'):
            # Save previous chain if exists
            if current_header and current_sequence:
                # Extract chain ID from header (look for chain= tag or use header)
                chain_match = re.search(r'chain=([A-Za-z0-9]+)', current_header)
                if chain_match:
                    chain_id = chain_match.group(1)
                else:
                    # Try to extract from header format
                    chain_id = current_header.split()[0] if current_header else 'A'
                chains[chain_id] = ''.join(current_sequence)
            
            current_header = line[1:]  # Remove '>'
            current_sequence = []
        else:
            current_sequence.append(line)
    
    # Save last chain
    if current_header and current_sequence:
        chain_match = re.search(r'chain=([A-Za-z0-9]+)', current_header)
        if chain_match:
            chain_id = chain_match.group(1)
        else:
            chain_id = current_header.split()[0] if current_header else 'A'
        chains[chain_id] = ''.join(current_sequence)
    
    return chains


def generate_submission_template(sequences_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a template submission DataFrame with the correct structure.
    
    Args:
        sequences_df: DataFrame containing test sequences with target_id and sequence columns
    
    Returns:
        Empty DataFrame with correct columns ready for coordinate data
    """
    submission_rows = []
    
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        
        # Create rows for each residue in the sequence
        # ID format: target_id_resid (e.g., "1ABC_A_1", "1ABC_A_2", ...)
        for i, residue in enumerate(sequence, start=1):
            resname = residue.upper()  # A, U, G, C
            
            # ID format: target_id_resid
            submission_id = f"{target_id}_{i}"
            
            # Initialize with zeros (to be replaced with actual predictions)
            submission_row = {
                'ID': submission_id,
                'resname': resname,
                'resid': i,
                'x_1': 0.0, 'y_1': 0.0, 'z_1': 0.0,
                'x_2': 0.0, 'y_2': 0.0, 'z_2': 0.0,
                'x_3': 0.0, 'y_3': 0.0, 'z_3': 0.0,
                'x_4': 0.0, 'y_4': 0.0, 'z_4': 0.0,
                'x_5': 0.0, 'y_5': 0.0, 'z_5': 0.0,
            }
            submission_rows.append(submission_row)
    
    return pd.DataFrame(submission_rows)


def clip_coordinates(coords: np.ndarray) -> np.ndarray:
    """
    Clip coordinates to valid range [-999.999, 9999.999] as required by competition.
    
    Args:
        coords: Array of coordinates (N, 3) or (3,)
    
    Returns:
        Clipped coordinates
    """
    coords = np.clip(coords, -999.999, 9999.999)
    return coords


def save_submission(predictions_df: pd.DataFrame, output_path: str = "submission.csv"):
    """
    Save predictions to submission CSV file.
    
    Args:
        predictions_df: DataFrame with predictions in submission format
        output_path: Path to save the submission file
    """
    # Clip coordinates to valid range before saving
    coord_cols = [col for col in predictions_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    for col in coord_cols:
        predictions_df[col] = clip_coordinates(predictions_df[col].values)
    
    # Create directory if it doesn't exist (for local development)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")
    
    predictions_df.to_csv(output_path, index=False)
    print(f"Submission saved to {output_path}")
    print(f"Shape: {predictions_df.shape}")
    print(f"Columns: {predictions_df.columns.tolist()}")


def read_msa_file(target_id: str, msa_dir: str = "MSA") -> Optional[List[Tuple[str, str]]]:
    """
    Read MSA (Multiple Sequence Alignment) file for a target.
    
    Args:
        target_id: Target identifier
        msa_dir: Directory containing MSA files
    
    Returns:
        List of (header, sequence) tuples, or None if file not found
    """
    # Try multiple possible paths
    possible_paths = [
        os.path.join(msa_dir, f"{target_id}.MSA.fasta"),
        os.path.join("/kaggle/input/stanford-rna-3d-folding-2", msa_dir, f"{target_id}.MSA.fasta"),
        os.path.join("/kaggle/working", msa_dir, f"{target_id}.MSA.fasta"),
    ]
    
    for msa_path in possible_paths:
        if os.path.exists(msa_path):
            alignments = []
            current_header = None
            current_sequence = []
            
            with open(msa_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('>'):
                        if current_header and current_sequence:
                            alignments.append((current_header, ''.join(current_sequence)))
                        current_header = line[1:]
                        current_sequence = []
                    else:
                        current_sequence.append(line)
                
                # Add last alignment
                if current_header and current_sequence:
                    alignments.append((current_header, ''.join(current_sequence)))
            
            return alignments
    
    return None


def validate_submission(submission_df: pd.DataFrame, sequences_df: pd.DataFrame) -> bool:
    """
    Validate that submission has correct format and all sequences are present.
    
    Args:
        submission_df: Submission DataFrame
        sequences_df: Test sequences DataFrame (with target_id and sequence columns)
    
    Returns:
        True if valid, raises error if invalid
    """
    # Check required columns
    required_cols = SUBMISSION_COLUMNS
    missing_cols = [col for col in required_cols if col not in submission_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check coordinate ranges
    coord_cols = [col for col in submission_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    for col in coord_cols:
        min_val = submission_df[col].min()
        max_val = submission_df[col].max()
        if min_val < -999.999 or max_val > 9999.999:
            print(f"Warning: {col} has values outside valid range [-999.999, 9999.999]")
            print(f"  Min: {min_val}, Max: {max_val}")
    
    # Check all sequences have predictions
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        seq_length = len(sequence)
        
        # Check that we have predictions for all residues
        expected_ids = [f"{target_id}_{i}" for i in range(1, seq_length + 1)]
        
        for expected_id in expected_ids:
            seq_rows = submission_df[submission_df['ID'] == expected_id]
            if len(seq_rows) == 0:
                raise ValueError(f"No predictions found for {expected_id}")
            
            # Check that coordinates are not all zeros (basic validation)
            for pred_num in range(1, 6):
                x_col = f'x_{pred_num}'
                y_col = f'y_{pred_num}'
                z_col = f'z_{pred_num}'
                coords = seq_rows[[x_col, y_col, z_col]].values[0]
                if np.allclose(coords, 0):
                    print(f"Warning: Prediction {pred_num} for {expected_id} contains all zeros")
    
    print("Submission validation passed!")
    return True


def center_coordinates(coords: np.ndarray) -> np.ndarray:
    """
    Center coordinates by subtracting the centroid.
    
    Args:
        coords: (L, 3) array
    Returns:
        Centered coords (L, 3)
    """
    centroid = np.mean(coords, axis=0, keepdims=True)
    return coords - centroid


def backbone_distance_stats(coords: np.ndarray) -> Tuple[float, float]:
    """
    Compute mean and std of adjacent residue distances for a conformation.
    Args:
        coords: (L, 3)
    Returns:
        (mean_dist, std_dist)
    """
    if coords.shape[0] < 2:
        return 0.0, 0.0
    diffs = coords[1:] - coords[:-1]
    dists = np.linalg.norm(diffs, axis=1)
    return float(np.mean(dists)), float(np.std(dists))


def build_submission_dataframe(sequences_df: pd.DataFrame, predictions: Dict[str, np.ndarray]) -> pd.DataFrame:
    """
    Build submission DataFrame from predictions.
    
    Args:
        sequences_df: DataFrame with target_id and sequence
        predictions: dict[target_id] -> coords (L, K, 3)
    Returns:
        DataFrame with SUBMISSION_COLUMNS
    """
    rows = []
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        coords = predictions[target_id]  # (L, K, 3)
        L, K, _ = coords.shape
        assert K == 5, f"Expected 5 conformations, got {K} for {target_id}"

        # Post-process per conformation
        proc = np.empty_like(coords)
        for k in range(K):
            c = coords[:, k, :]
            c = center_coordinates(c)
            # optional: no scaling; only center
            proc[:, k, :] = c
            m, s = backbone_distance_stats(c)
            if not (4.0 <= m <= 8.0):
                print(f"Warning: {target_id} conf{k+1} mean backbone dist {m:.2f}Å (std {s:.2f}) outside [4,8]Å")
        
        for i, base in enumerate(sequence, start=1):
            entry = {
                'ID': f"{target_id}_{i}",
                'resname': base.upper(),
                'resid': i,
            }
            for k in range(K):
                entry[f'x_{k+1}'] = float(proc[i-1, k, 0])
                entry[f'y_{k+1}'] = float(proc[i-1, k, 1])
                entry[f'z_{k+1}'] = float(proc[i-1, k, 2])
            rows.append(entry)
    df = pd.DataFrame(rows, columns=SUBMISSION_COLUMNS)
    return df
