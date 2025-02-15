import pymysql
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error
import numpy as np
# Guname = AA,BB,CC..... factor: light_num,schoolnum.... value 1,2,3,10,20....
def return_graph_data(GuName,factor):


    connection = pymysql.connect('localhost' ,'root','123123','dev')

    cursor = connection.cursor()
    get_Gu = "select * from traffic where gu_code=%s"
    cursor.execute(get_Gu,(GuName))

    datas = cursor.fetchall()
    df = pd.DataFrame(datas, columns =  ["id", "gu_code", "Longitude", "Latitude", "trafficlight_num", "crosswalk_num", "station_num", "school_num", "avg_landprice", "house_1", "house_2", "house_3", "house_4", "commerce_1", "commerce_2", "commerce_3", "commerce_4", "green_1", "green_2", "green_3", "industry_1","industry_2", "industry_3", "limit_num", "mediansep_num", "island_num", "mean_lane", "mean_maxspeed", "mean_roadwth", "mean_roadlen", "busstop_num", "acc_count"])
    print("------------------pick selected gu from sql ------------------")
    print(df)
    df_process = df.iloc[:,4:-1]
    print("------------------only factor columns(into xgboost)------------------")
    print(df_process)
    df_process[df_process.columns] = df_process[df_process.columns].apply(pd.to_numeric, downcast='float', errors='coerce')

    xgboost_001 = joblib.load('xg_reg_002')

    pred_ori = xgboost_001.predict(df_process)
    df["pred_ori"] = pred_ori
    
    print("------------------pre_ori column add at df------------------")
    print(df)

    insert_value = []
    if(factor == "trafficlight_num" or factor == "crosswalk_num" or factor == "mean_lane"):
        insert_value = [-2,-1,0,1,2]
    elif(factor == "mean_roadwth"):
        insert_value = [-10,-5,0,5,10]
    elif (factor=="mediansep_num" or factor=="island_num" or factor=="school_num"):
        insert_value = [-1,0,1]
    df_process_ori = df_process[factor].copy() #notion
    print(df_process_ori)
    for value in insert_value:
        df_process[factor] = df_process[factor] + value
        for j in range(len(df["gu_code"])):
             if(df_process[factor][j] < 0):
                 df_process[factor][j] = 0
        print("------------------checkout changed factor ------------------")
        print(df[factor])
        print(df_process[factor])
        pred_factor = xgboost_001.predict(df_process)
        df[str(value)] = pred_factor
        df_process[factor] =df_process_ori
        # df["pred-decline"] = df["pred_factor"]-df["pred_ori"]
        # df["pred-decline"] = round(df["pred-decline"],2)

    print("------------------pred-decline = pred_factor - pred_ori------------------")
    print(df)
    # acc_num 으로 내림차순 sort하기  
    df = df.sort_values(["pred_ori"],ascending=[False])

    row_num =[]
    for i in range(len(df["gu_code"])): 
        row_num.append(i+1)
    df["rank"]= row_num
    print("------------------rank add at df column------------------")
    print(df)

    x = df.loc[:,"pred_ori":]
    print("------------------finally data (send to web)------------------")
    print(x)

    json_x = x.to_json(orient='table')
    print(json_x)
    return json_x
return_graph_data("AA","trafficlight_num") #test data