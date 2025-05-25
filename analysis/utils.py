

import json
import codecs

def json_parse(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data



def hex_to_unicode(hex_string):
    hex_string = hex_string.replace("0x", "")
    return codecs.decode(hex_string, "hex").decode("utf-8")

def hex_to_int(hex_string):
    hex_string = hex_string.replace("0x", "")
    return int(hex_string, 16)



def get_hhi(number_list):
    sum_value = 0
    for number in number_list:
        sum_value += number
    
    hh_index = 0
    for number in number_list:
        hh_index += (number/sum_value)**2
    return hh_index


def get_crn(number_list,n):
    if n > len(number_list):
        return 1
    else:
        number_list.sort(reverse= True)
    
    total = sum(number_list)
    crn = 0
    for i in range(n):
        crn += number_list[i]/total
    return crn

def get_abbr(text):
    return text[:5] + "..."

def chunk_list(lst, n):
    # 计算每份的大小
    size = len(lst) // n
    # 将列表切片为n份
    return [lst[i:i+size] for i in range(0, len(lst), size)]

    