# Dependencies
For this project, you only need Python version 2.7 or greater installed on your machine.

# Usage
In src/, there are two python files:
- `run_session_acquisition.py` is the main script and uses functions from `utils.py` module.
- `utils.py` contains multiple helper functions and keeps them separate from the main script for clarity

The main script takes 2 required arguments and 1 optional argument.
The first 2 arguments are input files, `log.csv` and `inactivity_period.txt` respectively. The third argument is the output file (Default name is `sessionization.txt` unless specified by user).
Here is an example:
```shell
$ python run_session_acquisition.py log.csv inactivity_period.txt sessionization.txt
```

Note that `log.csv` (or any other valid csv file) must be located in `input/` folder.
`inactivity_period.txt` (or any other valid text file) must also be located in `input/` folder.
As for the output file, it will be created in `output/` folder.


There is a built-in help menu that you can access:

```shell
$ python run_session_acquisition.py -h

usage: run_session_acquisition.py [-h] LOG_FILE INACTIVITY_FILE [OUTPUT_FILE]

Streaming Data from EDGAR

 positional arguments:
  LOG_FILE         csv log file in root->input folder
  INACTIVITY_FILE  Text file containing the period of inactivity in seconds,
                   located in root-> input folder
  OUTPUT_FILE      (Optional) Ouput file name created in root->output folder.
                   Default name is sessionization.txt

optional arguments:
  -h, --help       show this help message and exit
```

As for `run.sh` bash script, it is setup to read data from a csv file named `log.csv` located in `input/` folder.
It also extract the inactivity period from a text file named `inactivity_period.txt` also located in `input/` folder.
Finally, the output file will be created in `output/` folder. Default name is `sessionization.txt`.

# Test

There is a total of 6 tests available with varying inactivity period.
Test 1 and test 2 used the provided input file but different inactivity period.
Test 3 and test 4 are consecutives samples from EDGAR weblog file dated at 2017-06-25 (downloaded from their website)
Test 5 and test 6 are composed of random samples from the same EDGAR weblog file (re-ordered by time)

