@echo off
echo Extracting new comments
py extract.py -i T9rlYjdfwJ0
py transform.py
echo ETL process complete!