# 949 Coms

Welcome to 949 Coms! This project was developed in an effort to make useable data out of the YouTube comments sections of my favorite weekly podcast, [The 949 Podcast](https://www.youtube.com/@The949Podcast).

In a production environment, it is a data engineers role to create and maintain data pipelines between various points in the data's lifespan. In this example, I have constructed an ETL (Extract, Transform, Load) pipeline that **extracts** raw comment data from each video on the given channetl, **transforms** the raw data into clean text data, and finally **loads** both the raw and processed data into a relational databse for use in downstream analytics.

In future work, I plan to integrate this process into cloud-hosted automation technology. This would allow for a constant data stream of processed comments in real-time! The impact of this project lies in the reliability of the process and capabilities we have as data scientists to make decisions and insights given access to good data. 
