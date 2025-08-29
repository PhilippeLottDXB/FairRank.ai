# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 16:41:34 2025

@author: Admin
"""

from Text_comparison_noGPT import compare_skill_lists
from compar_base import Analyse_job_offer, Audit_layer_Skills
from information import jd, future_project, team_skills
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

models = ["gpt-5", "gpt-5-mini"]
lock = threading.Lock()

def get_key_skills(jd, models, n_repeat=10, debug=False):
    count = [0]
    lst2 = []
    def process_model(m):
        local_skills = []
        count[0] += 1
        key_skills = Analyse_job_offer(jd, m)
        skills = eval(key_skills.replace('json', '').replace("```", "").replace("\n", ""))
        #print(key_skills)
        for d in skills["key_skills_ranked"]:
            d2 = d.lower().strip()
            local_skills.append(d2)
        return local_skills
    m2 = n_repeat*models
    num_threads = n_repeat*len(models)

    # Run initial skill extraction in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_model, m) for m in m2]
        for future in as_completed(futures):
            try:
                for skill in future.result():
                    with lock:
                        if skill not in lst2:
                            lst2.append(skill)
            except Exception as e:
                print("Error in process_model:", e)

    print("Non GPT test", len(lst2))
    groups = compare_skill_lists(lst2, 80)
    lst2 = [g[0] for g in groups]
    print("Pre Audit Loop %d" % len(lst2))

    # Audit loop

    votes = {}
    lst3 = []

    def audit_model(m):
        local_votes = {}
        local_lst3 = []
        shortlist_skills = Audit_layer_Skills(jd, lst2, m)
        skills = eval(shortlist_skills.replace('json', '').replace("```", "").replace("\n", ""))
        #print(shortlist_skills)
        for d in skills["key_skills_ranked"]:
            d2 = d.lower().strip()
            if d2 in lst2:
                local_lst3.append(d2)
                local_votes[d2] = local_votes.get(d2, 0) + 1
            else:
                print("Invented skill", d2)
        return local_lst3, local_votes

    # Run audit in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(audit_model, m) for m in m2]
        for future in as_completed(futures):
            try:
                local_lst3, local_votes = future.result()
                with lock:
                    for skill in local_lst3:
                        if skill not in lst3:
                            lst3.append(skill)
                    for skill, v in local_votes.items():
                        votes[skill] = votes.get(skill, 0) + v
            except Exception as e:
                print("Error in audit_model:", e)

    print(lst3)
    print(votes)

    if len(lst3) > 10:
        lst2 = []
        for key in votes:
            if n_repeat* len(models) > 3:
                if votes[key] > 1:
                    lst2.append(key)
            else:
                lst2.append(key)


    if len(lst3) == 10:
        return lst3
    else:
        top_10 = dict(sorted(votes.items(), key=lambda item: item[1], reverse=True)[:10])
        return list(top_10)

def progress_bar(value):
    print(" We are at %d/100" % value)

if __name__ == "__main__":
    ris = []
    ri = get_key_skills(jd, models)
    ris.append(ri)
    print("---")
    print(ris)
    vv = {}
    for ri in ris:
        print(len(ri))
        for r in ri:
            vv[r] = vv.get(r, 0) + 1
    print(vv)