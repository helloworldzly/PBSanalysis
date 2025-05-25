from preprocess import preprocess_by_day
from data_utils import get_dates_by_month
import multiprocessing
import os
import re



def main():
    data_dir = "/data4/zengliyi/all_preprocessed_data/"
        #"/mnt/data1/zhangzihao/preprocessed_data/"
    n_workers = 4
    #months = ["2022_03","2022_04","2022_05","2022_06","2022_07","2022_08","2022_09","2023_02"]
    months = ["2022-03","2022-04","2022-05","2022-06","2022-07","2022-08","2022-09","2022-10","2022-11","2022-12","2023-01","2023-02","2023-03","2023-04","2023-05","2023-06","2023-07","2023-08","2023-09"]

    dates =[]
    for month in months:
        #file_names = find_files_with_date(data_dir, month)
        dates.extend(get_dates_by_month(data_dir="/data4/zengliyi/preprocessed_data/",month=month))
        dates.extend(get_dates_by_month(data_dir="/data4/zengliyi/preprocessed_data_first/", month=month))
    
    unfinished_dates = []
    for date in dates:
        target_path = os.path.join(data_dir,f"preprocess_data_{date}.pkl") #,date,
        if not os.path.exists(target_path):
            unfinished_dates.append(date)
    print("date: ", unfinished_dates)
    
    pool = multiprocessing.Pool(processes=n_workers)
    pool.map(preprocess_by_day,unfinished_dates)
    
    pool.close()
    pool.join()
    
if __name__ == "__main__":
    main()