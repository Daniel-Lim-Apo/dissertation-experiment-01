# Data Directory

This directory contains example data used for the experimental pipeline of this dissertation.

## Data Confidentiality and Synthetic Content

> [!IMPORTANT]
> **Confidentiality Notice**: The original dataset used in this research contains sensitive information and is not publicly available due to privacy and legal requirements.

The file [ocorrencias_example.csv](data/ocorrencias_example.csv) provided in this folder is **entirely synthetic**. All names, identification numbers (CPF, RG), addresses, and incident descriptions are fictional and were generated solely for demonstration and testing purposes. 

## Usage for Reproducibility

To replicate the experiments described in this dissertation using your own data, you must ensure that your input files strictly adhere to the following:

- **Format**: CSV (Comma-Separated Values).
- **Delimiter**: Semicolon (`;`).
- **Structure**: The column headers and data types must match exactly those found in `ocorrencias_example.csv`.
- **Fields**:
  - `ano`: Year identifier.
  - `unidade`: Unit/Station code.
  - `numero`: Occurrence number.
  - `aditamento`: Amendment/Addendum identifier.
  - `historico`: Full textual narrative of the occurrence.

For more detailed technical specifications on the data fields and pipeline processing, please refer to the main [DATA_FORMAT.md](../DATA_FORMAT.md) file.
