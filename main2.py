from get_data import extract_text_from_pdf
import glob
from comparisons_class import overall_manager
from information import jd, future_project, team_skills
from Text_comparison_noGPT import compare_skill_lists
from jd_analysis_2 import get_key_skills

ri = ["Technical Acumen","Team Leadership",
"Communication Skills","Relevant Experience",
"Complementarity with the existing team",
"Alignment with Ongoing & Future Projects",
"Political Exposure","Strategy know-how",
"Probability of the CV being writtent by AI",
"CV Overall Quality (Grammar, Orthographe, Conjugation)"]

features = {"Leadership":["Relevant Leadership Experience",
                          "Communication Quality and Experience",
                          "Mentoring Capabilities and Skills",
                          "Mentoring Experience",
                          "Team Building Experience",
                          "Cross Functional Influence",
                          "Conflict Resolution Abilities",
                          "Individual Coaching Experience",
                          "Leadership Development Experience",
                          "Ability to handle ambiguity",
                          "Successions Readiness",
                          ],
            "Higher Level":["Stakeholder Management",
                            "Ability to prepare a succession",
                            "Political Exposure","Strategy know-how",
                            "Decision Making",
                            "Executive Leadership Experience",
                            "Leadership Development Experience",
                            ],
            "Technical" :["Relevant Technical Experience",
                          "Relevant Technical Education",
                          "Attention to detail",
                          "Ability to work and deliver projects",
                          "Systems Thinking Ability",
                          "Innovation Capacity",
                          ],
            "Company"   :["Available Team complementarty",
                          "Suitability for future projects",
                          "Values Alignment",
                          "Mission Drive",
                          "Loyalty",    
                          "Overall suitability for the role",
                          "Cultural and organizational fit",
                          ],
            "Candidate" :["Resilience and bounce back history",
                          "Team work","kindness",
                          "CV Overall Quality (Grammar, Orthographe, Conjugation)",
                          "Role Stretch Potential",
                          "Professional Narrative and Consistency",
                          "International Exposure",
                          "Adaptability and versatiloty",
                          "Growth mindset","Authenticity and Originality",
                          "Potential Relevant Technical Network",
                          "Probability of the CV being writtent by AI",
                          ],
            "Sales\Marketing":["Sales driving experience",
                               "Customer Facing Experience",
                               "Contribution to improvement of sales/turnover",
                               "Negociation skills",
                               "Customer acquisition"]}


"""
ri = ["CV Overall Quality (Grammar, Orthographe, Conjugation)",
      "Relevant Leadership Experience",
      "Communication Quality and Experience",
      "Relevant Technical Experience",
      "Relevant Technical Education"]
"""
#for f in features.keys():
#    for k in features[f]:
              

def progress_bar(value):
    print(" We are at %d/100"%value)

pp=5.18
path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
files_  = r"%s\PL*.pdf"%path
files = glob.glob(files_)
cvs = {}


# Exemple d’utilisation

for f in files[:]:
    contenu = extract_text_from_pdf(f)
    key = f.split("\\")[-1].split(".")[0]
    cvs[key]=contenu
    #(self,cvs,model,jd,future_project,team_skills,ranking_information,progress_bar)
models = ["gpt-5","gpt-5-mini","gpt-4.1","o3-mini","o4-mini","o1-mini"]#,"gpt-4o-mini","gpt-4.1-mini"]

ri = get_key_skills(jd,models)

models = models[:4]

e=1/0
analyses = {}
for model in models:
    analysis = overall_manager(cvs,model, jd, future_project, team_skills,ri ,progress_bar)
    analysis.collect_information_data_MT(len(cvs))  
    analyses[model]=analysis

all_pass = {}
all_pass_names = []
for model in models:
   for k in analyses[model].condorecet_selected:
       if k not in all_pass_names:
           all_pass_names.append(k)
           all_pass[k]=analyses[model].condorecet_selected[k]

print(all_pass_names)
for model in models:
    analysis=analyses[model]
    analysis.condorecet_selected = all_pass
    analysis.condorecet_applicants = all_pass_names
    ct = len(all_pass)
    ct2 = (ct*(ct-1))/2
    analysis.collect_comparison_data_MT(ct2)
    analysis.compute_winner_scores()
    analysis.compute_category_scores()

ll = len(models)    
df_categories = {}
for k in analysis.cat_winners_df.keys():
    df_categories[k]=analysis.cat_winners_df[k]*0 
    for m in models:
        df_categories[k]=df_categories[k]+analyses[m].cat_winners_df[k]
    print(k)
    cc = df_categories[k].shape[0]-1
    print(df_categories[k]/ll)
    print(df_categories[k].sum(axis=0)/(ll*cc))

df0 = analyses[m].overall_matrix_pd*0 

for k in analyses.keys():
    df0 = df0 + analyses[k].overall_matrix_pd
print(df0/(ll))
print(df0.sum(axis=0)/(ll*cc))
    
#print("Contenu extrait :", contenu)