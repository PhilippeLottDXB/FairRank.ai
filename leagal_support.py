# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 08:40:34 2025

@author: Admin
"""
from compar_base import summarize_rejections, self_audit_rejection, rebuttal_rejection
from concurrent.futures import ThreadPoolExecutor, as_completed


def legal_process(cvs,reject_justifications, jd,model):

    def process_cv(cv, text):
        # Step 1: Summarize
        test = summarize_rejections(jd, cvs[cv], text,model=model)
        print(test)
    
        # Step 2: Self-audit
        t2 = self_audit_rejection(jd, cvs[cv], test,model=model)
        print(t2)
    
        # Step 3: Rebuttal
        keepTrying = True
        while keepTrying:
            t3 = rebuttal_rejection(jd, cvs[cv], text, t2,model=model)
            try:
                t3 = eval(t3)  # Assuming this returns a dict
                keepTrying = False
            except:
                print("Error in parsing hiring information")
                print(t3)
        
        return cv, t3, t3["candidate_name"]

    crcs = len(cvs)
    # --- Main execution ---
    legal_responses = {}
    candidates_names = []
    
    # Adjust max_workers to your environment / API rate limits
    with ThreadPoolExecutor(max_workers=crcs) as executor:
        futures = [
            executor.submit(process_cv, cv, text)
            for cv, text in reject_justifications.items()
        ]
    
    for future in as_completed(futures):
        try:
            cv, t3, candidate_name = future.result()
            legal_responses[cv] = t3
            candidates_names.append(candidate_name)
        except Exception as e:
            print(f"Error processing {cv}: {e}")
            
    return legal_responses