import streamlit as st
#from Utilities.retrieve_files import collect_texts,extract_text_from_pdf
import PyPDF2
#import sys
#from pathlib import Path
#import random
from leagal_support import legal_process

from jd_analysis_2 import get_key_skills
from comparisons_class import overall_manager
#from data_processing import compute_winner_scores
#from compar_base import summarize_rejections, self_audit_rejection, rebuttal_rejection
from export_word_pdf import build_docx_bytes, try_export_pdf, concatenate_pdfs
#sys.path.append(r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\Testing_StreamLit\Utilities")


flag = True

st.title("Upload & Submit")

uploaded_file = st.file_uploader("Upload Candidates CVs",accept_multiple_files=True, type="pdf")

#files = st.session_state.get("files", [])

if flag:

    number_of_passes = st.selectbox("Choose the number of passes", [1,3,5,7,10])
    
    model_quality = st.selectbox("Choose the Models Quality",["Labor/Entry level jobs",
                                                              "Sales/mid level technical",
                                                              "Good Technical/Leadership",
                                                              "Executive/Managerial"])
    #st.text_area("""Services Levels:\n
    #             Level 1: Removal of Irrelevant Applicants Only\n
    #             Level 2: Level 1 + Rejection & Acceptance Justification\n
    #             Level 3: Level 2 + Sorting Relevant Candidates\n
    #             Level 4: Level 3 + Providing Audit Results""")

    service = st.selectbox("Choose service Settings",
                           ["Level 1",
                            "Level 2",
                            "Level 3",
                            "level 4"])
    
    n_cols = 3
    
    Token_Service = {"Level 1":1,"Level 2":2,"level 3":5,"level 4":10}
    service_selected = Token_Service[service]
    
    Token_Model = {"Labor/Entry level jobs":1,#,"gpt-4o-mini","gpt-4.1-mini"],
                  "Sales/mid level technical":2,#,"o4-mini","o1-mini"],
                  "Good Technical/Leadership":3,#,"o3-mini","o4-mini","o1-mini","gpt-4.1"],
                  "Executive/Managerial":4}
    
    Models = {"Labor/Entry level jobs":"gpt-5-mini",#,"gpt-4o-mini","gpt-4.1-mini"],
              "Sales/mid level technical":"gpt-5-mini",#,"o4-mini","o1-mini"],
              "Good Technical/Leadership":"gpt-5-mini",#,"o3-mini","o4-mini","o1-mini","gpt-4.1"],
              "Executive/Managerial":"gpt-5"}#,"gpt-5-mini","o3","o1"]}
    models = ["gpt-5","gpt-5-mini","o3-mini","o4-mini","o1-mini","gpt-4o-mini","gpt-4.1-mini"]

    price = Token_Model[model_quality]*Token_Service[service]*number_of_passes

    #st.text_area("The price of this analysis", value=price)


if flag:
    models = Models[model_quality]
    

    job_description = st.text_area("Detailed Job Description:", 
                                       placeholder="Please paste the job description here, the more details the finer the analysts")
                                       
    team_skills = "None"#st.text_area("Skills already available in the team and in the department:", 
                        #         placeholder="Please list the skills that are already available in the department, for which you may not need redundancy") 

    future_projects = "Not Available"#st.text_area("List future types of projects that the candidate may be facing:", 
                                     #placeholder="Please list potential future projects to understand how the candidate can complement your team in long term")                             

