import streamlit as st
import seaborn as sns
from comparisons_class import overall_manager
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd

import pandas as pd


def manual_sum_columns(dataframe):
    column_sums = {}
    for col in dataframe.columns:
        total = 0
        for value in dataframe[col]:
            # Ensure the value is numeric
            if pd.notnull(value) and isinstance(value, (int, float)):
                total += value
        column_sums[col] = total
    return column_sums

# Use the function
def to_long_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a DataFrame into long format with columns: row, col, value.
    Both row- and column-labels become strings.
    """
    long = df.stack().reset_index()
    long.columns = ["row", "col", "value"]
    long["row"] = long["row"].astype(str)
    long["col"] = long["col"].astype(str)
    return long

def col_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute column sums, return a DataFrame sorted by descending score.
    """
    #print(type(df))
    #print(df)
    #scores = manual_sum_columns(
    scores = df.sum(axis=0)
    return (
        pd.DataFrame({"Column": scores.index.astype(str), "Score": scores.values})
          .sort_values("Score", ascending=False)
          .reset_index(drop=True)
    )

import streamlit as st
import pandas as pd
import altair as alt

# 2. Optional: manual column sum function
def manual_sum_columns(df: pd.DataFrame) -> dict[str, float]:
    sums = {}
    for col in df.columns:
        total = 0
        for v in df[col]:
            if pd.notnull(v) and isinstance(v, (int, float)):
                total += v
        sums[col] = total
    return sums

# 3. Convert to long format and attach justification
def to_long_df_with_just(df: pd.DataFrame,
                        just_dict: dict[tuple[str, str], str]) -> pd.DataFrame:
    long = df.stack().reset_index()
    long.columns = ["row", "col", "value"]
    long["row"] = long["row"].astype(str)
    long["col"] = long["col"].astype(str)
    long["justification"] = long.apply(
        lambda r: just_dict[r["row"]][r["col"]],
        axis=1
    )
    return long

# 4. Column scores (you can swap to manual_sum_columns if you prefer)
def col_scores(df: pd.DataFrame) -> pd.DataFrame:
    scores = df.sum(axis=0)
    return (
        pd.DataFrame({"Column": scores.index.astype(str), "Score": scores.values})
          .sort_values("Score", ascending=False)
          .reset_index(drop=True)
    )

# 5. Main Streamlit app
if True:
    st.title("🎨 Heatmap Gallery with Justifications")

    # Example: load or use your own session_state data
    if "results" not in st.session_state:
        st.error("No data found. Please upload or initialize `st.session_state['results']`.")
        st.stop()

    analysis = st.session_state["results"]

    # Build a gallery dict if not already in state
    if "gallery" not in st.session_state:
        st.session_state.gallery = {}
        for k, df in analysis.cat_winners_df.items():
            st.session_state.gallery[k] = {"name": k, "matrix": df}
        st.session_state.gallery["Overall Winner"] = {
            "name": "Overall Winner",
            "matrix": analysis.overall_matrix_pd
        }

    gallery = st.session_state.gallery
    names = list(gallery.keys())
    if "idx" not in st.session_state:
        st.session_state.idx = 0

    # Sidebar: gallery selector
    with st.sidebar:
        st.header("🗂️ Gallery")
        choice = st.selectbox("Choose a table", names, index=st.session_state.idx)
        st.caption("Hover over cells for your custom text.")
        if choice != names[st.session_state.idx]:
            st.session_state.idx = names.index(choice)
            st.rerun()

    current_key = names[st.session_state.idx]
    current_df = gallery[current_key]["matrix"]

    # Left column: column totals bar chart
    left, main = st.columns([1.5, 4])
    with left:
        st.subheader("🏆 Column Totals")
        scores_df = col_scores(current_df)
        chart = (
            alt.Chart(scores_df)
            .mark_bar()
            .encode(
                y=alt.Y("Column:N", sort=scores_df["Column"].tolist(), title=""),
                x=alt.X("Score:Q", title="Sum"),
                color=alt.condition(
                    alt.datum.Score >= 0, alt.value("#4caf50"), alt.value("#ef5350")
                ),
                tooltip=["Column", "Score"],
            )
            .properties(height=300, width=200)
        )
        st.altair_chart(chart, use_container_width=True)

    # Main: heatmap with custom hover-text
    with main:
        nav_l, nav_c, nav_r = st.columns([0.2, 1, 0.2])

        with nav_l:
            if st.button("⬅ Prev") and len(names) > 1:
                st.session_state.idx = (st.session_state.idx - 1) % len(names)
                st.rerun()

        with nav_c:
            st.subheader(f"🖼️ {current_key}")

        with nav_r:
            if st.button("Next ➡") and len(names) > 1:
                st.session_state.idx = (st.session_state.idx + 1) % len(names)
                st.rerun()

        justifications = {}
        names = analysis.results.keys()
        for n in names:
            justifications[n]={}
            for n2 in names:
                if n == n2:
                    justifications[n][n2]="N/A"
                else:
                    justifications[n][n2]=analysis.results[n][n2]["justification"]
                    
        df_long = to_long_df_with_just(current_df, justifications)

        # color scale centered at zero
        color_scale = alt.Scale(
            domain=[df_long.value.min(), 0, df_long.value.max()],
            range=["#FF8A80", "#FFF176", "#81C784"],
        )
        cell_px = 100
        grid = (
            alt.Chart(df_long)
            .mark_rect(stroke="white", strokeWidth=1)
            .encode(
                x=alt.X("col:N", title="Column"),
                y=alt.Y("row:N", title="Row",
                        sort=list(reversed(current_df.index.astype(str)))),
                color=alt.Color("value:Q", scale=color_scale, legend=None),
                tooltip=[
                    alt.Tooltip("justification:N", title="Justification"),
                    alt.Tooltip("row:N", title="Row"),
                    alt.Tooltip("col:N", title="Col"),
                    alt.Tooltip("value:Q", title="Value"),
                ],
            )
            .properties(
                width=min(cell_px * current_df.shape[1],700),
                height=min(cell_px * current_df.shape[0], 500),
            )
        )
        st.altair_chart(grid, use_container_width=False)

        #with st.expander("Raw DataFrame"):
        #    st.dataframe(current_df, use_container_width=True)


