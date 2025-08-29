# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 15:00:13 2025

@author: Admin
"""

import os
import pickle
import pandas as pd
import difflib
from rapidfuzz import process, fuzz
import seaborn as sns
import matplotlib.pyplot as plt
#from matrix_justifications import plot_comparison_heatmap

# ---------- Match Utilities ----------
def find_best_match(expected_key, actual_keys, scorer=fuzz.token_set_ratio, threshold=60):
    """Use RapidFuzz to find best approximate match above a threshold."""
    match = process.extractOne(expected_key, actual_keys, scorer=scorer, score_cutoff=threshold)
    return match[0] if match else None

def find_closest_key(expected_key, actual_keys, cutoff=0.6):
    """Use difflib for fuzzy match based on similarity ratio."""
    matches = difflib.get_close_matches(expected_key, actual_keys, n=1, cutoff=cutoff)
    return matches[0] if matches else None

# ---------- Data Load ----------
def load_data(model_name, base_path):
    path = os.path.join(base_path, f"results_{model_name}.pck")
    with open(path, "rb") as f:
        return pickle.load(f)

# ---------- Score Calculation ----------
def compute_winner_scores(keys, data):
    scores = {}
    matrix = {}

    for a in keys:
        matrix[a] = {}
        p1 = a## os.path.join(path, a)
        total = 0
        for b in keys:
            p2 = b# os.path.join(path, b)
            if a == b:
                matrix[a][b] = 0
            else:
                result = data[p1][p2]["overall_winner"]
                matrix[a][b] = 1 if result == "A" else -1 if result == "B" else 0
            total += matrix[a][b]
        scores[a] = total
    return matrix, scores

def compute_category_scores(keys, path, data, categories):
    winners = {c: {} for c in categories}
    scores = {c: {} for c in categories}

    for category in categories:
        for a in keys:
            winners[category][a] = {}
            p1 = a#os.path.join(path, a)
            total = 0
            for b in keys:
                p2 = b# os.path.join(path, b)
                if a == b:
                    winners[category][a][b] = 0
                else:
                    d = data[p1][p2]["category_winners"]
                    c_key = category if category in d else find_closest_key(category, d.keys()) or find_best_match(category, d.keys())
                    result = d.get(c_key, None)
                    winners[category][a][b] = 1 if result == "A" else -1 if result == "B" else 0
                total += winners[category][a][b]
            scores[category][a] = total
    return winners, scores

# ---------- Visualization ----------
def plot_heatmap(matrix, title):
    df = pd.DataFrame(matrix)
    df = df.reindex(sorted(df.index), axis=0).reindex(sorted(df.columns), axis=1)

    plt.figure(figsize=(8, 6))
    sns.heatmap(df, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title(f"Comparison Heatmap : {title}")
    plt.show()

    return df
def get_justifications(keys, path, data):
    matrix = {}
    for a in keys:
        matrix[a] = {}
        p1 = a #os.path.join(path, a)
        for b in keys:
            p2 = b#os.path.join(path, b)
            if a == b:
                matrix[a][b] = ""
            else:
                matrix[a][b] = data[p1][p2]["justification"]
    return matrix

def get_justifications_txt(keys, path, data):
    matrix = {}
    for a in keys:
        matrix[a] = {}
        p1 = a #os.path.join(path, a)
        for b in keys:
            p2 = b#os.path.join(path, b)
            if a == b:
                matrix[a][b] = {}
                matrix[a][b]["winner"] = "A"
                matrix[a][b]["justification"] = ""
            else:
                matrix[a][b] = {}
                matrix[a][b]["justification"] = data[p1][p2]["justification"]
                if data[a][b]["overall_winner"] == "A":
                    matrix[a][b]["winner"] = a
                elif data[a][b]["overall_winner"] == "B":
                    matrix[a][b]["winner"] = b
                else:
                    matrix[a][b]["winner"] = "Tie"
    return matrix

def data_cleanup(data):
    d2 = {}
    for d in data.keys():
        d1 = d.split("\\")[-1].split(".")[0]
        d2[d1]={}
        for d3 in data[d].keys():
            d4 = d3.split("\\")[-1].split(".")[0]
            d2[d1][d4]=data[d][d3]
    return d2


# ---------- Main ----------
#def main():

if __name__ == "__main__":
   
    base_path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
    model = "gpt-4o-mini"
    data = data_cleanup(load_data(model, base_path))
    raw_keys = list(data.keys())
    candidate_files = [k for k in raw_keys]

    overall_matrix, overall_scores = compute_winner_scores(candidate_files, data)

    categories = [
        'Technical Acumen', 'Team Leadership', 'Communication Skills',
        'Relevant Experience', 'Complementarity', 'Project Alignment'
    ]
    cat_matrices, cat_scores = compute_category_scores(candidate_files, base_path, data, categories)
    justifications = get_justifications(candidate_files, base_path, data)
    # Merge overall into category dictionaries
    cat_matrices["overall_winner"] = overall_matrix
    cat_scores["overall_winner"] = overall_scores

    # Export results
    pd.DataFrame(cat_scores).to_excel(os.path.join(base_path, f"overall_results_{model}.xlsx"))

    # Visualize & Print
    for category in categories + ["overall_winner"]:
        df = plot_heatmap(cat_matrices[category], category)
        sorted_scores = sorted(cat_scores[category].items(), key=lambda item: item[1], reverse=True)
        print(f"\n--- Category: {category} ---")
        for name, score in sorted_scores:
            print(f"{name}: {score}")
    #plot_comparison_heatmap(overall_scores, justifications, candidate_files)
    #return justifications

#if __name__ == "__main__":
#    j = main()