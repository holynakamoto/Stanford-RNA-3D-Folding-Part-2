"""
Data Preprocessing Pipeline
===========================

Handles:
1. Loading competition data
2. MSA feature extraction
3. Sequence encoding
4. Creating training batches
5. Caching processed features
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pickle
import gzip
from dataclasses import dataclass
import re
import os


@dataclass
class RNASequence:
    """Represents an RNA sequence with metadata"""
    id: str
    sequence: str
    structure: Optional[np.ndarray] = None  # Shape: (L, num_atoms, 3) or (L, num_confs, 3)
    msa: Optional[np.ndarray] = None  # Shape: (num_seqs, L)
    length: int = 0
    
    def __post_init__(self):
        self.length = len(self.sequence)


class DataLoader:
    """Loads and processes competition data"""
    
    def __init__(self, cache_dir: Path = Path("cache")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def load_sequences_csv(self, path: Path) -> pd.DataFrame:
        """Load sequences CSV file"""
        if not path.exists():
            raise FileNotFoundError(f"Sequences file not found: {path}")
        
        df = pd.read_csv(path)
        print(f"📊 Loaded sequences from {path}")
        print(f"  - Total sequences: {len(df)}")
        print(f"  - Columns: {df.columns.tolist()}")
        
        return df
    
    def load_labels_csv(self, path: Path) -> pd.DataFrame:
        """Load labels CSV file with structures"""
        if not path.exists():
            raise FileNotFoundError(f"Labels file not found: {path}")
        
        df = pd.read_csv(path)
        print(f"📊 Loaded labels from {path}")
        print(f"  - Total residues: {len(df)}")
        print(f"  - Unique sequences: {df['ID'].str.split('_').str[0].nunique()}")
        
        return df
    
    def load_submission_format(self, path: Path) -> Tuple[pd.DataFrame, Dict[str, RNASequence]]:
        """Load and understand submission format"""
        df = pd.read_csv(path)
        print(f"📊 Submission format:")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Columns: {df.columns.tolist()}")
        print(f"  - Unique sequences: {df['ID'].str.split('_').str[0].nunique()}")
        
        # Parse structure
        sequences = self._parse_submission(df)
        print(f"  - Parsed {len(sequences)} unique sequences")
        
        return df, sequences
    
    def _parse_submission(self, df: pd.DataFrame) -> Dict[str, RNASequence]:
        """Parse submission CSV into RNASequence objects"""
        sequences = {}
        
        # Group by sequence ID (target_id)
        seq_ids = df['ID'].str.split('_').str[0].unique()
        
        for seq_id in seq_ids:
            # Get all residues for this sequence
            seq_mask = df['ID'].str.startswith(f"{seq_id}_")
            seq_data = df[seq_mask].sort_values('resid')
            
            # Extract sequence
            sequence_str = ''.join(seq_data['resname'].values)
            
            # Extract coordinates (5 conformations per residue)
            coords = []
            for _, row in seq_data.iterrows():
                # Each row has x_1,y_1,z_1 through x_5,y_5,z_5
                residue_coords = []
                for conf_idx in range(1, 6):
                    x = row[f'x_{conf_idx}']
                    y = row[f'y_{conf_idx}']
                    z = row[f'z_{conf_idx}']
                    residue_coords.append([x, y, z])
                coords.append(residue_coords)
            
            coords = np.array(coords, dtype=np.float32)  # Shape: (L, 5, 3)
            
            sequences[seq_id] = RNASequence(
                id=seq_id,
                sequence=sequence_str,
                structure=coords,
            )
        
        return sequences
    
    def parse_labels_csv(self, labels_df: pd.DataFrame) -> Dict[str, RNASequence]:
        """Parse labels CSV into RNASequence objects with structures"""
        sequences = {}
        
        # Group by sequence ID
        seq_ids = labels_df['ID'].str.split('_').str[0].unique()
        
        for seq_id in seq_ids:
            seq_mask = labels_df['ID'].str.startswith(f"{seq_id}_")
            seq_data = labels_df[seq_mask].sort_values('resid')
            
            # Extract sequence
            sequence_str = ''.join(seq_data['resname'].values)
            
            # Extract coordinates - labels may have multiple conformations
            coord_cols = [col for col in seq_data.columns if col.startswith(('x_', 'y_', 'z_'))]
            n_confs = len([c for c in coord_cols if c.startswith('x_')])
            
            coords = []
            for _, row in seq_data.iterrows():
                residue_coords = []
                for conf_idx in range(1, n_confs + 1):
                    x = row[f'x_{conf_idx}']
                    y = row[f'y_{conf_idx}']
                    z = row[f'z_{conf_idx}']
                    residue_coords.append([x, y, z])
                coords.append(residue_coords)
            
            coords = np.array(coords, dtype=np.float32)  # Shape: (L, n_confs, 3)
            
            sequences[seq_id] = RNASequence(
                id=seq_id,
                sequence=sequence_str,
                structure=coords,
            )
        
        return sequences
    
    def analyze_data_statistics(self, sequences: Dict[str, RNASequence]):
        """Analyze dataset statistics"""
        lengths = [seq.length for seq in sequences.values()]
        
        print("\n📈 Dataset Statistics:")
        print(f"  Number of sequences: {len(sequences)}")
        print(f"  Length distribution:")
        print(f"    - Min: {min(lengths)}")
        print(f"    - Max: {max(lengths)}")
        print(f"    - Mean: {np.mean(lengths):.1f}")
        print(f"    - Median: {np.median(lengths):.1f}")
        
        # Base composition
        all_bases = ''.join([seq.sequence for seq in sequences.values()])
        base_counts = {base: all_bases.count(base) for base in 'AUGC'}
        total = sum(base_counts.values())
        
        print(f"  Base composition:")
        for base, count in sorted(base_counts.items()):
            print(f"    - {base}: {count:>6} ({100*count/total:.1f}%)")
        
        # Structure analysis
        if sequences and list(sequences.values())[0].structure is not None:
            self._analyze_structures(sequences)
    
    def _analyze_structures(self, sequences: Dict[str, RNASequence]):
        """Analyze structural properties"""
        all_distances = []
        
        for seq in list(sequences.values())[:100]:  # Sample for speed
            if seq.structure is not None:
                # Calculate inter-residue distances (first conformation only)
                coords = seq.structure[:, 0, :]  # Shape: (L, 3)
                
                # Calculate consecutive residue distances
                for i in range(len(coords) - 1):
                    dist = np.linalg.norm(coords[i+1] - coords[i])
                    all_distances.append(dist)
        
        if all_distances:
            all_distances = np.array(all_distances)
            print(f"  Structural properties:")
            print(f"    - Inter-residue distance (mean): {np.mean(all_distances):.2f} Å")
            print(f"    - Inter-residue distance (std): {np.std(all_distances):.2f} Å")
            print(f"    - Inter-residue distance (range): [{np.min(all_distances):.2f}, {np.max(all_distances):.2f}] Å")


class FeatureExtractor:
    """Extract features for model input"""
    
    def __init__(self):
        self.base_to_idx = {'A': 0, 'U': 1, 'G': 2, 'C': 3}
        
    def encode_sequence(self, sequence: str) -> np.ndarray:
        """One-hot encode RNA sequence"""
        encoded = np.zeros((len(sequence), 4), dtype=np.float32)
        for i, base in enumerate(sequence):
            if base in self.base_to_idx:
                encoded[i, self.base_to_idx[base]] = 1.0
        
        return encoded
    
    def extract_position_encoding(self, length: int, dim: int = 128) -> np.ndarray:
        """Sinusoidal position encoding"""
        position = np.arange(length)[:, np.newaxis]
        div_term = np.exp(np.arange(0, dim, 2) * -(np.log(10000.0) / dim))
        
        pe = np.zeros((length, dim), dtype=np.float32)
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        
        return pe
    
    def create_distance_matrix(self, coords: np.ndarray) -> np.ndarray:
        """Create pairwise distance matrix from coordinates"""
        # coords shape: (L, 3)
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff**2, axis=-1))
        return distances
    
    def extract_all_features(self, sequence: RNASequence) -> Dict[str, np.ndarray]:
        """Extract all features for a sequence"""
        features = {
            'sequence_encoding': self.encode_sequence(sequence.sequence),
            'position_encoding': self.extract_position_encoding(sequence.length),
            'length': sequence.length,
            'id': sequence.id,
            'sequence': sequence.sequence,  # Keep original sequence
        }
        
        if sequence.structure is not None:
            # Use first conformation as reference
            coords = sequence.structure[:, 0, :]
            features['distance_matrix'] = self.create_distance_matrix(coords)
            features['coordinates'] = coords
        
        return features


class DataPipeline:
    """Complete data processing pipeline"""
    
    def __init__(self, cache_dir: Path = Path("cache")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loader = DataLoader(cache_dir)
        self.feature_extractor = FeatureExtractor()
        
    def process_submission_data(self, submission_path: Path):
        """Process the submission file to understand format"""
        print("🔄 Processing submission data...")
        
        df, sequences = self.loader.load_submission_format(submission_path)
        self.loader.analyze_data_statistics(sequences)
        
        return df, sequences
    
    def process_training_data(self, sequences_path: Path, labels_path: Path):
        """Process training data from competition files"""
        print("🔄 Processing training data...")
        
        # Load sequences
        seqs_df = self.loader.load_sequences_csv(sequences_path)
        
        # Load labels
        labels_df = self.loader.load_labels_csv(labels_path)
        
        # Parse into sequences
        sequences = self.loader.parse_labels_csv(labels_df)
        
        self.loader.analyze_data_statistics(sequences)
        
        return sequences
    
    def prepare_training_data(self, sequences: Dict[str, RNASequence]):
        """Prepare features for training"""
        print("\n🔄 Preparing training features...")
        
        features_list = []
        for seq_id, seq in sequences.items():
            features = self.feature_extractor.extract_all_features(seq)
            features_list.append(features)
            
            if len(features_list) % 100 == 0:
                print(f"  Processed {len(features_list)}/{len(sequences)} sequences")
        
        print(f"✅ Prepared features for {len(features_list)} sequences")
        return features_list
    
    def save_features(self, features: List[Dict], path: Path):
        """Save processed features"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with gzip.open(path, 'wb') as f:
            pickle.dump(features, f)
        print(f"💾 Saved features to {path}")
    
    def load_features(self, path: Path) -> List[Dict]:
        """Load processed features"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Features file not found: {path}")
        
        with gzip.open(path, 'rb') as f:
            features = pickle.load(f)
        print(f"📂 Loaded features from {path}")
        return features


def main():
    """Test the data pipeline"""
    from pathlib import Path
    
    # Initialize pipeline
    pipeline = DataPipeline(cache_dir=Path("cache"))
    
    # Test with current submission file
    submission_path = Path("submission.csv")
    if submission_path.exists():
        print("=" * 60)
        print("Testing with submission.csv")
        print("=" * 60)
        
        # Process submission data
        df, sequences = pipeline.process_submission_data(submission_path)
        
        # Prepare features
        features = pipeline.prepare_training_data(sequences)
        
        # Show sample features
        print("\n📋 Sample feature shapes:")
        for key, value in features[0].items():
            if isinstance(value, np.ndarray):
                print(f"  {key}: {value.shape}")
            else:
                print(f"  {key}: {type(value)}")
        
        return sequences, features
    else:
        print(f"⚠️  {submission_path} not found. Cannot test pipeline.")
        print("Expected files:")
        print("  - data/raw/train_sequences.csv")
        print("  - data/raw/train_labels.csv")
        print("  - submission.csv (for testing)")
        return None, None


if __name__ == "__main__":
    sequences, features = main()
