import ee
import pandas as pd
import numpy as np

def init_gee():
    service_account = st_secrets("gee_service_account")
    key_file = st_secrets("gee_key_file")
    # Change it to just this:
    ee.Initialize()


def st_secrets(key):
    import streamlit as st
    return st.secrets[key]

def _cloud_mask_landsat(image):
    qa = image.select("QA_PIXEL")
    cloud = qa.bitwiseAnd(1 << 3).eq(0)
    shadow = qa.bitwiseAnd(1 << 4).eq(0)
    return image.updateMask(cloud.And(shadow))

def _apply_scale(image):
    optical = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = image.select("ST_B.*").multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)

def fetch_city_heat_data(region, start_date, end_date, city_name, n_samples=1000):
    col = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .filter(ee.Filter.lt("CLOUD_COVER", 30))
        .map(_cloud_mask_landsat)
        .map(_apply_scale)
    )

    img = col.median().clip(region)

    lst = img.select("ST_B10").subtract(273.15).rename("lst_c")
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("ndvi")
    built = img.normalizedDifference(["SR_B6", "SR_B5"]).rename("built_index")

    stack = ee.Image.cat([lst, ndvi, built]).clip(region)

    samples = stack.sample(
        region=region,
        scale=30,
        numPixels=n_samples,
        geometries=True
    )

    features = samples.getInfo()["features"]
    rows = []
    for f in features:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        rows.append({
            "city": city_name,
            "lon": coords[0],
            "lat": coords[1],
            "lst_c": p.get("lst_c"),
            "ndvi": p.get("ndvi"),
            "built_index": p.get("built_index"),
        })

    return pd.DataFrame(rows)