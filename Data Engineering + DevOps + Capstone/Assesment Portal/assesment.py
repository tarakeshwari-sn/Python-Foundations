import difflib
import numpy as np
import os 
import subprocess
import json
import csv
import PyPDF2
import re
import filedialpy

def load_questions(file_path):
    file_path=os.path.abspath(file_path)
    text=""
    ext=os.path.splitext(file_path)[1].lower()
    if ext in ['.txt','.md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text=f.read()

    elif ext=='.csv':
        with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
            reader=csv.DictReader(f)
            for row in reader:
                for key, value in row.items():
                    if value and not value.replace('.', '', 1).isdigit(): 
                        text += str(value) + " "

    elif ext=='.pdf':
        try:
            with open(file_path, 'rb') as f:
                reader=PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text=page.extract_text()
                    if page_text:
                        text += page_text + " "
        except:
            print("Error reading PDF file")
    else:
        try:
            with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
                text=f.read()
        except:
            print(f"Cannot read file {file_path}")
            return []
        
    sentences=re.split(r'[.?]', text)
    questions=[s.strip() for s in sentences if len(s.split()) > 3]
    return questions

def isdistinct(questions,threshold=0.8):
    distinct=[]
    for q in questions:
        is_duplicate=False
        for e in distinct:
            sim=difflib.SequenceMatcher(None,q,e).ratio()
            if sim>= threshold:
                is_duplicate=True
                break
        if not is_duplicate:
            distinct.append(q)
    return distinct    

def split_q(players, questions):
    q_per_player=len(questions) // len(players)
    extra_q=len(questions) % len(players)
    paper={}
    np.random.shuffle(questions)
    idx=0
    for player in players:
        count=q_per_player
        paper[player]=questions[idx:idx+count]
        idx+= count
    global leftovers
    leftovers=questions[idx:idx+extra_q]
    return paper

def main():
    players_num=int(input("Enter number of participants: "))
    players=[]
    for _ in range(players_num):
        name=input("Enter player name: ")
        players.append(name)
        print(f"{name} saved.")

    print("\n Select question file. Ensure the file uses '?' or '.' as delimiters.") 

    file_path = filedialpy.openFile()
    questions=load_questions(file_path)
    distinct_questions=isdistinct(questions)
    print("\nDistinct Questions:")
    for q in distinct_questions:
        print(q)
    
    distribution=split_q(players,distinct_questions)
    print("\nQuestion Distribution:")
    for player, qs in distribution.items():
        print(f"{player}:")
        for q in qs:
            print(f"  - {q}")
    if leftovers:
        print("\nLeftover Questions:")
        for q in leftovers:
            print(q)
main()