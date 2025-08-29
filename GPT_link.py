# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 15:48:05 2025

@author: Admin
"""

#!/usr/bin/env -S poetry run python
key = "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"

from openai import OpenAI
import openai

# gets API Key from environment variable OPENAI_API_KEY
def request(prompt,model = "gpt-4"):
    client = OpenAI()
    key = "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"

    openai.api_key = key
    # Non-streaming:
    #print("----- standard request -----")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return(completion.choices[0].message.content)
"""
# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue

    print(chunk.choices[0].delta.content, end="")
print()

# Response headers:
print("----- custom response headers test -----")
response = client.chat.completions.with_raw_response.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
)
completion = response.parse()
print(response.request_id)
print(completion.choices[0].message.content)
"""