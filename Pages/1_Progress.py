import streamlit as st
import time
from comparisons_class import overall_manager
from data_processing import compute_winner_scores

st.title("Processing...")
if "candidates" in st.session_state:
    st.subheader("📄 Pass #1: removing irrelevant Candidates")

    progress_bar = {} 
    analyses  = {}
    prog = st.progress(0)
    total = len(st.session_state["model"])
    ct = 0
    
    for m in st.session_state["model"]:
        progress_bar[m] = None#st.progress(0)
        
        analysis = overall_manager(st.session_state["candidates"],
                                   m,
                                   st.session_state["job_description"], 
                                   st.session_state["future_projects"],
                                   st.session_state["team_skills"],
                                   st.session_state["candidate_features"])
                                   #progress_bar[m].progress)
        num_threads = len(st.session_state["candidates"])
        analysis.collect_information_data_MT(num_threads)  
        analyses[m]=analysis
        ct+=1
        prog.progress(int(100*ct/total))
    prog.progress(int(100))
        
    st.subheader("📄 Pass #2: Ranking Relevant Candidates")    
    
    prog2 = st.progress(0)
    all_pass = {}
    all_pass_names = []
    for model in st.session_state["model"]:
       for k in analyses[model].condorecet_selected:
           if k not in all_pass_names:
               all_pass_names.append(k)
               all_pass[k]=analyses[model].condorecet_selected[k]
    
    ct2 = 0           
    for model in st.session_state["model"]:
        analysis=analyses[model]
        analysis.condorecet_selected = all_pass
        analysis.condorecet_applicants = all_pass_names
        nshort = len(all_pass_names)
        num_threads = nshort*(nshort+1)/2
        analysis.collect_comparison_data_MT(num_threads)
        analysis.compute_winner_scores()
        analysis.compute_category_scores()
        ct2+=1
        prog2.progress(int(100*ct2/total)) 
    prog2.progress(int(100))

    ll = len(st.session_state["model"])    
    df_categories = {}
    for k in analysis.cat_winners_df.keys():
        df_categories[k]=analysis.cat_winners_df[k]*0 
        for m in st.session_state["model"]:
            df_categories[k]=df_categories[k]+analyses[m].cat_winners_df[k]
        print(k)
        cc = df_categories[k].shape[0]-1
        print(df_categories[k]/ll)
        print(df_categories[k].sum(axis=0)/(ll*cc))
    st.session_state["results"]=analysis
    #results = comparisons.execute_investigation(st.session_state["candidates"],st.session_state["model"],
    #                                  st.session_state["job_description"],st.session_state["future_projects"],
    #                                  st.session_state["team_skills"])
                                      
    #raw_keys = list(results.keys())
    #candidate_files = [k for k in raw_keys]

    #overall_matrix, overall_scores = compute_winner_scores(candidate_files, results)
    
    #st.session_state["overall"]={"scores":overall_scores,"matrix":overall_matrix}
    #for i in range(100):
    #    time.sleep(0.02)
    #    progress_bar.progress(i + 1)
    st.success("Done! Check the Results page.")
    st.switch_page("pages/2_Results.py")
else:
    st.warning("No file submitted yet.")