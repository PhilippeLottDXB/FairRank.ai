# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 15:48:05 2025

@author: Admin
"""

#!/usr/bin/env -S poetry run python

from openai import OpenAI
import openai


def getkey():
    try:
        import streamlit as st
        key = st.secrets["OPENAI_API_KEY"]
    except:
        import os
        key = os.getenv("OPENAI_API_KEY")
    return key

# gets API Key from environment variable OPENAI_API_KEY
def request_2(prompt,model = "gpt-5",debug=False):
    gpt_token_pricing = {
                                "gpt-5": {
                                    "input": 1.25,
                                    "output": 10.00
                                },
                                "gpt-5-mini": {
                                    "input": 0.25,
                                    "output": 2.00
                                },
                                "gpt-4.1": {
                                    "input": 2.00,
                                    "output": 8.00
                                },
                                "o3-mini": {
                                    "input": 1.10,
                                    "output": 4.40
                                },
                                "o4-mini": {
                                    "input": 1.10,
                                    "output": 4.40
                                },
                                "o1-mini": {
                                    "input": 15.00,
                                    "output": 60.00
                                }
                            }
    key = getkey()
    client = OpenAI(api_key=key)

    #openai.api_key = key
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
    data  = completion.usage
    dct = data.dict()
    if debug:
        inputs = dct['prompt_tokens']
        outputs = dct["completion_tokens"]
        price = gpt_token_pricing[model]["input"]*inputs*1e-6 + gpt_token_pricing[model]["output"]*outputs*1e-6 
        print("price is:",price,"split in inputs:",inputs,"and outputs:", outputs)
    #print(completion.done.input_token_details)
   # response = completion.choices[0].message.content

    return(completion.choices[0].message.content)

class GPT_connect0:
    def __init__(self):
        self.key = getkey()
        self.price = 0.0 
        self.test = 0
        self.gpt_token_pricing = {
                                    "gpt-5": {
                                        "input": 1.25,
                                        "output": 10.00
                                    },
                                    "gpt-5-mini": {
                                        "input": 0.25,
                                        "output": 2.00
                                    },
                                    "gpt-4.1": {
                                        "input": 2.00,
                                        "output": 8.00
                                    },
                                    "o3-mini": {
                                        "input": 1.10,
                                        "output": 4.40
                                    },
                                    "o4-mini": {
                                        "input": 1.10,
                                        "output": 4.40
                                    },
                                    "o1-mini": {
                                        "input": 15.00,
                                        "output": 60.00
                                    }
                                }
        
    def get_request_cost(self,inputs,outputs,model):
        dpi = self.gpt_token_pricing[model]["input"]*inputs*1e-6 
        dpo = self.gpt_token_pricing[model]["output"]*outputs*1e-6 
        self.price+=dpi+dpo
     
    def __call__(self,prompt,model = "gpt-5-mini"):
        key = self.key
        
        client = OpenAI(api_key=key)

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
            temperature=1,
        )
        data  = completion.usage
        dct = data.dict()
        inputs = dct['prompt_tokens']
        outputs = dct["completion_tokens"]
        self.get_request_cost(inputs, outputs, model)
        #print(inputs, outputs)
        #print(completion.done.input_token_details)
       # response = completion.choices[0].message.content

        return(completion.choices[0].message.content)


if __name__ == "__main__":
    connector = GPT_connect0()
    for k in range(1):
        data = connector.request("Develop a simple explaination for why the earth is flat","gpt-5-mini")
    print(connector.price)
    print(data)

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

from decimal import Decimal, getcontext, ROUND_HALF_UP
from threading import Lock
from types import MappingProxyType
from openai import OpenAI

getcontext().prec = 28  # plenty for money math

class GPT_connect:
    PRICING = MappingProxyType({
        "gpt-5":      {"input": Decimal("1.25"), "output": Decimal("10.00")},
        "gpt-5-mini": {"input": Decimal("0.25"), "output": Decimal("2.00")},
        "gpt-4.1":    {"input": Decimal("2.00"), "output": Decimal("8.00")},
        "o3-mini":    {"input": Decimal("1.10"), "output": Decimal("4.40")},
        "o4-mini":    {"input": Decimal("1.10"), "output": Decimal("4.40")},
        "o1-mini":    {"input": Decimal("15.00"), "output": Decimal("60.00")},
    })

    def __init__(self):
        self.key = getkey()
        self._total_usd = Decimal("0.00")
        self._lock = Lock()

    @staticmethod
    def _cost_usd(tokens: int, rate_per_million_usd: Decimal) -> Decimal:
        # cost = rate($/1e6 tok) * tokens / 1e6
        return (rate_per_million_usd * Decimal(tokens)) #/ Decimal(1_000_000)

    def _add_cost(self, usd: Decimal) -> None:
        # Quantize to cents before adding (or keep 1/10,000 if you prefer finer)
        usd = usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        with self._lock:
            self._total_usd += usd

    def get_total_usd(self) -> Decimal:
        with self._lock:
            return +self._total_usd  # unary + makes a copy

    def get_request_cost(self, inputs: int, outputs: int, model: str) -> Decimal:
        try:
            p = self.PRICING[model]
        except KeyError:
            raise ValueError(f"Unknown model: {model}")

        cost_in = self._cost_usd(inputs,  p["input"])
        cost_out = self._cost_usd(outputs, p["output"])
        total = cost_in + cost_out
        self._add_cost(total)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __call__(self, prompt: str, model: str = "gpt-5-mini") -> str:
        client = OpenAI(api_key=self.key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
        )
        usage = completion.usage
        inputs = usage.prompt_tokens
        outputs = usage.completion_tokens
        self.get_request_cost(inputs, outputs, model)
        return completion.choices[0].message.content


request = GPT_connect()