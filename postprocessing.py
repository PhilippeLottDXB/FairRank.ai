# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 17:30:13 2025

@author: Admin
"""

import pickle
import pandas as pd
import difflib
from rapidfuzz import process, fuzz


def find_best_match(expected_key, actual_keys, scorer=fuzz.token_set_ratio, threshold=60):
    match = process.extractOne(
        expected_key,
        actual_keys,
        scorer=scorer,
        score_cutoff=threshold
    )
    return match[0] if match else None


def find_closest_key(expected_key, actual_keys, cutoff=0.6):
    # Returns the best match or None
    matches = difflib.get_close_matches(expected_key, actual_keys, n=1, cutoff=cutoff)
    return matches[0] if matches else None

#from comparisons import models

models = ["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini",'o4-mini',"o3-mini","o1-mini"]
model = models[5]
p2 = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database\results_%s.pck"%model
path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
#data = pickle.load(open(path+"\\data.pickle","rb"))
data = pickle.load(open(p2,"rb"))
keys = list(data.keys())

k2 = []
for k in keys:
    m = k.split("\\")[-1]
    k2.append(m)

data[keys[0]][keys[1]].keys()

overall_winners = {}
overall_winners_score = {}
for k in k2:
    overall_winners[k]={}
    p1 = path+"\\"+k
    score = 0
    for l in k2:
        p2 = path+"\\"+l
        if l == k:
            overall_winners[k][l]=0
        else:
            if data[p1][p2]["overall_winner"]=="A":
                overall_winners[k][l]=1
            elif data[p1][p2]["overall_winner"]=="B":
                overall_winners[k][l]=-1
            else:
                overall_winners[k][l]=0
        score+=overall_winners[k][l]
    overall_winners_score[k]=score
    
category_winners ={}
category_winners_score = {}
categories = ['Technical Acumen', 'Team Leadership','Communication Skills',
              'Relevant Experience','Complementarity','Project Alignment']

for c in categories:
    category_winners[c]={}
    category_winners_score[c]={}
    for k in k2:
        category_winners[c][k]={}
        p1 = path+"\\"+k
        score = 0
        for l in k2:
            p2 = path+"\\"+l
            if l == k:
                category_winners[c][k][l]=0
            else:
                if c not in data[p1][p2]["category_winners"].keys():
                    c2 = find_closest_key(c, list(data[p1][p2]["category_winners"].keys()))
                    if c2 is None:
                        c2 = find_best_match(c, list(data[p1][p2]["category_winners"].keys()))
                else:
                    c2 = c
                if data[p1][p2]["category_winners"][c2]=="A":
                    category_winners[c][k][l]=1
                elif data[p1][p2]["category_winners"][c2]=="B":
                    category_winners[c][k][l]=-1
                else:
                    category_winners[c][k][l]=0
            score+=category_winners[c][k][l]
        category_winners_score[c][k]=score    

category_winners["overall_winner"]=overall_winners
category_winners_score["overall_winner"]=overall_winners_score

df_winner = pd.DataFrame(category_winners_score)
df_winner.to_excel(path+r"/overall_results_%s.xlsx"%model)

for k in categories+["overall_winner"]:

    df = pd.DataFrame(category_winners[k])
    
    # Optional: make rows and columns in the same order
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reindex(sorted(df.index), axis=0)
            #d = data[""]
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Assuming df is your 2D comparison DataFrame
    plt.figure(figsize=(8, 6))
    sns.heatmap(df, annot=True, cmap="YlGnBu", fmt=".2f")
    
    plt.title("Comparison Heatmap : %s"%k)
    plt.show()
    
    # Sort by value (descending)
    sorted_dict = dict(sorted(category_winners_score[k].items(), key=lambda item: item[1], reverse=True))
    print("\n--------------------\ncategory %s"%k)
    # Print nicely
    for filename, score in sorted_dict.items():
        print(f"{filename}: {score}")
# Sort by value (ascending)




