from run_log_analysis import get_dates_in_final_pre, run_log_analysis_by_date
from mev_analysis import run_mev_analysis
import multiprocessing

def main():
    base_data_dir = "/data4/zengliyi/final_pre"
    dates = get_dates_in_final_pre(base_data_dir)
    #dates = [date for date in dates if date >= "2023-03-01"] #why? fc version: 2022-03-01 - 2023-04-30
    print(dates)
    # log
    for date in dates:
        run_log_analysis_by_date(date)
    
    # mev
    n_workers = 8
    pool = multiprocessing.Pool(processes=n_workers)
    pool.map(run_mev_analysis,dates)
    pool.close()
    pool.join()
if __name__ == "__main__":
    main()