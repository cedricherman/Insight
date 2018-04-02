# Dependencies
For this project, you only need Python version 2.7 or greater installed on your machine.

# Usage
In src/, there are two python files:
- `run_session_acquisition.py` is the main script and uses functions from `utils.py` module.
- `utils.py` contains multiple helper function and kepts them separate from the main script for clarity

Run.sh is setup to read data from a csv file named `log.csv` located in input/ folder.
It also extract the inactivity period from a text file named `inactivity_period.txt` located in input/ folder
Finally, the output file will be created in output/ folder. Default name is `sessionization.txt`.

There is a built-in help menu that you can access:
$ python run_session_acquisition.py -h
