"""
Configuration settings for the RNA structure prediction project
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Main configuration class"""
    
    # Data paths
    data_dir: Path = Path("data")
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    msa_dir: Path = Path("data/msa")
    features_dir: Path = Path("data/features")
    
    # Model paths
    models_dir: Path = Path("models")
    checkpoints_dir: Path = Path("models/checkpoints")
    ensembles_dir: Path = Path("models/ensembles")
    configs_dir: Path = Path("models/configs")
    
    # Output paths
    results_dir: Path = Path("results")
    logs_dir: Path = Path("logs")
    cache_dir: Path = Path("cache")
    
    # Data files
    train_sequences_file: Path = Path("data/raw/train_sequences.csv")
    train_labels_file: Path = Path("data/raw/train_labels.csv")
    test_sequences_file: Path = Path("data/raw/test_sequences.csv")
    validation_sequences_file: Path = Path("data/raw/validation_sequences.csv")
    validation_labels_file: Path = Path("data/raw/validation_labels.csv")
    
    # Submission
    submission_sample_path: Path = Path("submission.csv")
    
    # Model settings
    device: str = "cuda"  # or "cpu"
    batch_size: int = 8
    num_epochs: int = 100
    learning_rate: float = 1e-4
    
    # Model architecture
    hidden_dim: int = 128
    use_msa: bool = True
    num_conformations: int = 5  # Number of conformations per sequence
    max_refinement_steps: int = 0  # Disabled for diversity (was 50)
    
    # Conformational diversity settings
    noise_scales: list = None  # Will be set in __post_init__
    
    # Feature extraction
    position_encoding_dim: int = 128
    max_sequence_length: int = 500
    
    # MSA settings
    max_msa_depth: int = 128
    
    # Training settings
    train_split: float = 0.9
    random_seed: int = 42
    
    # Inference
    num_predictions: int = 5  # Number of conformations per sequence (alias)
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        dirs = [
            self.data_dir, self.raw_data_dir, self.processed_data_dir,
            self.msa_dir, self.features_dir,
            self.models_dir, self.checkpoints_dir, self.ensembles_dir, self.configs_dir,
            self.results_dir, self.logs_dir, self.cache_dir
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Set default noise scales if not provided
        # Target RMSDs: [0, ~5, ~10, ~15, ~20] Angstroms
        if self.noise_scales is None:
            self.noise_scales = [0.0, 5.0, 10.0, 15.0, 20.0]


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration object.
    
    Args:
        config_name: Optional config name (for future extension)
    
    Returns:
        Config object
    """
    return Config()


# Default config instance
config = get_config()
