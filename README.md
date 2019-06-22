## Los Angeles Closed Caption News Data Archive to CSV

Convert the text files from the infamous LA Closed-Caption Television News data---infamous because it was part of the LaCour scandal--- to a CSV.

## Description

A python script to parse the Closed-Caption files (text format) to a single CSV file.

### Usage

```
Parse CC files to a single CSV file
Usage: lacc_to_csv.py [options] <directory of text files>

Options:
  -h, --help            show this help message and exit
  -o OUTFILE, --out=OUTFILE
                        Output file in CSV (default: program.data.csv)
```

### Example

```
python lacc_to_csv.py -o output.csv ./tv
```
