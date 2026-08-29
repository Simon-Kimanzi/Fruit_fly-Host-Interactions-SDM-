# Data

## Source

Observations of Tephritidae (fruit flies) exported from [iNaturalist](https://www.inaturalist.org/), including both occurrence-only records and host-plant interaction records.

## Why raw data isn't committed

Each observation carries its own license (CC-BY-NC, CC0, CC-BY, CC-BY-NC-ND, CC-BY-NC-SA, CC-BY-SA, CC-BY-ND). Several of these restrict redistribution or commercial use, so bulk-committing the raw dataset to a public repo isn't appropriate. Re-export it directly from iNaturalist for reproduction.

## Expected files (place here to run the pipeline)

| File | Description |
|---|---|
| `raw_data.csv` | Raw export from iNaturalist, 73 columns |
| `clean_data.csv` | Output of `src/data/clean_data.py` |

## Schema notes

- `Data_Category`: `"Occurrence Only"` (no host plant recorded) vs `"Interaction Study"` (host plant recorded)
- `host_plant`: scientific name of host plant, or `"Unknown"` for occurrence-only records
- `quality_grade`: `"research"` (community-vetted ID) vs `"needs_id"` (unconfirmed)
- `coordinates_obscured`: `True` if iNaturalist randomized the location
