# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:13:28 2025

@author: Admin
"""

import glob
import PyPDF2
#from get_data import extract_text_from_pdf

def extract_text_from_pdf(nom_fichier_pdf):
    texte = ""
    with open(nom_fichier_pdf, 'rb') as fichier:
        lecteur_pdf = PyPDF2.PdfReader(fichier)
        for page in lecteur_pdf.pages:
            texte += page.extract_text()
    return texte

def collect_texts(files):
    
    dct = {}
    
    for f in files:
        txt = extract_text_from_pdf(f)
        dct[f] = txt
        
    return dct
        
"""
if __name__ == "__main__":
    c = collect_texts(files)"""