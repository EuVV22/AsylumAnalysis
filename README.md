# Asylum seekers: During interantional migration crisis

## Overview

The repo is my capstone project for CODE:You. The project analyzes the asylum seekers, refugees and refugee like situation population to define, total numbers, countries of origin, countries of asylum and more. The goal of the project is to demonstrate a general knowledge of Python, Plotly.

## Data

Asylum flow data:
- [Flow data](https://www.unhcr.org/refugee-statistics/insights/explainers/forcibly-displaced-flow-data.html)

Population data:
- [Population data](https://data.worldbank.org/indicator/SP.POP.TOTL)

Countries flags data:
- [Countries flags data](https://www.kaggle.com/datasets/zhongtr0n/country-flag-urls?resource=download)

## images:
UNHCR logo https://freebiesupply.com/logos/unhcr-logo/
World bank logo https://en.m.wikipedia.org/wiki/File:The_World_Bank_logo.svg

### Project Structure
---

The project is organized as follows:

- **Data Exploration:** Jupyter notebooks or scripts to explore the dataset.

- **Analysis:** Using Python with the  Pandas package to clean the data.

- **Visualizations :** Using Plotly to visualize my findings. 

- **Dashboard:** There are dashboards inveded in the jupyter notebook for better vizualization.


## Features Utilized for the project

  | Feature        | Description                           |
  |----------------|---------------------------------------|
  | Read TWO data files| Used one csv file and one xlsx          |
  | Clean your data and perform a pandas merge with your two data sets, then calculate some new values based on the new data set.      | Cleaned my data and merged them with pandas. The calculated stats from various data points |
  | Make 3 matplotlib, and Plotly | Made various plots with Plotly to show off my findings. |
  | Make a Tableau dashboard      | Made a dasboard with Dash inside the jupyter notebook |
  | Utilize a virtual environment      | Made a venv for this project to keep my computer clean. |
  | Notate your code with markdown cells in Jupyter Notebook | Code is described with comments. |

## Getting Started

To run this project, follow these steps:

1. Clone the repository: `git clone https://github.com/EuVV22/AsylumAnalysis`
2. Install the necessary dependencies: `pip install -r requirements.txt`
3. Explore the Jupyter notebooks or scripts in the respective folders.

## Dependencies

- Pandas
- Plotly
- Dash


###  Virtual Environment Instructions
---
1. After you have cloned the repo to your machine, navigate to the project 
folder in GitBash/Terminal.
1. Create a virtual environment in the project folder. 
1. Activate the virtual environment.
1. Install the required packages. 
1. When you are done working on your repo, deactivate the virtual environment.

Virtual Environment Commands

| Command | Linux/Mac | GitBash |
|---------|-----------|---------|
| Create | `python3 -m venv venv` | `python -m venv venv` |
| Activate | `source venv/bin/activate` | `source venv/Scripts/activate` |
| Install | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Deactivate | `deactivate` | `deactivate` |
