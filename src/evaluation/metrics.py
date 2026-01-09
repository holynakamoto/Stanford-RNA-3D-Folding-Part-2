"""
Evaluation and Submission System
=================================

1. TM-score calculation (competition metric)
2. Structure quality metrics
3. Submission file generation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TMScoreCalculator:
    """
    Calculate TM-score (Template Modeling score)
    
    TM-score measures structural similarity:
    - Range: [0, 1]
    - >0.5: Same fold
    - >0.7: Nearly identical structures
    """
    
    def __init__(self):
        self.d0_constant = 1.24
        self.d0_scale = 15.0
    
    def calculate(self, pred_coords: np.ndarray, true_coords: np.ndarray) -> float:
        """
        Calculate TM-score between predicted and true structures
        
        Args:
            pred_coords: Predicted coordinates (L, 3)
            true_coords: True coordinates (L, 3)
        
        Returns:
            tm_score: TM-score value [0, 1]
        """
        if len(pred_coords) != len(true_coords):
            raise ValueError("Predicted and true coordinates must have same length")
        
        L = len(pred_coords)
        
        # Calculate d0 normalization factor
        d0 = self._calculate_d0(L)
        
        # Optimal superposition using Kabsch algorithm
        pred_aligned, true_aligned = self._kabsch_alignment(pred_coords, true_coords)
        
        # Calculate distances after alignment
        distances = np.sqrt(np.sum((pred_aligned - true_aligned)**2, axis=1))
        
        # Calculate TM-score
        tm_score = np.mean(1.0 / (1.0 + (distances / d0)**2))
        
        return float(tm_score)
    
    def _calculate_d0(self, L: int) -> float:
        """Calculate d0 normalization factor"""
        if L < 12:
            d0 = 0.3
        elif L < 16:
            d0 = 0.4
        elif L < 20:
            d0 = 0.5
        elif L < 24:
            d0 = 0.6
        elif L < 30:
            d0 = 0.7
        else:
            d0 = self.d0_constant * np.cbrt(L - self.d0_scale) - 1.8
        return d0
    
    def _kabsch_alignment(self, P: np.ndarray, Q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Optimal superposition using Kabsch algorithm
        
        Args:
            P: First structure (L, 3)
            Q: Second structure (L, 3)
        
        Returns:
            P_aligned, Q_aligned: Aligned structures
        """
        # Center both structures
        P_center = P - np.mean(P, axis=0)
        Q_center = Q - np.mean(Q, axis=0)
        
        # Calculate covariance matrix
        H = P_center.T @ Q_center
        
        # SVD
        U, S, Vt = np.linalg.svd(H)
        
        # Calculate rotation matrix
        R = Vt.T @ U.T
        
        # Ensure right-handed coordinate system
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        
        # Apply rotation
        P_aligned = P_center @ R
        Q_aligned = Q_center
        
        return P_aligned, Q_aligned


class StructureQualityMetrics:
    """Additional quality metrics for structure validation"""
    
    def __init__(self):
        self.clash_threshold = 2.0  # Angstroms
        self.bond_length_expected = 5.9  # Angstroms (inter-residue)
        self.bond_length_tolerance = 1.0  # Angstroms
    
    def calculate_all_metrics(self, coords: np.ndarray, sequence: str) -> Dict[str, float]:
        """Calculate all quality metrics"""
        metrics = {
            'num_clashes': self.count_clashes(coords),
            'rmsd_from_ideal': self.calculate_bond_rmsd(coords),
            'radius_of_gyration': self.calculate_radius_of_gyration(coords),
            'compactness': self.calculate_compactness(coords),
        }
        return metrics
    
    def count_clashes(self, coords: np.ndarray) -> int:
        """Count steric clashes (atoms too close)"""
        num_clashes = 0
        L = len(coords)
        
        for i in range(L):
            for j in range(i+2, L):  # Skip adjacent residues
                dist = np.linalg.norm(coords[j] - coords[i])
                if dist < self.clash_threshold:
                    num_clashes += 1
        
        return num_clashes
    
    def calculate_bond_rmsd(self, coords: np.ndarray) -> float:
        """Calculate RMSD of backbone bonds from ideal length"""
        deviations = []
        
        for i in range(len(coords) - 1):
            dist = np.linalg.norm(coords[i+1] - coords[i])
            deviation = dist - self.bond_length_expected
            deviations.append(deviation**2)
        
        if deviations:
            return np.sqrt(np.mean(deviations))
        return 0.0
    
    def calculate_radius_of_gyration(self, coords: np.ndarray) -> float:
        """Calculate radius of gyration (measure of compactness)"""
        center = np.mean(coords, axis=0)
        distances = np.sqrt(np.sum((coords - center)**2, axis=1))
        return np.sqrt(np.mean(distances**2))
    
    def calculate_compactness(self, coords: np.ndarray) -> float:
        """Calculate structure compactness"""
        # Average pairwise distance
        total_dist = 0.0
        count = 0
        
        for i in range(len(coords)):
            for j in range(i+1, len(coords)):
                dist = np.linalg.norm(coords[j] - coords[i])
                total_dist += dist
                count += 1
        
        if count > 0:
            return total_dist / count
        return 0.0


