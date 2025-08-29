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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from rapidfuzz import process, fuzz
import difflib
import pandas as pd

models = ["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini",'o4-mini',"o3-mini","o1-mini"]

path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
model = models[0]

def find_best_match(expected_key, actual_keys, scorer=fuzz.token_set_ratio, threshold=60):
    """Use RapidFuzz to find best approximate match above a threshold."""
    match = process.extractOne(expected_key, actual_keys, scorer=scorer, score_cutoff=threshold)
    return match[0] if match else None

def find_closest_key(expected_key, actual_keys, cutoff=0.6):
    """Use difflib for fuzzy match based on similarity ratio."""
    matches = difflib.get_close_matches(expected_key, actual_keys, n=1, cutoff=cutoff)
    return matches[0] if matches else None

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

class overall_manager:
    def __init__(self,cvs,model,jd,future_project,team_skills,ranking_information,progress_bar=None):
        self.debug = True
        self.cvs = cvs
        self.model = model
        self.jd = jd 
        self.future_project = future_project
        self.team_skills = team_skills
        self.ranking_information = ranking_information
        self.progress_bar = progress_bar
        cvs_count = len(list(cvs.keys()))
        self.cvs_count_0 = cvs_count
        self.total_calls = cvs_count+0.14*(cvs_count)**2
        self.ct = 0
        self.applicants = list(cvs.keys())
        self.update_lock = threading.Lock()
        
        
    def update_progress_bar(self):
        self.ct += 1
        pct =  self.ct/self.total_calls
        if pct>1:
            pct=1
        if self.progress_bar is not None:
            self.progress_bar(int(pct*100))
            
        
    def collect_information_data(self):
        #texts = collect_texts(path)
        self.results = {}
        for key,val in self.cvs.items():
            information = compare_candidates_against_offer_chatgpt(val, self.jd,self.team_skills,
                                                                   self.future_project,self.model,self.ranking_information)
            i2 = information.replace('json','').replace("```","").replace("\n","").replace("```","")
            self.results[key]=eval(i2)
            self.update_progress_bar()
            if self.debug:
                print(key,'\n', information)
        
        #return self.results
        r1 = {}
        for key in self.results.keys():
            if self.results[key]["final_decision"] != "No":
                r1[key]=self.cvs[key]
        self.successful_applicants = list(r1.keys())
        cvs_count_1 = len(list(r1.keys()))
        self.total_calls = self.cvs_count_0 + 0.5*(cvs_count_1**2-cvs_count_1)
        self.condorecet_selected = r1
        self.condorecet_applicants = r1.keys()
        
    def collect_information_data_MT(self, num_threads=4):
        """
        Compare each CV against the offer in parallel.
        :param num_threads: Number of worker threads to use.
        """
        self.results = {}
        # Internal worker: processes one (key, val) pair
        def worker(item):
            key, val = item
            # Submit to server
            info = compare_candidates_against_offer_chatgpt(
                val,
                self.jd,
                self.team_skills,
                self.future_project,
                self.model,
                self.ranking_information
            )
            # Clean up JSON-like wrapper
            payload = info.replace('json', '') \
                          .replace("```", "") \
                          .replace("\n", "")
            result = eval(payload)
            # Safely update shared structures
            with self.update_lock:
                self.results[key] = result
                self.update_progress_bar()
                if self.debug:
                    print(f"{key}\n{info}")
            return key, result

        # Kick off threads
        items = list(self.cvs.items())
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, item) for item in items]
            for future in as_completed(futures):
                # Can handle exceptions here if needed
                try:
                    future.result()
                except Exception as e:
                    print("Error processing CV:", e)

        # Post-processing: filter successful applicants
        filtered = {
            key: self.cvs[key]
            for key, res in self.results.items()
            if res.get("final_decision") != "No"
        }

        self.successful_applicants = list(filtered.keys())
        cvs_count_1 = len(self.successful_applicants)
        self.total_calls = (
            len(self.cvs)
            + 0.5 * (cvs_count_1**2 - cvs_count_1)
        )
        self.condorecet_selected = filtered
        self.condorecet_applicants = filtered.keys()    
        
    def collect_comparison_data(self):
        #texts = collect_texts(path)
        
        #lst = list(texts.values())
        #lst1=list(texts.keys())
        #e = compare_candidates_chatgpt(lst[0], lst[1], jd,team_skills,future_project)
        
        #def compare_entries(data):
        if True:
            comparisons = {}
            for c in self.condorecet_selected.keys():
                comparisons[c]={}
            for (key1, val1), (key2, val2) in combinations(self.condorecet_selected.items(), 2):
                diff = compare_candidates_chatgpt(val1, val2, self.jd,self.team_skills,self.future_project,self.model,self.ranking_information)               
                d2 = (diff.replace('json','').replace("```","").replace("\n","").replace("```",""))
                comparisons[key1][key2] = eval(d2)
                inverse0 = d2.replace('"A"','"A0"').replace('"B"','"B0"').replace(" A "," A0 ").replace(" B "," B0 ") 
                inverse = inverse0.replace('"A0"','"B"').replace('"B0"','"A"').replace(" A0 "," B ").replace(" B0 "," A ") 
                comparisons[key2][key1] = eval(inverse)
                self.update_progress_bar()
                if self.debug:
                    print(key1,key2,'\n',diff)
        #return comparisons
        self.results = comparisons
        #pickle.dump(results, open(path+r'/results_%s.pck'%model,"wb"))
        return self.results
        


    def collect_comparison_data_MT(self, num_threads=4):
        """
        Compare each pair of selected candidates in parallel.
        :param num_threads: Number of worker threads to use.
        :return: Nested dict of pairwise comparison results.
        """

        # Initialize empty comparison buckets
        comparisons = {
            key: {} for key in self.condorecet_selected.keys()
        }

        def worker(pair):
            key1, val1 = pair[0]
            key2, val2 = pair[1]
            # Call remote comparison API
            diff = compare_candidates_chatgpt(
                val1, val2,
                self.jd, self.team_skills, self.future_project,
                self.model, self.ranking_information
            )
            # Clean up payload
            cleaned = diff.replace('json', '') \
                          .replace("```", "") \
                          .replace("\n", "")
            result = eval(cleaned)

            # Build inverse mapping
            inv = cleaned.replace('"A"', '"A0"') \
                         .replace('"B"', '"B0"') \
                         .replace(" A ", " A0 ") \
                         .replace(" B ", " B0 ")
            inv = inv.replace('"A0"', '"B"') \
                     .replace('"B0"', '"A"') \
                     .replace(" A0 ", " B ") \
                     .replace(" B0 ", " A ")
            inverse_result = eval(inv)

            # Safely update shared structure
            with self.update_lock:
                comparisons[key1][key2] = result
                comparisons[key2][key1] = inverse_result
                self.update_progress_bar()
                if self.debug:
                    print(f"{key1} vs {key2}\n{diff}")

        # Prepare all unique pairs
        pairs = list(combinations(self.condorecet_selected.items(), 2))

        # Execute in thread pool
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, pair) for pair in pairs]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print("Error during comparison:", e)

        # Store and return
        self.results = comparisons
        return self.results

    # ---------- Score Calculation ----------
    def compute_winner_scores(self):
        self.overall_scores = {}
        self.overall_matrix = {}

        for a in self.condorecet_applicants:
            self.overall_matrix[a] = {}
            total = 0
            for b in self.condorecet_applicants:
                if a == b:
                    self.overall_matrix[a][b] = 0
                else:
                    try:
                        result = self.results[a][b]["overall_winner"]
                        self.overall_matrix[a][b] = 1 if result == "A" else -1 if result == "B" else 0
                    except:
                        self.overall_matrix[a][b] = 0
                total += self.overall_matrix[a][b]
            self.overall_scores[a] = total
        self.overall_matrix_pd = pd.DataFrame(self.overall_matrix)
        #return matrix, scores

    def compute_category_scores(self):
        self.cat_winners = {c: {} for c in self.ranking_information}
        self.cat_scores = {c: {} for c in self.ranking_information}
        self.cat_winners_df = {c: {} for c in self.ranking_information}

        for category in self.ranking_information:
            for a in self.condorecet_selected:
                self.cat_winners[category][a] = {}
                total = 0
                for b in self.condorecet_selected:
                    if a == b:
                        self.cat_winners[category][a][b] = 0
                    else:
                        d = self.results[a][b]["category_winners"]
                        c_key = category if category in d else find_closest_key(category, d.keys()) or find_best_match(category, d.keys())
                        result = d.get(c_key, None)
                        self.cat_winners[category][a][b] = 1 if result == "A" else -1 if result == "B" else 0
                    total += self.cat_winners[category][a][b]
                self.cat_scores[category][a] = total
            self.cat_winners_df[category] = pd.DataFrame(self.cat_winners[category])
        return self.cat_winners, self.cat_scores,self.cat_winners_df



def collect_comparison_data_MT(path, model, jd, future_project, team_skills, texts):
    data = texts
    comparisons = {c: {} for c in data.keys()}



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


"""
def execute_investigation(texts,model,jd,future_project,team_skills):
    r2 = collect_information_data(texts,model,jd,future_project,team_skills,texts)
    r1 = {}
    for key in r2.keys():
        if r2[key]["final_decision"] != "No":
            r1[key]=texts[key]
    results = collect_comparison_data(texts,model,jd,future_project,team_skills,r1)   
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

winners = {}
for s in results[lst1[1]][lst1[0]]["category_winners"].keys():
    for k in lst1:
        ct = 0
        for j 
"""