if st.button("Submit"):
    if uploaded_file:

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
            #dct[(file.name).replace(".pdf","2.pdf")]=text
            #dct[(file.name).replace(".pdf","3.pdf")]=text
            #dct[(file.name).replace(".pdf","4.pdf")]=text

        st.subheader("📄 analyzing the Job Description")
        #progress_bar_0 = st.progress(0)
        print(models)
        selected_features = get_key_skills(job_description, models,n_repeat=number_of_passes*3)
        #print(uploaded_file)

        #for f in dct.keys():
            #print(dct[f][:1000])

    # Do something with content
        st.session_state["candidates"]=dct
        ll = 1
        st.session_state["model"] = models#[:min(number_of_passes,ll)]
        st.session_state["n_pass"]=number_of_passes
        #option1
        if flag:
            st.session_state["candidate_features"]=selected_features#candidate_features.split(";")
            st.session_state["job_description"]=job_description
            st.session_state["team_skills"]=team_skills
            st.session_state["future_projects"]=future_projects
            #print(st.session_state["candidate_features"])
        if service_selected>=1:
        # Do your processing or validation here
            st.subheader("📄 Pass #1: removing irrelevant Candidates")
        
            progress_bar = {} 
            analyses  = []
            prog = st.progress(0)
            total = st.session_state["n_pass"]#len(st.session_state["model"])
            ct = 0
            
            for k in range(st.session_state["n_pass"]):
                #progress_bar[m] = None#st.progress(0)
                m = st.session_state["model"]
                cvs = st.session_state["candidates"]
                analysis = overall_manager(st.session_state["candidates"],
                                           m,
                                           st.session_state["job_description"], 
                                           st.session_state["future_projects"],
                                           st.session_state["team_skills"],
                                           st.session_state["candidate_features"])
                                           #progress_bar[m].progress)
                num_threads = len(st.session_state["candidates"])
                analysis.collect_information_data_MT(num_threads)  
                analyses.append(analysis)
                ct+=1
                prog.progress(int(100*ct/total))
                print("pass # %d"%k)
            prog.progress(int(100))
            all_pass = {}
            all_pass_names = []
            accept_points = {}
            for analysis in analyses:
               for k in analysis.condorecet_selected:
                   if k not in all_pass_names:
                       all_pass_names.append(k)
                       all_pass[k]=analysis.condorecet_selected[k]   
            print("Selection finished")
            for cv in cvs:
                accept_points[cv]=0
                for analysis in analyses:
                    if analysis.results[cv]["final_decision"]=="Maybe":
                        accept_points[cv]+=0.5
                    elif analysis.results[cv]["final_decision"]=="Yes":
                        accept_points[cv]+=1
            if service_selected == 1:
                print("RATINGS PRINT")
                import matplotlib.pylab as plt
                filtered = {k: v for k, v in accept_points.items() if v > 0}
                sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
                
                # Split into names and values
                names = [item[0] for item in sorted_items]
                values = [100*item[1]/number_of_passes for item in sorted_items]
                
                # Create the horizontal bar chart
                fig, ax = plt.subplots()
                ax.barh(names, values, color="skyblue")
                ax.set_xlabel("Grades")
                ax.set_title("Percentage of Approvals")
                
                # Invert y-axis so highest values are at the top
                ax.invert_yaxis()
                
                # Show in Streamlit
                st.pyplot(fig)
# Streamlit bar chart (horizontal by swapping axes)



        if service_selected>=2:
            st.subheader("📄 Pass #2: Ranking Relevant Candidates")    
            prog2 = st.progress(0)        

            
            #if len(all_pass_names)>30:
            reject_justifications = {}
            crcs = 0
            for cv in cvs:
                if cv not in all_pass_names:
                    crcs+=1
                    reject_justifications[cv] = "The Summarized Justifications are:\n"
                    for analysis in analyses:
                        if cv in analysis.results.keys(): 
                            d0 = analysis.results[cv]["justification"]
                            reject_justifications[cv] += d0+"\n"+30*"-"+"\n"
        
            jd = st.session_state["job_description"]
            m0  = "gpt-5-mini"
            
            
            legal_responses = legal_process(cvs, reject_justifications, jd, model="gpt-5-mini")
            pdfs_list = []
            
            for cv,t3 in legal_responses.items():
                print(t3["candidate_name"])
                word_doc = build_docx_bytes(t3["candidate_name"], "CV rejection Reason", t3["reason_for_rejection"])
                pdf_bytes, method_info = try_export_pdf(word_doc.getvalue())
                if pdf_bytes:
                    pdfs_list.append(pdf_bytes)
                    print(t3)
                
            #reasoning = concatenate_pdfs(pdfs_list)
        
            print(len(pdfs_list))
            reports = concatenate_pdfs(pdfs_list)
            st.session_state["reject_reports"]=reports
        
        if service_selected>=3:        
            ct2 = 0           
            for analysis in analyses:
                #analysis=analyses[model]
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
        
            ll = total#len(st.session_state["model"])    
            df_categories = {}
            for k in analysis.cat_winners_df.keys():
                df_categories[k]=analysis.cat_winners_df[k]*0 
                for analysis in analyses:
                    df_categories[k]=df_categories[k]+analysis.cat_winners_df[k]
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
        if service_selected>2:
            st.success("Done! Check the Results page.")
            st.switch_page("pages/2_Results.py")


    else:
        st.warning("Please upload a file first.")