if False:
    if "results" in st.session_state:
        st.write("Here are the results of your analysis")
        #st.write(f"Option selected: {st.session_state['option']}")
        #st.write("Here's a preview of your uploaded file:")
        analysis = st.session_state["results"]
        
        if "gallery" not in st.session_state:
            st.session_state.gallery = {}
            for key in analysis.cat_winners_df.keys():
                st.session_state.gallery[key]={"name": key,"matrix": analysis.cat_winners_df[key]}
            st.session_state.gallery["Overall Winner"]={"name":"overall_winner","matrix":analysis.overall_matrix_pd}
        
        
        gallery = st.session_state.gallery
        if "idx" not in st.session_state:
            st.session_state.idx = 0
            
        names = list(gallery.keys())

        names = list(gallery.keys())
        current_name = names[st.session_state.idx]
        current_df = gallery[current_name]
        # ───────────────────────── UI layout ───────────────────────────────

        left_col, main_col, menu_col = st.columns([1.2, 4, 1.6], gap="large")


        # ①  MENU (right) ────────────────────────────────────────────────
        with menu_col:
            st.header("🗂️ Gallery")
            choice = st.selectbox("Choose a table", names, index=st.session_state.idx)
            if choice != current_name:
                st.session_state.idx = names.index(choice)
                st.rerun()

            st.markdown("---")
            st.caption("Your input dict drives these pages.")


        # ②  RANKING (left) ──────────────────────────────────────────────
        with left_col:
            st.header("🏆 Column totals")
            scores_df = col_scores(current_df["matrix"])
            chart = (
                alt.Chart(scores_df)
                .mark_bar()
                .encode(
                    y=alt.Y("Column:N", sort=scores_df["Column"].tolist(), title=""),
                    x=alt.X("Score:Q", title="Sum"),
                    color=alt.condition(
                        alt.datum.Score >= 0, alt.value("#4caf50"), alt.value("#ef5350")
                    ),
                    tooltip=["Column", "Score"],
                )
                .properties(
                    height=max(200, 25 * len(scores_df)),
                    width=160,
                )
            )
            st.altair_chart(chart, use_container_width=True)


        # ③  MAIN GRID (center) ──────────────────────────────────────────
        with main_col:
            nav_l, nav_c, nav_r = st.columns([0.1, 1, 0.1])

            with nav_l:
                if st.button("⬅ Previous") and len(names) > 1:
                    st.session_state.idx = (st.session_state.idx - 1) % len(names)
                    st.rerun()

            with nav_c:
                st.subheader(f"🖼️ {current_name}")

            with nav_r:
                if st.button("Next ➡") and len(names) > 1:
                    st.session_state.idx = (st.session_state.idx + 1) % len(names)
                    st.rerun()

            # prepare long-form for Altair
            df_long = to_long_df(current_df["matrix"])

            color_scale = alt.Scale(
                domain=[df_long.value.min(), 0, df_long.value.max()],
                range=["#FF8A80", "#FFF176", "#81C784"],
            )
            cell_px = 50
            grid = (
                alt.Chart(df_long)
                .mark_rect(stroke="white", strokeWidth=2)
                .encode(
                    x=alt.X("col:N", title="Column"),
                    y=alt.Y(
                        "row:N",
                        title="Row",
                        sort=list(reversed(current_df["matrix"].index.astype(str).tolist())),
                    ),
                    color=alt.Color("value:Q", scale=color_scale, legend=None),
                    tooltip=[
                        alt.Tooltip(analysis.results["row:N"]["Col:N"]["justification"],
                                    title="Justification"),
                        alt.Tooltip("row:N", title="Row"),
                        alt.Tooltip("col:N", title="Col"),
                        alt.Tooltip("value:Q", title="Value"),
                    ],
                )
                .properties(
                    width=min(cell_px * current_df["matrix"].shape[1], 800),
                    height=min(cell_px * current_df["matrix"].shape[0], 600),
                    background="#fafafa",
                )
            )
            st.altair_chart(grid, use_container_width=False)

            with st.expander("Raw DataFrame"):
                st.dataframe(current_df["matrix"], use_container_width=True)
