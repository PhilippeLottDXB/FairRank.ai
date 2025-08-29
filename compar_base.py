# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 07:18:34 2025

@author: Admin
"""

from GPT_link import request
import json
import datetime

# Load your API key (replace this line with your preferred method)


#key = "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"

#openai.api_key = key# or "your-api-key-here"  # Replace securely in prod


def Analyse_job_offer(job_description,model = "gpt-4"):
    
    today = datetime.datetime.today()
    today = today.strftime("%d %m %Y")
    skills = ""
    ratings = ""
    prompt = f"""You are an expert in recruitment, job analysis, and skills extraction.
Your task:
1. Read the job description provided below.
2. Identify exactly **10 broad key skills** required for the role — avoid overly detailed or niche skills.  
3. Rank these skills from **most critical (rank 1)** to **least critical (rank 10)** for successfully performing the job.  
4. Ensure the skills reflect both **technical** and **managerial/strategic** competencies where applicable.
5. Output must be **strictly valid JSON**, following this exact format:

{{
  "key_skills_ranked": [
    "Skill 1",
    "Skill 2",
    "Skill 3",
    "Skill 4",
    "Skill 5",
    "Skill 6",
    "Skill 7",
    "Skill 8",
    "Skill 9",
    "Skill 10"
  ]
}}

Formatting rules:
- The output MUST contain only the JSON object — no explanations, no extra text.
- Each skill must be a short phrase (max 6 words), capitalized as in a title.
- No duplicate skills.
- JSON must be directly parsable by Python’s json library without modifications.

Now process the following job description and produce the ranked JSON list:

[{job_description}]
"""

    # Send to ChatGPT
    response = request(prompt,model=model)
    return response 


def Audit_layer_Skills(job_description,skills,model = "gpt-4"):
    skills_list = ""
    for s in skills:
        skills_list += s + ",\n"
    
    prompt = f"""You are an expert in recruitment, job analysis, and skills extraction. You are hired to perform a detailed audit of the previous groups of recruitment experts.
Your task:
1. Read the job description provided below.
2. Various recruitment experts like you have selected a list of skills for this job offer, provided below as well 
3. Out of these skills, ONLY, Identify exactly 10 required for the role — do not come back with any new skills.  
4. Rank these skills from **most critical (rank 1)** to **least critical (rank 10)** for successfully performing the job.  
5. Output must be **strictly valid JSON**, following this exact format:

{{
  "key_skills_ranked": [
    "Skill 1",
    "Skill 2",
    "Skill 3",
    "Skill 4",
    "Skill 5",
    "Skill 6",
    "Skill 7",
    "Skill 8",
    "Skill 9",
    "Skill 10"
  ]
}}

Formatting rules:
- The output MUST contain only the JSON object — no explanations, no extra text.
- Each skill must be a short phrase (max 6 words), capitalized as in a title.
- No duplicate skills.
- JSON must be directly parsable by Python’s json library without modifications.

Now process the following job description and produce the ranked JSON list:

[{job_description}]

and the skills provided.
[{skills_list}]
"""
    # Send to ChatGPT
    response = request(prompt,model=model)
    return response 

def compare_candidates_against_offer_chatgpt(cv_a, job_description, 
                                             team_profile="", 
                                             project_descriptions="",
                                             model = "gpt-4",
                                             categories = ["Technical Acumen","Team Leadership",
                                             "Communication Skills","Relevant Experience",
                                             "Complementarity with the existing team",
                                             "Alignment with Ongoing & Future Projects"]):
    
    today = datetime.datetime.today()
    today = today.strftime("%d %m %Y")
    skills = ""
    ratings = ""
    for c in categories:
        skills+=" - %s \n"%c
        ratings+='\t"%s": grade from 0 to 10,\n'%c
    #ratings = ""
    prompt = f"""
You are an impartial hiring assistant comparing one anonymized candidates for a specific role and long-term team fit, be harsh with candidates. Make sure only relevant people pass, yet make sure that it does not miss any relevant candidate.

