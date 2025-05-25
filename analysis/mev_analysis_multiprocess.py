
import multiprocessing

from pbs_analysis import analysis_pbs_into_pickle_by_date
from data_utils import get_dates_by_month,get_all_dates
from mev_analysis import run_mev_analysis



def main():
    #data_dir = "/mnt/data1/zhangzihao/preprocessed_data/"
    n_workers = 8
    
    #months = ["2023_03","2023_04"]
    #dates =[]
    #for month in months:
    #    dates.extend(get_dates_by_month(data_dir=data_dir,month=month))
    #dates = get_all_dates(data_dir)

    print(w3.is_connected())
    base_data_dir = "/data4/zengliyi/final_pre"
    dates = get_dates_in_final_pre(base_data_dir)
    #dates = [date for date in dates if date >= "2023-03-01"] #why? fc version: 2022-03-01 - 2023-04-30
    print(dates)
    pool = multiprocessing.Pool(processes=n_workers)
    pool.map(run_mev_analysis,dates)
    pool.close()
    pool.join()
    
if __name__ == "__main__":
    main()