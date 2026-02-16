import pandas as pd
import csv

file=pd.read_csv("a.csv")
num=int(input("Enter number of entries: "))
for i in range(num):
    id=int(input("Id: "))
    sub=input("Subject: ")
    mark=int(input("Mark: "))

    with open("a.csv","a",newline="") as f:
        writer=csv.writer(f)
        writer.writerow([id,sub,mark])
        