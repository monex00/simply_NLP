# simply_NLP

This repository contains a collection of projects developed during the Natural Language Processing (NLP) course. Each project addresses a specific topic and includes the necessary files for execution and understanding of the results.

## Projects

### 1. **Basicness**

- **Description**: A project focused on analyzing and calculating the "basicness" of terms or concepts. A Random Forest model was used, starting from an annotated dataset and adding features derived from WordNet and a corpus of children's stories.
- **Main Files**:
  - `basicness.ipynb`: Main notebook for analysis.
  - `basicness_f.py`: Script for functions and logic.
- **Results**: Includes results in CSV format (`fold1_results.csv`).
- **Requirements**:
  ```bash
  pip install -r requirements.txt
  ```

### 2. **content2form**

- **Description**: This project performs onomasiological research, starting from definitions written by participants, and conducts a search in the WordNet graph following the "genus-differentia" principle.
- **Main Files**:
  - `content2form.ipynb`: Main notebook.
  - `C2F_functions.py`: Auxiliary functions script.
- **Dataset**: `TLN-definitions-24.csv`.
- **Requirements**:
  ```bash
  pip install -r requirements.txt
  ```

### 3. **Defs**

- **Description**: A project dedicated to the analysis of linguistic definitions. It aims to identify similarities between definitions provided by various participants.
- **Main Files**:
  - `def.ipynb`: Main notebook.
  - `defs_f.py`: Functions script.
- **Dataset**: `TLN-definitions-24.csv`.

### 4. **FN**

- **Description**: This project uses WordNet to disambiguate the various components of a frame in FrameNet.
- **Main Files**:
  - `FN_algo.py`: Core algorithms.
  - `FN_main.ipynb`: Main notebook.
  - JSON mapping files: `mappings_hand_loris.json`, `mappings_hand_mattia.json`, `mappings_hand_simo.json`.

### 5. **ProfDanny\_FINAL**

- **Description**: This project aims to create a chatbot that acts as a professor, asking questions on NLP topics through a frame-based approach.
- **Main Files**:
  - `dep.py`: Core script.
  - `frames.json`: JSON file containing frames.
- **Documentation**: Includes a `readme.txt` file with additional details.

### 6. **TweetLikeTrump**

- **Description**: Project to generate texts similar to Trump tweets.
- **Main Files**:
  - `ngrams.ipynb`: Notebook on n-grams.
  - `ngrams_lm.ipynb`: Notebook for language models.
- **Data**: Stored in the `data` directory.

### 7. **WSD**

- **Description**: Project for Word Sense Disambiguation (WSD).
- **Structure**:
  - `ConceptualSimilarity/`: Implementations for conceptual similarity.
  - `Lesk/`: Algorithms based on the Lesk method.

## General Requirements

Ensure you have installed:

- Python >= 3.8
- Libraries specified in the `requirements.txt` files in each project.

## Repository Structure

```
.
├── Basicness/
├── content2form/
├── Defs/
├── FN/
├── ProfDanny_FINAL/
├── TweetLikeTrump/
├── WSD/
└── README.md
```

##