Do not consider data that is not relevant to the text being provided, analyse only the texts provided. 

The date of Today is: \"\"\"{today}\"\"\"

Your task is to:
1. Compare the verify whether candidates could fit the job within these categories:
{skills}
2. Use both the job description and the list of ongoing/upcoming projects to determine what is most important.

3. For each category:
   - Indicate what is the level of fit from 0 to 10

4. Then, indicate clearly whether the candidate's CV is worth further review.

5. Justify your overall decision in 5-7 clear, evidence-based sentences.

Job Description:
\"\"\"
{job_description}
\"\"\"

Candidate:
\"\"\"
{cv_a}
\"\"\"

Team Profile:
\"\"\"
{team_profile}
\"\"\"

Ongoing and Upcoming Projects:
\"\"\"
{project_descriptions}
\"\"\"

Return the result in the following very strict JSON format:
{{
  "Category rating": {{
{ratings}
  }},
  "final_decision": "Yes" - "No" - "Maybe",
  "justification": "<Concise, evidence-based justification, especially referencing future team/project relevance>"
}}
"""

    # Send to ChatGPT
    response = request(prompt,model=model)
    return response 


def compare_candidates_chatgpt(cv_a, cv_b, job_description, team_profile="", 
                               project_descriptions="",model = "gpt-4",
                               categories = ["Technical Acumen","Team Leadership",
                               "Communication Skills","Relevant Experience",
                               "Complementarity with the existing team",
                               "Alignment with Ongoing & Future Projects"]):
    skills = ""
    ratings = ""
    for c in categories:
        skills+=" - %s \n"%c
        ratings+='\t"%s": "A" | "B" | "Tie",\n'%c
    #ratings = ""
    
    prompt = f"""
You are an impartial hiring assistant comparing two anonymized candidates for a specific role and long-term team fit.

Your task is to:
1. Compare the two candidates in each of the following categories:
{skills}

2. Use both the job description and the list of ongoing/upcoming projects to determine what is most important.

3. For each category:
   - Indicate who is stronger, or if it is a tie.

4. Then, choose the overall winner (or declare a tie) based on a balanced judgment of all six categories.

5. Justify your overall decision in 5-7 clear, evidence-based sentences.

Job Description:
\"\"\"
{job_description}
\"\"\"

Candidate A:
\"\"\"
{cv_a}
\"\"\"

Candidate B:
\"\"\"
{cv_b}
\"\"\"

Team Profile:
\"\"\"
{team_profile}
\"\"\"

Ongoing and Upcoming Projects:
\"\"\"
{project_descriptions}
\"\"\"

Return the result in the following very strict JSON format:
{{
  "category_winners": {{
{ratings}
  }},
  "overall_winner": "A" | "B" | "Tie",
  "justification": "<Concise, evidence-based justification, especially referencing future team/project relevance>"
}}
"""

    # Send to ChatGPT
    response = request(prompt,model=model)
    return response 
    """
    # Attempt to load JSON safely
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        print("Warning: GPT response was not valid JSON. Raw response:")
        print(content)
        result = {"error": "Invalid JSON response", "raw": content}

    return result"""



if __name__ == "__main__":
    cv_a = """PhD in Aerospace, 7 years in CFD, 2 years in drone aeroelastic testing, Python, TensorFlow, Fluent."""
    cv_b = """MSc in Mechanical Engineering, 10 years in team leadership, PM on propulsion projects, skilled in communication."""
    
    job_description = """Seeking a propulsion lead with strong technical background in aerodynamics and the ability to manage cross-functional teams. CFD and data-driven diagnostics are a plus."""
    
    team_profile = """Current team has strong thermal and manufacturing expertise but lacks deep CFD and AI modeling."""
    
    project_descriptions = """1. AI turbine health monitoring. 2. CFD-based drone wing redesign. 3. Satellite structure FEM optimization."""
    
    result = compare_candidates_chatgpt(cv_a, cv_b, job_description, team_profile, project_descriptions,model="gpt-4.1-nano")
    
    print(json.dumps(result, indent=2))
