# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 09:55:22 2025

@author: Admin
"""

from rapidfuzz import fuzz, process

def normalize_skill(skill):
    return skill.lower().strip()

def compare_skill_lists(lists, threshold=80):
    """
    Compare multiple GPT skill lists and group similar ones.
    lists: list of lists of skills
    threshold: similarity score (0-100) for considering skills the same
    """
    all_skills = set()
    for skill in lists:
        #for skill in skill_list:
            all_skills.add(normalize_skill(skill))
    
    all_skills = list(all_skills)
    groups = []
    used = set()
    
    for skill in all_skills:
        if skill in used:
            continue
        group = [skill]
        used.add(skill)
        for other in all_skills:
            if other not in used:
                if fuzz.token_sort_ratio(skill, other) >= threshold:
                    group.append(other)
                    used.add(other)
        groups.append(group)
    
    return groups




if __name__ == "__main__":
    # Example usage:
    list1 = ["Leadership and Team Management", "Propulsion Systems Engineering", "Budget Management"]
    list2 = ["Team Leadership", "Propulsion Engineering", "Financial and Resource Management"]
    
    similar_groups = compare_skill_lists([list1, list2])
    for group in similar_groups:
        print(group)