class SubmissionGenerator:
    """Generate submission files in competition format"""
    
    def __init__(self, config):
        self.config = config
        self.num_conformations = config.num_conformations
    
    def generate_submission(
        self,
        predictions: Dict[str, np.ndarray],
        sequences: Dict[str, str],
        output_path: Path
    ) -> pd.DataFrame:
        """
        Generate submission CSV
        
        Args:
            predictions: Dict mapping sequence_id -> coordinates (L, num_conf, 3)
            sequences: Dict mapping sequence_id -> sequence string
            output_path: Path to save submission CSV
        """
        rows = []
        
        for seq_id in predictions:
            coords = predictions[seq_id]  # Shape: (L, num_conformations, 3)
            sequence = sequences[seq_id]
            
            L = len(sequence)
            
            # Ensure coordinates match sequence length
            if len(coords) != L:
                raise ValueError(f"Coordinates length {len(coords)} != sequence length {L} for {seq_id}")
            
            for res_idx in range(L):
                # ID format: target_id_resid (matching competition format)
                row = {
                    'ID': f"{seq_id}_{res_idx+1}",
                    'resname': sequence[res_idx],
                    'resid': res_idx + 1,
                }
                
                # Add coordinates for all conformations
                for conf_idx in range(self.num_conformations):
                    if conf_idx < coords.shape[1]:  # Safety check
                        x, y, z = coords[res_idx, conf_idx, :]
                        row[f'x_{conf_idx+1}'] = float(x)
                        row[f'y_{conf_idx+1}'] = float(y)
                        row[f'z_{conf_idx+1}'] = float(z)
                
                rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Reorder columns to match expected format
        coord_cols = []
        for i in range(1, self.num_conformations + 1):
            coord_cols.extend([f'x_{i}', f'y_{i}', f'z_{i}'])
        
        columns = ['ID', 'resname', 'resid'] + coord_cols
        df = df[columns]
        
        # Clip coordinates to valid range
        from utils import clip_coordinates
        for col in coord_cols:
            df[col] = clip_coordinates(df[col].values)
        
        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"💾 Submission saved to {output_path}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Sequences: {len(predictions)}")
        
        return df
    
    def validate_submission(self, df: pd.DataFrame) -> bool:
        """Validate submission format"""
        # Check required columns
        required_cols = ['ID', 'resname', 'resid']
        for i in range(1, self.num_conformations + 1):
            required_cols.extend([f'x_{i}', f'y_{i}', f'z_{i}'])
        
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False
        
        # Check for NaN values
        if df.isnull().any().any():
            print(f"❌ Found NaN values")
            return False
        
        # Check coordinate ranges
        coord_cols = [col for col in df.columns if col.startswith(('x_', 'y_', 'z_'))]
        for col in coord_cols:
            if (df[col].abs() > 9999.999).any():
                print(f"⚠️  Coordinates out of range in column {col} (will be clipped)")
        
        print(f"✅ Submission validation passed")
        return True


class EvaluationPipeline:
    """Complete evaluation pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.tm_calculator = TMScoreCalculator()
        self.quality_metrics = StructureQualityMetrics()
        self.submission_gen = SubmissionGenerator(config)
    
    def evaluate_predictions(
        self,
        predictions: Dict[str, np.ndarray],
        ground_truth: Dict[str, np.ndarray],
        sequences: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Evaluate predictions against ground truth
        
        Args:
            predictions: Dict mapping seq_id -> predicted coords (L, num_conf, 3)
            ground_truth: Dict mapping seq_id -> true coords (L, 3)
            sequences: Dict mapping seq_id -> sequence string
        
        Returns:
            results: Dictionary of evaluation results
        """
        print("\n📊 Evaluating predictions...")
        
        tm_scores = []
        quality_results = []
        
        for seq_id in predictions:
            if seq_id not in ground_truth:
                continue
            
            # Use first conformation for evaluation
            pred_coords = predictions[seq_id][:, 0, :]  # (L, 3)
            true_coords = ground_truth[seq_id]  # (L, 3)
            
            # Calculate TM-score
            try:
                tm_score = self.tm_calculator.calculate(pred_coords, true_coords)
                tm_scores.append(tm_score)
                
                # Calculate quality metrics
                quality = self.quality_metrics.calculate_all_metrics(
                    pred_coords, 
                    sequences[seq_id]
                )
                quality['seq_id'] = seq_id
                quality['tm_score'] = tm_score
                quality_results.append(quality)
            except Exception as e:
                print(f"⚠️  Error evaluating {seq_id}: {e}")
        
        if not tm_scores:
            print("❌ No valid evaluations performed")
            return {}
        
        # Summary statistics
        results = {
            'mean_tm_score': np.mean(tm_scores),
            'median_tm_score': np.median(tm_scores),
            'std_tm_score': np.std(tm_scores),
            'min_tm_score': np.min(tm_scores),
            'max_tm_score': np.max(tm_scores),
            'num_sequences': len(tm_scores),
            'per_sequence_results': quality_results,
        }
        
        # Print results
        print(f"\n🎯 Evaluation Results:")
        print(f"  Mean TM-score: {results['mean_tm_score']:.4f}")
        print(f"  Median TM-score: {results['median_tm_score']:.4f}")
        print(f"  Std TM-score: {results['std_tm_score']:.4f}")
        print(f"  Range: [{results['min_tm_score']:.4f}, {results['max_tm_score']:.4f}]")
        print(f"  Sequences evaluated: {results['num_sequences']}")
        
        return results
