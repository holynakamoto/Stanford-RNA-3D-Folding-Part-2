# Competition Data Format Guide

## Input Files

### test_sequences.csv
Contains the RNA sequences to predict. Columns:
- **target_id**: Identifier (format: `pdb_id_chain_id`)
- **sequence**: RNA sequence string (concatenated chains according to stoichiometry)
- **temporal_cutoff**: Publication date (yyyy-mm-dd)
- **description**: Entry description/title
- **stoichiometry**: Chain information (format: `{chain:number}`)
- **all_sequences**: FASTA-formatted sequences of all chains
- **ligand_ids**: Three-letter ligand identifiers (semicolon-delimited)
- **ligand_SMILES**: SMILES strings for ligands (semicolon-delimited)

### MSA Files
Located in `MSA/` directory, named `{target_id}.MSA.fasta`
- Multiple sequence alignments in FASTA format
- Headers contain `chain={chain}` tag
- For multi-chain targets, each chain's homologs are in separate rows with gaps (-) for other chains

### PDB_RNA/
Contains structural data:
- `{PDB_id}.cif` files for RNA-containing PDB entries
- `pdb_seqres_NA.fasta` - sequences of all nucleic acid chains
- `pdb_release_dates_NA.csv` - PDB entry IDs and release dates

## Output Format

### submission.csv
Required format:
```
ID,resname,resid,x_1,y_1,z_1,x_2,y_2,z_2,x_3,y_3,z_3,x_4,y_4,z_4,x_5,y_5,z_5
1ABC_A_1,G,1,-7.561,9.392,9.361,-7.301,9.023,8.932,...
1ABC_A_2,G,2,-8.02,11.014,14.606,-7.953,10.02,12.127,...
```

- **ID**: Format is `target_id_resid` (e.g., `1ABC_A_1`, `1ABC_A_2`)
- **resname**: Nucleotide (A, C, G, or U)
- **resid**: Residue number (1-based indexing)
- **x_1, y_1, z_1, ..., x_5, y_5, z_5**: Coordinates for 5 predictions
- Coordinates must be clipped to range [-999.999, 9999.999]

## Key Points

1. **ID Format**: Submission IDs are `target_id_resid`, not just `target_id`
2. **Five Predictions**: Must provide exactly 5 structure predictions per sequence
3. **Coordinate Clipping**: All coordinates are automatically clipped to valid range
4. **C1' Atom**: Predictions are for the C1' atom of each residue
5. **Residue Numbering**: Uses 1-based indexing (first residue is 1, not 0)

## Example Workflow

```python
# Read sequences
test_sequences = read_test_sequences("test_sequences.csv")

# For each target
for _, row in test_sequences.iterrows():
    target_id = row['target_id']
    sequence = row['sequence']
    
    # Optional: Load MSA
    msa_data = read_msa_file(target_id)
    
    # Generate 5 predictions
    for pred_num in range(1, 6):
        coords = predict_rna_structure(sequence, pred_num, msa_data)
        # Save with ID format: target_id_resid
```

## Helper Functions

- `parse_fasta()`: Parse `all_sequences` field into chain:sequence dictionary
- `read_msa_file()`: Load MSA data for a target
- `clip_coordinates()`: Ensure coordinates are in valid range
- `generate_submission_template()`: Create submission DataFrame structure
- `validate_submission()`: Check submission format correctness
