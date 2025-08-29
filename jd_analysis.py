# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 11:46:21 2025

@author: Admin
"""
from Text_comparison_noGPT import compare_skill_lists
from compar_base import Analyse_job_offer,Audit_layer_Skills
from information import jd, future_project, team_skills
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

models = ["gpt-5","gpt-5-mini"]#,"gpt-4.1","o3-mini","o4-mini","o1-mini"]#,"gpt-4o-mini","gpt-4.1-mini"]


def get_key_skills(jd,models,iter_audit_ref=2, n_repeat = 2,debug = False):
    # Use JD for identifying the key skills required.
    import threading
    #passcount = len(models)*iter_audit_ref*n_repeat
    count = [0]
    
    lst2 = []
    lock = threading.Lock()
    def process_model(m):
        print(m)
        for i in range(n_repeat):
            count[0]+=1
            #progress_bar(int(100*count[0]/passcount))
            key_skills = Analyse_job_offer(jd, m)
            skills = eval(key_skills.replace('json', '').replace("```", "").replace("\n", "").replace("```", ""))
            print(key_skills)
    
            for d in skills["key_skills_ranked"]:
                d2 = d.lower().strip()
                with lock:
                    if d2 not in lst2:
                        lst2.append(d2)


    # Create and start threads
    threads = []
    for m in models:
        for i in range(n_repeat):        
            t = threading.Thread(target=process_model, args=(m,))
            threads.append(t)
            t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    print("Non GPT test",len(lst2))
    groups = compare_skill_lists(lst2,80)
    lst2 = []
    for g in groups:
        lst2.append(g[0])
    #print(lst2)

    """
    lst2 = []
    for m in models:
        print(m)
        for i in range(3):
            key_skills = Analyse_job_offer(jd,m)
            skills = eval(key_skills.replace('json','').replace("```","").replace("\n","").replace("```",""))
            print(key_skills)
            #lst.append(skills["key_skills_ranked"])
            for d in skills["key_skills_ranked"]:
                d2= d.lower().strip()
                if d2 not in lst2:
                    lst2.append(d2)
    """
    lst3 = []
    
    print("Pre Audit Loop %d"%len(lst2))
    
    #votes = {}    
    self_audit_flag = True        
    iter_audit = 0
    ## Audit Layer
    while self_audit_flag and iter_audit<=iter_audit_ref:
        import threading

        votes = {}
        lst3 = []
        lock = threading.Lock()
        
        def audit_model(m):
            print("Audit", m, iter_audit)
            for k in range(n_repeat):
                count[0]+=1
                #progress_bar(int(100*count[0]/passcount))
                shortlist_skills = Audit_layer_Skills(jd, lst2, m)
                skills = eval(shortlist_skills.replace('json', '').replace("```", "").replace("\n", "").replace("```", ""))
                print(shortlist_skills)
            
                for d in skills["key_skills_ranked"]:
                    d2 = d.lower().strip()
                    with lock:
                        if d2 in lst2:
                            if d2 not in lst3:
                                lst3.append(d2)
                            if d2 not in votes:
                                votes[d2] = 1
                            else:
                                votes[d2] += 1
                        else:
                            print("Invented skill", d2)
        
        # Create and start threads
        threads = []
        """
        items = list(self.cvs.items())
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, item) for item in items]
            for future in as_completed(futures):
                # Can handle exceptions here if needed
                try:
                    future.result()
                except Exception as e:
                    print("Error processing CV:", e)
        """
        for m in models:
            t = threading.Thread(target=audit_model, args=(m,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to finish
        for t in threads:
            t.join()
        """
        votes = {}    
        lst3 = []
        for m in models:
            print("Audit",m,iter_audit)
            shortlist_skills = Audit_layer_Skills(jd,lst2,m)
            skills = eval(shortlist_skills.replace('json','').replace("```","").replace("\n","").replace("```",""))
            print(shortlist_skills)
            #lst.append(skills["key_skills_ranked"])
            for d in skills["key_skills_ranked"]:
                d2 = d.lower().strip()
                if d2 in lst2:
                    if d2 not in lst3:
                        lst3.append(d2)
                    if d2 not in votes.keys():
                        votes[d2]=1 
                    else:
                        votes[d2]+=1
                else:
                    print("Invented skill",d2)
        """            
        print(iter_audit,len(lst3))
        print(lst3)
        print(votes)
        if len(lst3)>10:
            lst2 = []
            for key in votes.keys():
                if iter_audit>2 and len(models)>3:
                    if votes[key]>1:
                        lst2.append(key)
                else:
                    lst2.append(key)
                    
            iter_audit+=1 
        else:
            self_audit_flag = False 
    #progress_bar(100)
    if len(lst3)==10:
        return lst3
    else:
        top_10 = dict(sorted(votes.items(), key=lambda item: item[1], reverse=True)[:10])
        return list(top_10)

def progress_bar(value):
    print(" We are at %d/100"%value)

if __name__ == "__main__":
    ris = []
    if True: #for c in range(0,2,1):
        ri = get_key_skills(jd,models)
        ris.append(ri)
    print("---")
    print(ris)
    vv = {}
    for ri in ris:
        print(len(ri))
        for r in ri:
            if r in vv.keys():
                vv[r]+=1 
            else:
                vv[r]=1
                
    print(vv)
