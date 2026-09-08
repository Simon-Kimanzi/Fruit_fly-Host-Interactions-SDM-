"""
ENEZA Project Dashboard
Fruit fly (Tephritidae) host-plant interactions and species distribution modeling.

Run locally with: streamlit run app.py
(run from inside src/dashboard/, or adjust DATA_DIR below)
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Fruit Fly SDM Dashboard", layout="wide", page_icon="🪰")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")
MODELS_DIR = os.path.join(BASE_DIR, "..", "..", "outputs", "models")


@st.cache_data
def load_clean_data():
    return pd.read_csv(os.path.join(DATA_DIR, "clean_data.csv"))


@st.cache_data
def load_host_plant_lookup():
    with open(os.path.join(MODELS_DIR, "host_plant_lookup.json")) as f:
        return json.load(f)


@st.cache_data
def load_performance_summaries():
    primary = pd.read_csv(os.path.join(MODELS_DIR, "sdm_performance_summary.csv"))
    ensemble_path = os.path.join(MODELS_DIR, "ensemble_performance_summary.csv")
    ensemble = pd.read_csv(ensemble_path) if os.path.exists(ensemble_path) else None
    return primary, ensemble


@st.cache_data
def load_grid_predictions(pipeline):
    fname = f"africa_grid_predictions_{pipeline}.csv"
    path = os.path.join(MODELS_DIR, fname)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def nearest_grid_prediction(grid_df, species, lat, lon):
    """Find the nearest precomputed grid point for a given species and location."""
    sub = grid_df[grid_df["species"] == species].copy()
    if sub.empty:
        return None
    sub["dist"] = np.sqrt((sub["latitude"] - lat) ** 2 + (sub["longitude"] - lon) ** 2)
    nearest = sub.loc[sub["dist"].idxmin()]
    return nearest


def suitability_band(score):
    if score >= 0.6:
        return "HIGH"
    elif score >= 0.4:
        return "MODERATE"
    else:
        return "LOW"


BAND_COLORS = {"HIGH": "#d62728", "MODERATE": "#ff7f0e", "LOW": "#2ca02c"}

try:
    df = load_clean_data()
    host_plant_lookup = load_host_plant_lookup()
    primary_perf, ensemble_perf = load_performance_summaries()
    data_ready = True
except FileNotFoundError as e:
    data_ready = False
    load_error = str(e)

TARGET_SPECIES = primary_perf["species"].tolist() if data_ready else []

st.title("Fruit Fly (Tephritidae) Host-Plant Interactions and Species Distribution Dashboard")
st.caption("ENEZA Data Science Internship Project — International Centre of Insect Physiology and Ecology (icipe)")

if not data_ready:
    st.error(
        "Could not load project data. Make sure `data/clean_data.csv` and "
        "`outputs/models/host_plant_lookup.json` exist (produced by notebooks 01 and 02). "
        f"Details: {load_error}"
    )
    st.stop()

tab_overview, tab_explorer, tab_interactions, tab_sdm, tab_risk = st.tabs(
    ["Overview", "Data Explorer", "Host-Pest Interactions", "Species Distribution Models", "Farmer Risk Lookup"]
)

with tab_overview:
    st.header("Project Overview")
    st.markdown(
        """
        This dashboard presents the results of a data science project using citizen-science
        observations from iNaturalist to analyze fruit fly (Tephritidae) host-plant interactions
        and predict climatic suitability across Africa.

        **Objectives:**
        - Clean and structure raw citizen-science observation data
        - Analyze host plant interaction patterns
        - Model species distribution and ecological suitability (SDM), with attention to
          transferability to regions with sparse observation records, especially East Africa
        - Combine climate suitability with host plant associations into a farmer-facing risk tool
        """
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total observations", f"{len(df):,}")
    col2.metric("Species-level records", f"{(df['taxon_resolution']=='species').sum():,}")
    col3.metric("Interaction-study records", f"{(df['Data_Category']=='Interaction Study').sum():,}")
    col4.metric("Modeled species", len(TARGET_SPECIES))

    st.markdown("**Modeled species:**")
    st.write(", ".join(f"*{sp}*" for sp in TARGET_SPECIES))

with tab_explorer:
    st.header("Data Explorer")

    col1, col2 = st.columns(2)
    with col1:
        top_species = df["scientific_name"].value_counts().head(15).sort_values()
        fig = px.bar(top_species, orientation="h", labels={"value": "Number of observations", "index": ""},
                     title="Top 15 species by observation count", color=top_species.values,
                     color_continuous_scale="Viridis")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_countries = df["place_country_name"].value_counts().head(15).sort_values()
        fig = px.bar(top_countries, orientation="h", labels={"value": "Number of observations", "index": ""},
                     title="Top 15 countries by observation count", color=top_countries.values,
                     color_continuous_scale="Plasma")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        obs_year = df["obs_year"].value_counts().sort_index()
        fig = px.line(x=obs_year.index, y=obs_year.values, markers=True,
                      labels={"x": "Year", "y": "Number of observations"}, title="Observations per year")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        cat_counts = df["Data_Category"].value_counts()
        fig = px.pie(values=cat_counts.values, names=cat_counts.index,
                     title="Occurrence-only vs interaction-study records")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "*Note: observation volume grew sharply from 2018 onward, consistent with growing "
        "iNaturalist platform adoption rather than a genuine change in pest prevalence.*"
    )

with tab_interactions:
    st.header("Host-Pest Interaction Explorer")
    interactions = df[df["Data_Category"] == "Interaction Study"]

    selected_species = st.selectbox("Select a fly species to see its documented host plants:",
                                     sorted(interactions["scientific_name"].unique()))
    hosts = sorted(interactions[interactions["scientific_name"] == selected_species]["host_plant"].unique())
    st.markdown(f"**{selected_species}** has been documented on: " + ", ".join(f"*{h}*" for h in hosts))

    col1, col2 = st.columns(2)
    with col1:
        top_hosts = interactions["host_plant"].value_counts().head(10).sort_values()
        fig = px.bar(top_hosts, orientation="h", title="Top 10 host plants by interaction record count",
                     labels={"value": "Number of records", "index": ""}, color=top_hosts.values,
                     color_continuous_scale="Sunset")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_sp = interactions["scientific_name"].value_counts().head(10).index
        top_hp = interactions["host_plant"].value_counts().head(10).index
        matrix = pd.crosstab(
            interactions[interactions["scientific_name"].isin(top_sp)]["scientific_name"],
            interactions[interactions["host_plant"].isin(top_hp)]["host_plant"],
        )
        fig = px.imshow(matrix, text_auto=True, color_continuous_scale="Reds",
                         title="Species vs host plant interaction counts", aspect="auto")
        st.plotly_chart(fig, use_container_width=True)

with tab_sdm:
    st.header("Species Distribution Model Performance")

    pipeline_choice = st.radio("Pipeline:", ["Primary (single Random Forest)", "Ensemble (RF + GB + LogReg)"],
                                horizontal=True)
    pipeline_key = "primary" if "Primary" in pipeline_choice else "ensemble"

    if pipeline_key == "primary":
        perf = primary_perf.sort_values("auc", ascending=True)
        fig = px.bar(perf, x="auc", y="species", orientation="h", title="Spatial cross-validated AUC by species",
                     labels={"auc": "AUC", "species": ""}, color="auc", color_continuous_scale="Teal", range_x=[0, 1])
        fig.add_vline(x=0.7, line_dash="dash", line_color="gray", annotation_text="Usable threshold")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(primary_perf, use_container_width=True)
    else:
        if ensemble_perf is not None:
            perf = ensemble_perf.sort_values("ensemble_auc", ascending=True)
            fig = go.Figure()
            for col, color in zip(["Random Forest", "Gradient Boosting", "Logistic Regression", "ensemble_auc"],
                                   ["#1f77b4", "#d62728", "#e377c2", "#17becf"]):
                fig.add_trace(go.Bar(x=perf[col], y=perf["species"], name=col, orientation="h"))
            fig.update_layout(barmode="group", title="Classifier comparison and ensemble AUC by species",
                               xaxis_title="AUC", xaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(ensemble_perf, use_container_width=True)
        else:
            st.info("Ensemble performance summary not found. Run notebook 03 to generate it.")

    st.subheader("Predicted Suitability Map (Africa)")
    map_species = st.selectbox("Species:", TARGET_SPECIES, key="map_species")
    grid_df = load_grid_predictions(pipeline_key)

    if grid_df is not None:
        species_grid = grid_df[grid_df["species"] == map_species]
        fig = px.scatter_geo(
            species_grid, lat="latitude", lon="longitude", color="suitability",
            color_continuous_scale="YlOrRd", scope="africa",
            title=f"{map_species}: predicted climatic suitability",
        )
        fig.update_traces(marker=dict(size=4))
        fig.update_layout(height=550, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
        novel_pct = species_grid["is_novel"].mean() * 100
        st.caption(f"{novel_pct:.1f}% of the mapped area falls outside {map_species}'s confirmed climatic range "
                   f"(extrapolated / novel conditions) — treat high suitability in these areas as a hypothesis, "
                   f"not a validated forecast.")
    else:
        st.info(
            f"Precomputed grid predictions not found for the {pipeline_key} pipeline. "
            f"Run the grid-export cell at the end of the corresponding notebook to generate "
            f"`africa_grid_predictions_{pipeline_key}.csv`."
        )

with tab_risk:
    st.header("Farmer-Facing Risk Lookup")
    st.markdown(
        "Enter a location and the crop you grow. This tool checks, for each modeled fruit fly "
        "species, whether your location is climatically suitable and whether your crop is a "
        "documented host, then combines both into a risk assessment."
    )

    pipeline_choice_risk = st.radio("Pipeline:", ["Primary", "Ensemble"], horizontal=True, key="risk_pipeline")
    pipeline_key_risk = "primary" if pipeline_choice_risk == "Primary" else "ensemble"

    col1, col2, col3 = st.columns(3)
    lat = col1.number_input("Latitude", value=-1.286389, format="%.4f")
    lon = col2.number_input("Longitude", value=36.817223, format="%.4f")
    crop = col3.text_input("Crop you grow (e.g. Mangifera indica, mango)", value="Mangifera indica")

    if st.button("Assess Risk", type="primary"):
        grid_df = load_grid_predictions(pipeline_key_risk)
        if grid_df is None:
            st.error(f"No precomputed grid available for the {pipeline_key_risk} pipeline.")
        else:
            results = []
            for species in TARGET_SPECIES:
                nearest = nearest_grid_prediction(grid_df, species, lat, lon)
                if nearest is None:
                    continue
                hosts = host_plant_lookup.get(species, [])
                is_host = any(crop.lower() in h.lower() or h.lower() in crop.lower() for h in hosts)
                results.append({
                    "species": species,
                    "suitability": round(float(nearest["suitability"]), 3),
                    "band": suitability_band(nearest["suitability"]),
                    "documented_host": "Yes" if is_host else "No",
                    "hosts": ", ".join(hosts),
                    "nearest_grid_distance_deg": round(float(nearest["dist"]), 2),
                    "is_novel": bool(nearest["is_novel"]),
                })

            results_df = pd.DataFrame(results).sort_values("suitability", ascending=False)

            st.subheader(f"Results for ({lat:.3f}, {lon:.3f}) growing {crop}")
            for _, row in results_df.iterrows():
                color = BAND_COLORS[row["band"]]
                novel_note = " climatically novel area — treat as a hypothesis" if row["is_novel"] else ""
                st.markdown(
                    f"<div style='padding:10px;border-left:5px solid {color};margin-bottom:8px;background:#fafafa'>"
                    f"<b>{row['species']}</b> — suitability {row['suitability']} "
                    f"(<span style='color:{color};font-weight:bold'>{row['band']}</span>), "
                    f"documented host: <b>{row['documented_host']}</b>{novel_note}<br>"
                    f"<span style='font-size:0.85em;color:#666'>Documented hosts: {row['hosts']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.caption(
                "Suitability is looked up from the nearest precomputed grid point "
                "(grid spacing approx. 0.5 degrees), not a live model prediction at the exact "
                "coordinate. Host plant matching is based on documented associations in this "
                "dataset's interaction records, not an independent host plant distribution layer."
            )
