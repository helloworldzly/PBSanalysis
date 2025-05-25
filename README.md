# PBSanalysis

This repository hosts the code for **An Empirical Study of Proposer-Builder Separation (PBS) Effects on Ethereum Ecosystem**. Our research conducts a comprehensive, data-driven analysis of Ethereum’s PBS implementation—a groundbreaking architectural shift reshaping block production dynamics.

The full methodological details and analysis results are documented in our accompanying paper (currently under peer review). Upon acceptance, we will synchronize the final version here. Researchers are encouraged to cite the official publication once available.


# Usage

## data preprocessing
 The data processing module provides a pipeline for downloading, processing, and organizing Ethereum data. It handles various types of blockchain data including:blocks, transactions, logs, token transfers, and traces. First, it will split data by date, and then will re-organize data by block.
### download data
1. block info & transaction & logs & token transfers
这里包括以太坊链上数据，这些需要从google cloud下载，具体请参见https://cloud.google.com/blog/products/data-analytics/ethereum-bigquery-public-dataset-smart-contract-analytics. 
2. Relay data
这里记录每一个块在relay上的提交记录，需要从https://mevboost.pics/data.html下载。
3. 
## data processing

## analysis

# Contacts
We welcome discussions and collaborations from researchers and practitioners interested in the PBS mechanism. Feel free to reach out to our team at: zengly@pcl.ac.cn, zhangzihao2016@gmail.com.
