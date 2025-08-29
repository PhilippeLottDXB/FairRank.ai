# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:32:28 2025

@author: Admin
"""

from compar_base import compare_candidates_chatgpt,compare_candidates_against_offer_chatgpt
from retrieve_files import collect_texts
from information import jd, future_project, team_skills
from itertools import combinations
import pickle

models = ["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini",'o4-mini',"o3-mini","o1-mini"]

path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
model = models[0]

def collect_information_data(path,model,jd,future_project,team_skills,texts):
    #texts = collect_texts(path)
    results = {}
    for key,val in texts.items():
        information = compare_candidates_against_offer_chatgpt(val, jd,team_skills,future_project,model=model)
        i2 = information.replace('json','').replace("```","").replace("\n","").replace("```","")
        results[key]=eval(i2)
        print(key,'\n', information)
    return results

import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations

def collect_comparison_data_MT(path, model, jd, future_project, team_skills, texts):
    data = texts
    comparisons = {c: {} for c in data.keys()}

    def compare_pair(key1, val1, key2, val2):
        diff = compare_candidates_chatgpt(val1, val2, jd, team_skills, future_project, model=model)
        d2 = diff.replace('json', '').replace("```", "").replace("\n", "").replace("```", "")
        result = {
            "pair": (key1, key2),
            "direct": eval(d2),
            "inverse": eval(
                d2.replace('"A"', '"A0"').replace('"B"', '"B0"')
                   .replace(" A ", " A0 ").replace(" B ", " B0 ")
                   .replace('"A0"', '"B"').replace('"B0"', '"A"')
                   .replace(" A0 ", " B ").replace(" B0 ", " A ")
            ),
            "raw": diff
        }
        return result

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(compare_pair, key1, val1, key2, val2)
            for (key1, val1), (key2, val2) in combinations(data.items(), 2)
        ]
        for future in as_completed(futures):
            res = future.result()
            key1, key2 = res["pair"]
            comparisons[key1][key2] = res["direct"]
            comparisons[key2][key1] = res["inverse"]
            print(key1, key2, '\n', res["raw"])

    results = comparisons
    pickle.dump(results, open(path + r'/results_%s.pck' % model, "wb"))
    return results


def collect_comparison_data(path,model,jd,future_project,team_skills,texts):
    #texts = collect_texts(path)
    
    #lst = list(texts.values())
    #lst1=list(texts.keys())
    #e = compare_candidates_chatgpt(lst[0], lst[1], jd,team_skills,future_project)
    
    #def compare_entries(data):
    if True:
        data=texts
        comparisons = {}
        for c in data.keys():
            comparisons[c]={}
        for (key1, val1), (key2, val2) in combinations(data.items(), 2):
            diff = compare_candidates_chatgpt(val1, val2, jd,team_skills,future_project,model=model)               
            d2 = (diff.replace('json','').replace("```","").replace("\n","").replace("```",""))
            comparisons[key1][key2] = eval(d2)
            inverse0 = d2.replace('"A"','"A0"').replace('"B"','"B0"').replace(" A "," A0 ").replace(" B "," B0 ") 
            inverse = inverse0.replace('"A0"','"B"').replace('"B0"','"A"').replace(" A0 "," B ").replace(" B0 "," A ") 
            comparisons[key2][key1] = eval(inverse)
            print(key1,key2,'\n',diff)
    #return comparisons
    results = comparisons
    pickle.dump(results, open(path+r'/results_%s.pck'%model,"wb"))
    return results

def execute_investigation(texts,model,jd,future_project,team_skills):
    r2 = collect_information_data(path,model,jd,future_project,team_skills,texts)
    r1 = {}
    for key in r2.keys():
        if r2[key]["final_decision"] != "No":
            r1[key]=texts[key]
    results = collect_comparison_data(path,model,jd,future_project,team_skills,r1)   
    return results


if __name__ == "__main__":
    if True:
        results = execute_investigation(path,model,jd,future_project,team_skills)
        
    else:
    #results = collect_comparison_data(path,model,jd,future_project,team_skills)
        texts = collect_texts(path)
        r2 = collect_information_data(path,model,jd,future_project,team_skills,texts)
        r1 = {}
        for key in r2.keys():
            if r2[key]["final_decision"] != "No":
                r1[key]=texts[key]
        results = collect_comparison_data(path,model,jd,future_project,team_skills,r1)
        
# Example usage
#results = compare_entries(texts)
#for pair, diffs in results.items():
#    print(f"Comparison between {pair[0]} and {pair[1]}: {diffs}")
"""
winners = {}
for s in results[lst1[1]][lst1[0]]["category_winners"].keys():
    for k in lst1:
        ct = 0
        for j 
"""


