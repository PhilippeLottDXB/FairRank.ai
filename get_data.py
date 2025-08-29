# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:02:00 2025

@author: Admin
"""

import PyPDF2
import glob

def extract_text_from_pdf(nom_fichier_pdf):
    texte = ""
    with open(nom_fichier_pdf, 'rb') as fichier:
        lecteur_pdf = PyPDF2.PdfReader(fichier)
        for page in lecteur_pdf.pages:
            texte += page.extract_text()
    return texte

if __name__ == "__main__":
    path = r"C:\Users\Admin\OneDrive\Documents\CondorcetHR\database"
    files_  = r"%s\*.pdf"%path
    files = glob.glob(files_)
    # Exemple d’utilisation
    fichier_pdf = files[0]
    contenu = extract_text_from_pdf(fichier_pdf)
    #print("Contenu extrait :", contenu)

