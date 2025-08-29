# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 07:32:01 2025

@author: Admin
"""


import os
key = os.getenv("OPENAI_API_KEY")###
key = "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"

#import openai


from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "t",
        },
    ],
    openai_key = key,
)
print(completion.choices[0].message.content)

response = client.request.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn.",
    api_key = key
)

print(response.output_text)
"""
# Remplace ceci par ta propre clé API
openai.api_key = key

def envoyer_prompt(prompt_utilisateur):
    reponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # ou "gpt-4" selon ton accès
        messages=[
            {"role": "system", "content": "Tu es un assistant utile."},
            {"role": "user", "content": prompt_utilisateur}
        ]
    )
    return reponse.choices[0].message["content"]

# Exemple d’utilisation
prompt = "Quels sont les avantages de l'énergie solaire ?"
reponse = envoyer_prompt(prompt)
print("Réponse de ChatGPT :", reponse)
"""
#im