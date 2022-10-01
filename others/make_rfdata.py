  

import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import csv

from sklearn.datasets import make_blobs
import hdbscan
import matplotlib.pyplot as plt
import pandas as pd

np.set_printoptions(threshold=np.inf)

lin=20
inputfile="./軌跡數據/abnormal/abnormal"+str(lin)+".txt"
y=np.loadtxt(inputfile, dtype=float)
plt_order = []

np.shape(y) #功能是讀取矩陣的形狀，輸出如: (6791, 2) 
coordinate=[[0]*2 for i in range(720)] #二維矩陣，每一row是元素為兩個0的一維矩陣, 有720個row

count=0 #整個txt的pointer
onecircle=0 #720個資料算一個動作
graphnum=0 #計算有多少個動作
List_size_in_graph=[] #紀錄被判定成人的群有幾個點
total_node_size=0 #紀錄所有人的點數的總和，用來設定array大小
check_for_peop=0 #用來判斷此動是否有被判定為人的物件

adjacency_pointx = []
adjacency_pointy = []
adj_index = 0
filenum=1


#filenum=0
#filename=0
while count < np.size(y, 0):  #因為row裡面有兩個col
    if (onecircle < 720):
        if(y[count,0]>0 and y[count,0]<90):
            coordinate[onecircle][0]=y[count][1]*math.cos(math.radians(y[count,0]))
            coordinate[onecircle][1]=y[count][1]*math.sin(math.radians(y[count,0]))
        if(y[count,0]>90 and y[count,0]<180):
            coordinate[onecircle][1]=y[count][1]*math.sin(math.radians(y[count,0]))
            coordinate[onecircle][0]=y[count][1]*math.cos(math.radians(y[count,0]))
        if(y[count,0]>180 and y[count,0]<270):
            coordinate[onecircle][0]=y[count][1]*math.cos(math.radians(y[count,0]))
            coordinate[onecircle][1]=y[count][1]*math.sin(math.radians(y[count,0]))
        if(y[count,0] and y[count,0]<360):
            coordinate[onecircle][1]=y[count][1]*math.sin(math.radians(y[count,0]))
            coordinate[onecircle][0]=y[count][1]*math.cos(math.radians(y[count,0]))
        onecircle+=1
    else:
      
        graphnum=graphnum+1
        x=np.array(coordinate)
        clustering=DBSCAN(algorithm='brute',eps=180,leaf_size=180,metric='euclidean'
                          ,metric_params=None,min_samples=2,n_jobs=1,p=None).fit(coordinate)
        onecircle=0
        #整體房間空間
        plt.figure(figsize=(10,10),dpi=250)
        plt.scatter(x[:,0],x[:,1],c=clustering.labels_)
        plt.savefig('./photo/file'+str(1)+'step'+str(adj_index), dpi=250, bbox_inches='tight')
        plt.show()
        
        clustering.fit(x)
        Y_pred = clustering.labels_ #分群狀況
       
        #動態陣列
        Listx=[]
        Listy=[]

        #知道有幾個分群
        maxcluster=0
        for k in range(720):
                if(Y_pred[k]>maxcluster):
                    maxcluster=Y_pred[k]
        maxcluster=maxcluster+1
        #print(maxcluster)

        #建立群陣列
        for i in range(maxcluster):
            Listx.append([])
            Listy.append([])

        #把資料分群放進陣列
        for j in range(720):
            if(Y_pred[j]!=-1):
                Listx[Y_pred[j]].append(x[j][0])
                Listy[Y_pred[j]].append(x[j][1])
        
        arrx=np.array(Listx)
        arry=np.array(Listy)

        
        #印出每一個物件
        for m in range(0,maxcluster):
            plt.scatter(arrx[m],arry[m])
            plt.show()
    
    #得到rf tree的資料
        length=np.zeros(maxcluster) #y的距離差長度
        width=np.zeros(maxcluster) #x的距離差寬度
        group_number = len(Listx) #總共幾群
        center_distance=np.zeros(maxcluster)

        #計算長寬
    
        for m in range(maxcluster):
            length[m] = max(Listx[m]) - min(Listx[m])
            width[m] = max(Listy[m]) - min(Listy[m])

        #計算到中心點的平均距離
       
        for m in range(maxcluster):
            center_x = sum(Listx[m])/len(Listx[m])
            center_y = sum(Listy[m])/len(Listy[m])
      
            for n in range(len(Listx[m])):           
                center_distance[m]=center_distance[m]+ ((Listx[m][n]-center_x)**2+ (Listy[m][n]-center_y)**2)**0.5  
            center_distance[m]=center_distance[m]/len(Listx[m])
            
        #算每群的點的數量
        num_of_each_group=[] #每群幾個點

        for i in range(group_number):
            num_of_each_group.append(len(Listx[i]))
            
        #算每群的點的標準差
        x_std = [] #每群點的x的標準差
        y_std = [] #每群點的y的標準差
        x_var = [] #每群點的x的變異數
        y_var = [] #每群點的y的變異數

        for i in range(group_number):
            x_std.append(np.std(Listx[i]))
            y_std.append(np.std(Listy[i]))
            x_var.append(np.var(Listx[i]))
            y_var.append(np.var(Listy[i]))
        
        #csv輸出
        filename ="./rffile/abnormal"+str(lin)+"-"+str(filenum)+".csv"
        sheet=[[0 for _ in range(9)] for _ in range(group_number)]
        for i in range(group_number):
            sheet[i][0]=lin
            sheet[i][1]=num_of_each_group[i]
            sheet[i][2]=x_std[i]
            sheet[i][3]=y_std[i]
            sheet[i][4]=width[i]
            sheet[i][5]=length[i]
            sheet[i][6]=center_distance[i]
            sheet[i][7]=x_var[i]
            sheet[i][8]=y_var[i]

            np.savetxt(filename, sheet, delimiter =",",fmt ='% s')
        filenum+=1
        
        #轉換rf tree 訓練樣本
        sheet=[[0 for _ in range(8)] for _ in range(group_number)] #group_number個裡面有8個0的一維陣列
        for i in range(group_number):
            sheet[i][0]=num_of_each_group[i]
            sheet[i][1]=x_std[i]
            sheet[i][2]=y_std[i]
            sheet[i][3]=width[i]
            sheet[i][4]=length[i]
            sheet[i][5]=center_distance[i]
            sheet[i][6]=x_var[i]
            sheet[i][7]=y_var[i]
        sheet = pd.DataFrame(sheet)
        
        '''
        #匯入rf tree 檔案
        df = pd.read_csv("data0309.csv")
        #去除與決策不相關之數據
        df.drop(['file'], axis=1, inplace=True)
        #確認結果資料型態
        Y = df["people"].values 
        Y=Y.astype('int')
        #創造訓練條件
        X = df.drop(labels = ["people"], axis=1)  
        
        from sklearn.model_selection import train_test_split
        #如果沒設random_state每次隨機取樣結果將不同
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.4, random_state=20)
        from sklearn.ensemble import RandomForestClassifier
        #model製作
        model = RandomForestClassifier(n_estimators = 10, random_state = 30)
        model.fit(X_train, y_train)
        prediction_test = model.predict(sheet)
        #sheet為此張圖片判斷出的物件特徵 prediction為 rf tree 判斷的結果
        sheet=sheet.values
        check_for_peop=0
        #print(prediction_test)
        for c in range(len(prediction_test)):
            if(prediction_test[c]==1): #將被判定為人的物件紀錄
                List_size_in_graph.append(sheet[c][0])  #把人的size放進array中
                total_node_size=total_node_size+sheet[c][0] #計算所有人物件的總數
                check_for_peop=1
                adjacency_pointx.append([])
                adjacency_pointy.append([])
                for i, j in zip(Listx[c],Listy[c]):
                    adjacency_pointx[adj_index].append(i) 
                    adjacency_pointy[adj_index].append(j) 
                adj_index =  adj_index+1
      
        #若此張圖片沒有被判斷為人的物件插入0
        if(check_for_peop==0):
            List_size_in_graph.append(0)
            
        '''
    count = count + 1
    





