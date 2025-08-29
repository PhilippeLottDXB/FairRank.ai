# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 15:02:09 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""Streamlit Condorcet Comparison Dashboard - Modular Version"""
import streamlit as st

import pandas as pd
import numpy as np
import plotly.graph_objs as go
#from information import jd, future_project, team_skills
#from comparisons import collect_comparison_data
from data_processing import load_data,compute_winner_scores,get_justifications_txt, data_cleanup
import os

models = ["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini",'o4-mini',"o3-mini","o1-mini"]
path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
model = models[0]

# ==== Data Utilities ====

def generate_sample_matrix(candidates, seed=42):
    """Generate a mock Condorcet pairwise win matrix"""
    np.random.seed(seed)
    matrix = np.asarray([
        [0, 0, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 1, 0, 1]
    ])
    return pd.DataFrame(matrix, index=candidates, columns=candidates)

def generate_justifications(matrix, candidates):
    """Create justifications for each pairwise comparison"""
    justifications = {}
    for i in range(len(candidates)):
        for j in range(len(candidates)):
            if i != j:
                key = f"{candidates[i]} vs {candidates[j]}"
                winner = candidates[i] if matrix.iloc[i, j] == 1 else candidates[j]
                justifications[key] = {
                    "winner": winner,
                    "justification": f"{winner} demonstrated stronger technical alignment and relevant experience than the other candidate."
                }
    return justifications

def create_hover_text(matrix, candidates, justifications):
    """Construct hover tooltips for Plotly heatmap"""
    hover_text = []
    for i in candidates:
        row = []
        for j in candidates:
            if i == j:
                row.append("")
            else:
                #print(i,j)
                #key = f"{candidates[i]} vs {candidates[j]}"
                winner = justifications[i][j]['winner']
                reason = justifications[i][j]['justification']
                text = f"🏆 Winner: {winner}<br>{reason}"
                row.append(text)
        hover_text.append(row)
    return hover_text

# ==== Visualization ====

def plot_comparison_heatmap(matrix, hover_text, candidates):
    """Generate Plotly heatmap of pairwise wins"""
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=candidates,
        y=candidates,
        text=hover_text,
        hoverinfo="text",
        colorscale="Blues",
        zmin=0,
        zmax=1,
    ))

    fig.update_layout(
        title="Pairwise Condorcet Win Matrix (Hover for Justification)",
        xaxis_title="Candidate (Column)",
        yaxis_title="Candidate (Row)",
        height=600,
    )

    return fig

# ==== Streamlit App ====

def main():
    st.set_page_config(page_title="Condorcet Dashboard", layout="wide")

    st.title("🎯 Condorcet-Based Candidate Comparison Matrix")
    base_path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
    model = "gpt-4o-mini"
    data = data_cleanup(load_data(model, base_path))
    
    raw_keys = list(data.keys())
    candidate_files = [os.path.basename(k) for k in raw_keys]

    overall_matrix, overall_scores = compute_winner_scores(candidate_files, base_path, data)
    justifications = get_justifications_txt(raw_keys, path, data)
    matrix = pd.DataFrame(overall_matrix)

    candidates = raw_keys#['A', 'B', 'C', 'D']

    hover_text = create_hover_text(matrix, candidates, justifications)
    fig = plot_comparison_heatmap(matrix, hover_text, candidates)

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()