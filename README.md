### Setup

Install [Python 3.8](https://docs.python.org/3/using/windows.html)
Install requirements
```bash
pip install -r requirements.txt
```

### Execute
Windows
```bash
py <REPO_LOCATION>/calculate_tax.py [-h] [--debug] [--filepath FILEPATH]
```

`-h` help

`--debug`,`-d`  show debug output

`--filepath`,`-f`  explicitly provide filepath to csv otherwise dialogue will trigger

Will create a file in the same directory `<FILENAME>_result.txt` with gross, net and tax figures.
Example output:

```text
total gross: 1059.94
total net: 858.55
total tax: 201.39
avg. tax percentage: 19%
evaluated range: 2021/01/02 - 2021/02/19
```

Will also create an Excel file in the same directory `<FILENAME>_fixed.xlsx`.