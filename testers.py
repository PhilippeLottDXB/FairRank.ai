# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 07:51:46 2025

@author: Admin
"""

import os, requests, datetime as dt

API_KEY= os.environ["OPENAI_API_KEY"]
headers = {"Authorization": f"Bearer {API_KEY}"}

# Example: last 30 days
end = dt.date.today()
start = end - dt.timedelta(days=30)

# Replace with the documented endpoints/params for Usage/Costs in your org/project.
# Typical pattern:
resp = requests.get(
    "https://api.openai.com/v1/usage/costs",
    params={"start_date": start.isoformat(), "end_date": end.isoformat(), "granularity": "day"},
    headers=headers,
    timeout=30
)
resp.raise_for_status()
data = resp.json()
total_spend = sum(d["cost"] for d in data.get("data", []))
print(f"USD spent (last 30 days): {total_spend:.2f}")
