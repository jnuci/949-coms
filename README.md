# 949 Coms

Welcome to 949 Coms! This project was developed in an effort to make useable data out of the YouTube comments sections of my favorite weekly podcast, [The 949 Podcast](https://www.youtube.com/@The949Podcast).

In a production environment, it is a data engineers role to create and maintain data pipelines between various points in the data's lifespan. In this example, I have constructed an ETL (Extract, Transform, Load) pipeline that **extracts** raw comment data from each video on the given channetl, **transforms** the raw data into clean text data, and finally **loads** both the raw and processed data into a relational databse for use in downstream analytics.

Additionally, we have constructed an analytics dashboard that can be integrated with live data.  

### Replicating dashboard

System requirements:
 - PostgreSQL 15
 - PostgreSQL bin on PATH
 - pgAdmin 4
 - Python 3.10 or later

Define and configure database
In your pgAdmin application, create database with a relevant name then run this command in your terminal:
```
psql -U {your_username} -d {your_database_name} -f db_dump_file.sql
```

After obtaining a YouTube Data API key and your local IP address, define environment variables in a config file:
```
API_KEY = {youtube_api_key}
DB_PASS = {database_password}
LOCALHOST = {your_ipv4_address}
```

(Optional) Define and activate virtual environment:

```
python -m venv {virtual environment name}
\venv\scripts\activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Run ETL process to update databases:
```
ETL.bat
```

To start app:
```
py app.py
```