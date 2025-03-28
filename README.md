# Asylum seekers: During interantional migration crisis 

## Overview

The repo is my capstone project for CODE:You. The project analyzes the asylum seekers, refugees and refugee like situation population to define, total numbers, countries of origin, countries of asylum and more. The goal of the project is to demonstrate a general knowledge of Python, Plotly. 

## Analysis timeframe: 1962-2024

## Data

Asylum flow data:
- [Flow data](https://www.unhcr.org/refugee-statistics/insights/explainers/forcibly-displaced-flow-data.html)

Population data:
- [Population data](https://data.worldbank.org/indicator/SP.POP.TOTL)

Countries flags data:
- [Countries flags data](https://www.kaggle.com/datasets/zhongtr0n/country-flag-urls?resource=download)

## images:
* UNHCR logo https://freebiesupply.com/logos/unhcr-logo/
* World bank logo https://en.m.wikipedia.org/wiki/File:The_World_Bank_logo.svg

### Project Structure
---

The project is organized as follows:

- **Data Cleaning:** Jupyter notebooks with two funcitons that output the clean datasets to .csv files.

- **Data manipulation and graphs:** All the logic code is separated in a python file call functions_and_backend.py, in the future will be separate into a function class and a graph class.

- **Analysis:** All the analysis in located in a Jupyter notebook call Big Picture.ipynb

- **Visualizations :** I used Plotly to visualize my findings and Dash to make the graphs interactive. 

- **Dashboard:** There are dashboards inveded in the jupyter notebook for better vizualization.


## Features Utilized for the project

  | Feature        | Description                           |
  |----------------|---------------------------------------|
  | Read TWO data files| Used one csv file and one xlsx          |
  | Clean your data and perform a pandas merge with your two data sets, then calculate some new values based on the new data set.      | Cleaned my data and merged them with pandas. The calculated stats from various data points |
  | Make 3 matplotlib, and Plotly | Made various plots with Plotly to show off my findings. |
  | Make a Tableau dashboard      | Made a dasboard with Dash inside the jupyter notebook |
  | Utilize a virtual environment      | Made a venv for this project to keep my eviroment organized. |
  | Notate your code with markdown cells in Jupyter Notebook | Functions are described with comments and graphs are presented with markdown. |

## Dependencies

- Pandas
- Plotly
- Dash

## Getting Started

To run this project, follow these steps:

1. Clone the repository: `git clone https://github.com/EuVV22/AsylumAnalysis`
2. Navigate to the project folder: `cd AsylumAnalysis`
3. Create and activate a virtual environment: (see instructions in the next step)
4. Install the necessary dependencies: `pip install -r requirements.txt`
5. Run the jupyter notebook: `Cleaning.ipynb`
6. Run and explore the Jupyter notebook: `Big Picture.ipynb`


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
