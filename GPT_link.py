from openai import OpenAI
import streamlit as st
import openai

# gets API Key from environment variable OPENAI_API_KEY
def request(prompt,model = "gpt-4"):
    key =OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    client = OpenAI(api_key=key)
    # key = "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"

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

if __name__ == "__main__":
    data = request("What are the top cities in europe")
    print(data)

