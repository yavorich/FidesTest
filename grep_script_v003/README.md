Grep script
===========

## Setup

- Python 3.9

No other dependencies needed

## Usage

Create general config (e.g. `config.ini`):
```
[Input]
separator=¬~
columns=md5, url, short_snippet, long_snippet
index_column=md5
```

Create a search config (e.g. `search.ini`):
```
[SearchFor]
suffix_max_padding=10
column_to_search=short_snippet
search_mode=regex
```

Run the script:
```
python3 script.py -i in/acropol.j2cm -o out.txt -s search.ini -w weights.csv
```

Check the script help (run without arguments or with -h) to get more info on how you could customize your user experience

