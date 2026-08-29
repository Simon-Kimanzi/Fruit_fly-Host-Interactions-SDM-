# Insect–Host Plant Interactions: Citizen Science Data Analysis & SDM

> ENEZA Data Science Internship Project — International Centre of Insect Physiology and Ecology (icipe)

## 📋 Project Overview

Citizen-science platforms like iNaturalist provide large volumes of georeferenced, time-stamped biodiversity observations, including insect–host plant interaction data. This project uses iNaturalist occurrence and interaction records for **fruit flies (Tephritidae)** — including *Bactrocera*, *Zeugodacus*, and *Dacus* species — to:

1. Clean and structure raw citizen-science observation data
2. Analyze host-plant interaction patterns (which pest species associate with which host plants)
3. Model species distribution / ecological suitability (SDM) using occurrence and environmental data
4. Deploy an interactive dashboard for exploring results

**Supervisors:** Subramanian Sevgan, Elfatih Abdel Rehman
**Host Institution:** International Centre of Insect Physiology and Ecology (icipe)

## 🎯 Objectives

- [ ] Data cleaning & quality assessment
- [ ] Exploratory data analysis (species, temporal, geographic patterns)
- [ ] Host-pest interaction analysis
- [ ] Species Distribution Modeling (SDM)
- [ ] Interactive dashboard deployment

## 📊 Data

Source: [iNaturalist](https://www.inaturalist.org/) observations of Tephritidae (fruit flies), including:
- **Occurrence-only records**: where/when a fly was observed
- **Interaction-study records**: observations with an identified host plant

> **Note on data availability:** Raw data is not committed to this repo due to mixed per-record licensing (CC-BY-NC, CC0, CC-BY-ND, etc. — see the `license` column). See [`data/README.md`](data/README.md) for instructions on obtaining the dataset.

## 🗂️ Project Structure

```
.
├── data/                   # Raw & cleaned data (not committed — see data/README.md)
├── notebooks/              # Exploratory / analysis notebooks
├── src/
│   ├── data/               # Data cleaning scripts
│   ├── analysis/           # EDA & host-interaction analysis
│   ├── modeling/           # SDM model training
│   └── dashboard/          # Streamlit app
├── outputs/
│   ├── figures/            # Generated plots
│   └── models/             # Trained model artifacts
├── docs/                   # Additional documentation
├── requirements.txt
└── README.md
```

## 🚀 Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd <repo-name>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage

```bash
# 1. Clean the data
python src/data/clean_data.py

# 2. Run EDA
python src/analysis/eda.py

# 3. Run host-interaction analysis
python src/analysis/interactions.py

# 4. Train SDM
python src/modeling/train_sdm.py

# 5. Launch dashboard locally
streamlit run src/dashboard/app.py
```

## 🌐 Live Dashboard

🔗 _[link will go here once deployed]_

## 📈 Key Findings

_(To be filled in as analysis progresses)_

## 📚 References

See the full project proposal in [`docs/project_proposal.md`](docs/project_proposal.md).

## 👤 Author

_(Your name here)_

## 📄 License

Code in this repository: MIT License (see `LICENSE`).
Underlying observation data: subject to individual iNaturalist record licenses — see `data/README.md`.
