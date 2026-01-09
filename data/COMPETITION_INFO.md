# RNA 3D Structure Prediction Competition

## Data Sources
1. Training sequences with ground truth structures
2. MSA (Multiple Sequence Alignment) files
3. Test sequences (structures to predict)

## Evaluation Metric
TM-score (Template Modeling score)
- Range: [0, 1]
- >0.5: Similar fold
- >0.7: Nearly identical structures
- Competition winning score: likely 0.65-0.75+

## Submission Format
- CSV with columns: ID, resname, resid, x_1, y_1, z_1, ..., x_5, y_5, z_5
- 5 conformations per residue
- All coordinates in Angstroms
