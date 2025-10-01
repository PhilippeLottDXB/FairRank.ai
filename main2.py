from get_data import extract_text_from_pdf
import glob
import time
from comparisons_class import overall_manager
from information import jd, future_project, team_skills
#from Text_comparison_noGPT import compare_skill_lists
from jd_analysis_2 import get_key_skills
#from compar_base import summarize_rejections, self_audit_rejection, rebuttal_rejection
from export_word_pdf import build_docx_bytes, try_export_pdf,concatenate_pdfs
from GPT_link import request

"""
ri = ["CV Overall Quality (Grammar, Orthographe, Conjugation)",
      "Relevant Leadership Experience",
      "Communication Quality and Experience",
      "Relevant Technical Experience",
      "Relevant Technical Education"]
"""
#for f in features.keys():
#    for k in features[f]:
              
t0 = time.time()

path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
files_  = r"%s\*.pdf"%path
files = glob.glob(files_)
files = files[::3]
cvs = {}

# Exemple d’utilisation

for f in files[:]:
    contenu = extract_text_from_pdf(f)
    key = f.split("\\")[-1].split(".")[0]

    cvs[key]=contenu
    if False:
        cvs[key+"1"]=contenu
        cvs[key+"2"]=contenu
        cvs[key+"3"]=contenu
    #(self,cvs,model,jd,future_project,team_skills,ranking_information,progress_bar)

models = ["gpt-5","gpt-5-mini"]#,"gpt-4.1","o3-mini","o4-mini","o1-mini"]#,"gpt-4o-mini","gpt-4.1-mini"]
model = models[0]
npasses=2
ri = get_key_skills(jd,model,n_repeat=3*npasses)

print(request._total_usd)
model = models[0]

analyses = []

for r in range(npasses):
    analysis = overall_manager(cvs,model, jd, future_project, team_skills,ri)
    analysis.collect_information_data_MT(len(cvs))  
    analysis.condense_information_data()
    analyses.append(analysis)
    
print(request._total_usd)

all_pass = {}
all_pass_names = []
for analysis in analyses:
   for k in analysis.condorecet_selected:
       if k not in all_pass_names:
           all_pass_names.append(k)
           all_pass[k]=analysis.condorecet_selected[k]

q=1/0

reject_justifications = {}
accept_justifications = {}
accept_points = {}
for cv in cvs:
    accept_points[cv]=0
    if cv not in all_pass_names:
        reject_justifications[cv] = "The Summarized Justifications are:\n"
        for analysis in analyses:
            d0 = analysis.results[cv]["justification"]
            reject_justifications[cv] += d0+"\n"+30*"-"+"\n"
    else:
        accept_justifications[cv] = "The Summarized Justifications are:\n"
        for analysis in analyses:
            d0 = analysis.results[cv]["justification"]
            accept_justifications[cv] += d0+"\n"+30*"-"+"\n"            

for cv in cvs:
    for analysis in analyses:
        if analysis.results[cv]["final_decision"]=="Maybe":
            accept_points[cv]+=0.5
        elif analysis.results[cv]["final_decision"]=="Yes":
            accept_points[cv]+=1
            
for cv in cvs:
    accept_points[cv]=   accept_points[cv]/npasses             



print(request._total_usd)

from leagal_support import legal_process

legal_responses = legal_process(cvs, reject_justifications, jd, model=model)



pdfs_list = []

for cv,t3 in legal_responses.items():
    print(t3["candidate_name"])
    word_doc = build_docx_bytes(t3["candidate_name"], "CV rejection Reason", t3["reason_for_rejection"])
    pdf_bytes, method_info = try_export_pdf(word_doc.getvalue())
    
    pdfs_list.append(pdf_bytes)
    
reasoning = concatenate_pdfs(pdfs_list)

path2 = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR"

#with open("report.docx", "wb") as f:
#    f.write(reasoning)
with open(r"%s\report.pdf"%path2, "wb") as f:
    f.write(reasoning)

print(request._total_usd)
    
"""    
legal_responses = {}  
pdfs_list = [] 
for cv,text in reject_justifications.items():
    test = summarize_rejections(jd,cvs[cv],text,model="gpt-5-mini")
    print(test)
    t2 = self_audit_rejection(jd, cvs[cv], test,model="gpt-5-mini")
    print(t2)
    t3 = rebuttal_rejection(jd, cvs[cv], text, t2,model="gpt-5-mini")
    t3 = eval(t3)
    legal_responses[cv]=t3
    word_doc = build_docx_bytes(t3["candidate_name"], "CV rejection Reason", t3["reason_for_rejection"])
    pdf_bytes, method_info = try_export_pdf(word_doc.getvalue())
    pdfs_list.append(pdf_bytes)
"""    

#model = "gpt-5"
#analyses = analyses

print(all_pass_names)
for analysis in analyses:
    #analysis=analyses[model]
    analysis.update_model(model)
    analysis.condorecet_selected = all_pass
    analysis.condorecet_applicants = all_pass_names
    ct = len(all_pass)
    ct2 = (ct*(ct-1))/ct
    ct2 = min(ct2,200)
    analysis.collect_comparison_data_MT(int(ct2))
    analysis.compute_winner_scores()
    analysis.compute_category_scores()

ll = len(models)    
df_categories = {}
for k in analysis.cat_winners_df.keys():
    df_categories[k]=analysis.cat_winners_df[k]*0 
    for analysis in analyses:
        df_categories[k]=df_categories[k]+analysis.cat_winners_df[k]
    print(k)
    cc = df_categories[k].shape[0]-1
    print(df_categories[k]/ll)
    print(df_categories[k].sum(axis=0)/(ll*cc))

df0 = analyses[0].overall_matrix_pd*0 

for analysis in analyses:
    df0 = df0 + analysis.overall_matrix_pd
print(df0/(ll))
print(df0.sum(axis=0)/(ll*cc))
t1=time.time()
elapsed_time = t1-t0
print(elapsed_time)
print(float(request._total_usd)*1e-6)

    
#print("Contenu extrait :", contenu)