import streamlit as st
#from Utilities.retrieve_files import collect_texts,extract_text_from_pdf
import PyPDF2
import sys
from pathlib import Path
import random
from jd_analysis_2 import get_key_skills
sys.path.append(r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\Testing_StreamLit\Utilities")


flag = True

st.title("Upload & Submit")

uploaded_file = st.file_uploader("Upload Candidates CVs",accept_multiple_files=True, type="pdf")

#files = st.session_state.get("files", [])

if flag:

    number_of_passes = st.selectbox("Choose the number of passes", [1,2,3,4,5])
    
    model_quality = st.selectbox("Choose the Models Quality",["Labor/Entry level jobs",
                                                              "Sales/mid level technical",
                                                              "Good Technical/Leadership",
                                                              "Executive/Managerial"])
    
    n_cols = 3
    
    
    Models = {"Labor/Entry level jobs":["gpt-5-mini","gpt-4o-mini","gpt-4.1-mini"],
              "Sales/mid level technical":["gpt-5-mini","o4-mini","o1-mini"],
              "Good Technical/Leadership":["gpt-5","gpt-5-mini","o3-mini","o4-mini","o1-mini","gpt-4.1"],
              "Executive/Managerial":["gpt-5","gpt-5-mini","o3","o1"]}
    models = ["gpt-5","gpt-5-mini","o3-mini","o4-mini","o1-mini","gpt-4o-mini","gpt-4.1-mini"]
else:
    option1 = st.selectbox("Choose a model", ["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini",'o4-mini',"o3","o3-mini"])

if flag:
    models = Models[model_quality][:number_of_passes]

    job_description = st.text_area("Detailed Job Description:", 
                                       placeholder="Please paste the job description here, the more details the finer the analysts")
                                       
    team_skills = "None"#st.text_area("Skills already available in the team and in the department:", 
                        #         placeholder="Please list the skills that are already available in the department, for which you may not need redundancy") 

    future_projects = "Not Available"#st.text_area("List future types of projects that the candidate may be facing:", 
                                     #placeholder="Please list potential future projects to understand how the candidate can complement your team in long term")                             

if st.button("Submit"):
    if uploaded_file:
        st.subheader("📄 analyzing the Job Description")
        #progress_bar_0 = st.progress(0)
        selected_features = get_key_skills(job_description, models)
        #print(uploaded_file)
        st.subheader("📄 Uploading files")
        progress_bar = st.progress(0)
        nfiles = len(uploaded_file)
        ct = 0
        dct = {}
        for file in uploaded_file:
            ct+=1
            pct = int(100*ct/nfiles)
            progress_bar.progress(pct)
            #print(file.name)
            #st.subheader(f"📄 {file.name}")
            # Read the PDF content
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            dct[file.name]=text
        #for f in dct.keys():
            #print(dct[f][:1000])

    # Do something with content
        st.session_state["candidates"]=dct
        ll = len(Models[model_quality])
        st.session_state["model"] = Models[model_quality][:min(number_of_passes,ll)]
        #option1
        if flag:
            st.session_state["candidate_features"]=selected_features#candidate_features.split(";")
            st.session_state["job_description"]=job_description
            st.session_state["team_skills"]=team_skills
            st.session_state["future_projects"]=future_projects
            #print(st.session_state["candidate_features"])
        
    # Do your processing or validation here

        st.success("Submitted! Go to the Progress page.")
        st.switch_page("1_Progress.py")

    else:

        st.warning("Please upload a file first.")
