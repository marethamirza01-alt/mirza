from flask import Flask, render_template
import folium
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/map")
def map_view():

    df = pd.read_csv("kaltim_dengan_koordinat.csv")
    df["populasi"] = pd.to_numeric(df["populasi"], errors="coerce")

    # pusat peta
    map_kaltim = folium.Map(location=[-0.5, 116.9], zoom_start=7)

    # min max populasi
    max_pop = df["populasi"].max()

    # fungsi warna
    def get_color(pop):
        if pop >= max_pop * 0.75:
            return "red"       # sangat padat
        elif pop >= max_pop * 0.5:
            return "orange"    # padat
        elif pop >= max_pop * 0.25:
            return "blue"      # sedang
        else:
            return "green"     # rendah

    # marker tiap kabupaten
    for _, row in df.iterrows():

        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue

        pop = row["populasi"]

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=pop / 300000,
            color=get_color(pop),
            fill=True,
            fill_color=get_color(pop),
            fill_opacity=0.7,
            popup=folium.Popup(
                f"""
                <b>{row['kabupaten']}</b><br>
                Populasi: {pop:,}
                """,
                max_width=250
            )
        ).add_to(map_kaltim)

    # =========================
    # LEGEND (KETERANGAN WARNA)
    # =========================
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        z-index:9999;
        background-color:white;
        padding:12px;
        border:2px solid grey;
        border-radius:8px;
        font-size:14px;
    ">
    <b>Legenda Kepadatan Penduduk</b><br><br>

    <i style="background:red;width:10px;height:10px;display:inline-block;"></i>
    Sangat Padat (≥ 75%)<br>

    <i style="background:orange;width:10px;height:10px;display:inline-block;"></i>
    Padat (50–75%)<br>

    <i style="background:blue;width:10px;height:10px;display:inline-block;"></i>
    Sedang (25–50%)<br>

    <i style="background:green;width:10px;height:10px;display:inline-block;"></i>
    Rendah (< 25%)<br>

    </div>
    """

    map_kaltim.get_root().html.add_child(folium.Element(legend_html))

    # render ke HTML Flask
    map_html = map_kaltim._repr_html_()

    return render_template("map.html", map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True)