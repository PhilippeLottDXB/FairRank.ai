import streamlit as st

# 1. Define your individual checkbox labels
labels = [
    "Relevant Technical Experience",
    "Relevant Technical Education",
    "Relevant Leadership Experience",
    "Communication Quality and Experience"
    "Potential Relevant Technical Network",
    "Available Team complementarty",
    "Suitability for future projects",
    "Political Exposure","Strategy know-how",
    "Probability of the CV being writtent by AI",
    "CV Overall Quality (Grammar, Orthographe, Conjugation)",
    "Executive Leadership Experience",
    "Sales driving experience",
    "Team Building Experience",
    "Juniors Mentoring Experience",
    "Leadership Development Experience",
    "Individual Coaching Experience",
    "Customer Facing Experience",
    "Overall suitability for the role",
    "Team work","kindness",
    "Attention to detail",
    "Ability to work and deliver projects",
    "Ability to handle ambiguity",
    "Adaptability and versatiloty",
    "Growth mindset","Authenticity and Originality",
    "Cultural and organizational fit",
    "Professional Narrative and Consistency",
    "Systems Thinking Ability",
    "Decision Making",
    "Innovation Capacity",
    "Cross Functional Influence",
    "Conflict Resolution Abilities",
    "Stakeholder Management",
    "International Exposure",
    "Successions Readiness",
    "Role Stretch Potential",
    "Resilience and bounce back history",
    "Values Alignment",
    "Mission Drive",
    "Loyalty"
    ]

# 2. Configure number of columns in the grid
n_cols = 3

# 3. Initialize session state so values persist
for lbl in labels:
    if lbl not in st.session_state:
        st.session_state[lbl] = False

# 4. Render title
st.title("Settings & Options")

# 5. Render checkboxes in a grid
#    Split labels into rows of length n_cols
rows = [labels[i : i + n_cols] for i in range(0, len(labels), n_cols)]

for row in rows:
    cols = st.columns(n_cols)
    for col, lbl in zip(cols, row):
        col.checkbox(lbl, key=lbl)

# 6. Display which options are selected
selected = [lbl for lbl in labels if st.session_state[lbl]]
st.write("### You’ve selected:")
if selected:
    #for lbl in selected:
        st.write(f"✅ {len(selected)}")
else:
    st.write("No options selected.")