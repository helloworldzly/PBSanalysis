# PBSanalysis

This repository hosts the code for **An Empirical Study of Proposer-Builder Separation (PBS) Effects on Ethereum Ecosystem**. Our research conducts a comprehensive, data-driven analysis of Ethereum’s PBS implementation—a groundbreaking architectural shift reshaping block production dynamics.

The full methodological details and analysis results are documented in our accompanying paper (currently under peer review). Upon acceptance, we will synchronize the final version here. Researchers are encouraged to cite the official publication once available.

# Introduction
We have collected the following Ethereum on-chain data:
- Block Data
- Transaction Data
- Event Logs
- Token Transfer Records
- Transaction Traces

We have developed a comprehensive toolkit for analyzing PBS (Proposer-Builder Separation) and MEV (Maximal Extractable Value) using this data, including:

1. PBS Analysis
   - Block Builder Behavior Analysis
   - Block Proposer Revenue Analysis
   - Transaction Fee Analysis
2. MEV Analysis
   - Detection and analysis of Arbitrage, Liquidation, and Sandwich attacks (the detection logic comes from [^weintraub2022] and )
   - MEV revenue flow analysis and tracking

# Usage

## Download Raw Data
1. Block Info, Transactions, Logs & Token Transfers
    - These Ethereum on-chain data sets should be downloaded from Google Cloud in parquet.gzip format. For detailed instructions, please refer to [Google Bigquery](https://cloud.google.com/blog/products/data-analytics/ethereum-bigquery-public-dataset-smart-contract-analytics).
2. Relay Data (Only use for analyis relay behavior)
    - Block submission records from relays can be downloaded from [Mevboost.pics](https://mevboost.pics/data.html).
3. Smart Contract Information
    - This requires access to specific chain RPC endpoints. We use [QuickNode RPC](https://www.quicknode.com/docs/ethereum) to obtain contract information and token data
4. CoinGecko
    - Used for retrieving daily token prices (can be replaced with alternative coin price APIs)

## Data Preprocessing
The data processing module provides a comprehensive pipeline for downloading, processing, and organizing Ethereum data. It handles various types of blockchain data including blocks, transactions, logs, token transfers, and traces. The process involves two main steps: first splitting data by date, then reorganizing data by block.

1. Place all data downloaded from Google Cloud into the data directory, with separate folders for each data type

2. Data Processing
    ```bash
    python data_split_batch.py  # Split raw data by date
    python data_merge_batch.py  # Merge split data of same date
    python preprocess_batch.py  # Re-organize data by block
    ```
3. Token Price Retrieval (using CoinGecko API)
    ```bash
    python price_loader.py
    ```

## PBS & MEV Analysis
Our analysis focuses on two main aspects: PBS analysis examining block proposer and builder behavior, and MEV analysis investigating MEV distribution and revenue allocation. Our implementation references https://github.com/a-flashbot-in-the-pan/a-flashbot-in-the-pan

1. PBS Analysis
    - Analyzes block builder and proposer behavior, calculates revenue distribution, and examines transaction fee allocation
    ```bash
    python mev_analysis.py
    ```
2. Log Analysis
    - Parses event logs from various DeFi protocols, supporting major DEXes including Uniswap, Curve, Balancer, etc.
    - Requires QuickNode RPC for contract information and daily token prices
    ```bash
    python log_mev_analysis_multiprocessing.py
    ```
3. MEV Analysis
    - Based on DeFi events parsed in step 2, analyzes MEV revenue distribution
    - Detects and analyzes arbitrage trades, liquidations, and sandwich attacks
    ```bash
    python mev_analysis_multiprocess.py
    ```
4. Results
    - All MEV and PBS information from blocks is stored in daily-segmented data files for subsequent analysis

## Reference
[1] Qin, Kaihua, Liyi Zhou, and Arthur Gervais. "Quantifying blockchain extractable value: How dark is the forest?." 2022 IEEE Symposium on Security and Privacy (SP). IEEE, 2022.
[^weintraub2022]: Weintraub, Ben, et al. "A flash (bot) in the pan: measuring maximal extractable value in private pools." Proceedings of the 22nd ACM Internet Measurement Conference. 2022.

# Contact
We welcome discussions and collaborations from researchers and practitioners interested in the PBS mechanism. Feel free to reach out to our team at: zengly@pcl.ac.cn, zhangzihao2016@gmail.com.
