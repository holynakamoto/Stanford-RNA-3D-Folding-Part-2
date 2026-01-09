"""
Inference code for RNA structure prediction
"""

import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import sys
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modeling.rna_model import RNAStructureModel, GeometricRefiner
from src.preprocessing.data_pipeline import FeatureExtractor
from src.preprocessing.load_msa import load_msa_for_target, msa_to_array, read_msa_file
from src.config import get_config


class RNASequencePredictor:
    """Predict RNA structures from sequences"""
    
    def __init__(self, config=None):
        if config is None:
            config = get_config()
        self.config = config
        
        # Initialize model
        self.model = RNAStructureModel(config)
        self.refiner = GeometricRefiner(config) if config.max_refinement_steps > 0 else None
        self.feature_extractor = FeatureExtractor()
    
    def predict_sequence(
        self,
        sequence: str,
        target_id: str,
        msa_dir: Optional[Path] = None,
        refine: bool = True
    ) -> np.ndarray:
        """
        Predict structure for a single sequence.
        
        Args:
            sequence: RNA sequence string
            target_id: Target identifier (for MSA lookup)
            msa_dir: Directory containing MSA files
            refine: Whether to apply geometric refinement
        
        Returns:
            coordinates: 3D coordinates (seq_len, num_conformations, 3)
        """
        # Encode sequence
        seq_encoding = self.feature_extractor.encode_sequence(sequence)
        seq_batch = seq_encoding[np.newaxis, :, :]  # Add batch dimension
        
        # Try to load MSA if enabled
        msa_batch = None
        if self.config.use_msa:
            if msa_dir is None:
                msa_dir = self.config.msa_dir
            
            msa_array = load_msa_for_target(target_id, msa_dir)
            if msa_array is not None:
                # Convert to one-hot for MSA transformer
                num_seqs, seq_len = msa_array.shape
                msa_onehot = np.zeros((num_seqs, seq_len, 5), dtype=np.float32)
                base_to_idx = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}  # Map N to gap
                for i in range(num_seqs):
                    for j in range(seq_len):
                        base_idx = int(msa_array[i, j])
                        if base_idx < 5:
                            msa_onehot[i, j, base_idx] = 1.0
                
                msa_batch = msa_onehot[np.newaxis, :, :, :]  # Add batch dimension
        
        # Create deterministic per-target RNG for diverse conformations
        seed = int.from_bytes(hashlib.md5(target_id.encode('utf-8')).digest()[:8], 'little')
        rng = np.random.default_rng(seed)
        
        # Predict structure
        coords_batch = self.model.forward(seq_batch, msa_batch, rng=rng)
        coords = coords_batch[0]  # Remove batch dimension: (seq_len, num_confs, 3)
        
        # Refine if requested
        if refine and self.refiner is not None:
            refined_coords = np.zeros_like(coords)
            for conf_idx in range(self.config.num_conformations):
                refined = self.refiner.refine(coords[:, conf_idx, :], sequence)
                refined_coords[:, conf_idx, :] = refined
            coords = refined_coords
        
        return coords
    
    def predict_batch(
        self,
        sequences: List[str],
        target_ids: List[str],
        msa_dir: Optional[Path] = None,
        refine: bool = True
    ) -> List[np.ndarray]:
        """
        Predict structures for multiple sequences.
        
        Args:
            sequences: List of RNA sequence strings
            target_ids: List of target identifiers
            msa_dir: Directory containing MSA files
            refine: Whether to apply geometric refinement
        
        Returns:
            List of coordinate arrays, each shape (seq_len, num_conformations, 3)
        """
        predictions = []
        
        for seq, target_id in zip(sequences, target_ids):
            coords = self.predict_sequence(seq, target_id, msa_dir, refine)
            predictions.append(coords)
        
        return predictions


def predict_from_dataframe(
    sequences_df,
    config=None,
    msa_dir: Optional[Path] = None
) -> Dict[str, np.ndarray]:
    """
    Predict structures from sequences DataFrame.
    
    Args:
        sequences_df: DataFrame with 'target_id' and 'sequence' columns
        config: Configuration object
        msa_dir: Directory containing MSA files
    
    Returns:
        Dictionary mapping target_id to coordinates
    """
    if config is None:
        config = get_config()
    
    predictor = RNASequencePredictor(config)
    predictions = {}
    
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        
        print(f"Predicting {target_id}: {len(sequence)} residues")
        
        coords = predictor.predict_sequence(sequence, target_id, msa_dir)
        predictions[target_id] = coords
    
    return predictions


if __name__ == "__main__":
    # Test prediction
    config = get_config()
    predictor = RNASequencePredictor(config)
    
    test_sequence = "GGCGUAGUCC"
    test_target_id = "test_1"
    
    print(f"Testing prediction for: {test_sequence}")
    coords = predictor.predict_sequence(test_sequence, test_target_id, refine=False)
    
    print(f"✅ Prediction successful!")
    print(f"  - Shape: {coords.shape}")
    print(f"  - Expected: ({len(test_sequence)}, {config.num_conformations}, 3)")
    print(f"  - Coordinate range: [{coords.min():.2f}, {coords.max():.2f}]")
