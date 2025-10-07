# Electoral College Project

This repository contains Python code and data used to simulate a proportional, turnout-based Electoral College system.

## Files

- `electoral_college.py` – Python code that calculates state allocations and candidate apportionments.
- `data/countypres_2000-2024.csv` – MIT Election Data for U.S. presidential elections.

## Usage

1. Make sure you have Python 3 and `pandas` installed.
2. Set `election_year` variable on line 114 to desired presidential election year (2000 - 2024).
3. Run `electoral_college.py` to reproduce the election simulations.

## Notes

This project applies the Huntington–Hill method for interstate allocation of electors and the Sainte–Laguë method for intrastate proportional apportionment.
