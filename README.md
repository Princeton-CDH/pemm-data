# PEMM data

![CSV validation](https://github.com/Princeton-CDH/pemm-data/workflows/Valid%20CSVs/badge.svg)

From 2020 to 2022, this repository was used to version and publish data from the [Princeton Ethiopian Miracles of Mary (PEMM)](https://cdh.princeton.edu/projects/ethiopian-miracles-mary-project/) that is automatically synchronized from Google Sheets. A 1.0 version of the dataset has been published on Zenodo; future versions of the data will be made available through the [PEMM project website](https://pemm.princeton.edu/). 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6909569.svg)](https://doi.org/10.5281/zenodo.6909569) (Version 1.0 data)

For an online view of the data in this repository that allows for filtering and sorting, we recommend [Flat GitHub](https://flatgithub.com/Princeton-CDH/pemm-data?filename=data%2Fcanonical_story.csv&sha=215b3f0c9bd5540d0f929b8133868ea8c34c98e8).

For a write-up of the approach for using Google Sheets as a lightweight database and synchronizing eports to GitHub, see [Is a spreadsheet a database?](https://cdh.princeton.edu/updates/2021/02/11/google-sheets-experiments-pemm/) by Rebecca Sutton Koeser (February 2021).

To see the code used to generate the PEMM spreadsheets and synchronize data to GitHub, see [pemm-scripts](https://github.com/Princeton-CDH/pemm-scripts).

| :warning:  | This site represents work in progress. Please consult the [2022 Zenodo upload](https://doi.org/10.5281/zenodo.6909569) for a presentation of the most useful, most complete data to date. Please contact Principal Investigator Wendy Laura Belcher at wbelcher@princeton.edu if you need more information; the data should not be cited without permission.       |
|---------------|:------------------------|

----

Files in the data directory should *NOT* be edited on GitHub.

## Data Model

This data model diagram shows how the documents in the data folder
are related to each other.

![data model diagram](docs/v0.2_data-model.svg)
