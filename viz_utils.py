import plotly.express as px

def make_city_map(df):
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="lst_c",
        size_max=10,
        zoom=10,
        color_continuous_scale="Turbo",
        hover_data=["ndvi", "built_index", "lst_c"],
        title="Urban Heat Map from Earth Engine samples"
    )
    fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=40, b=0))
    return fig

def make_results_chart(df):
    fig = px.bar(
        df,
        x="Scenario",
        y="Cooling reduction (°C)",
        text="Cooling reduction (°C)",
        title="Estimated cooling by intervention"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="Cooling reduction (°C)", uniformtext_minsize=8)
    return fig