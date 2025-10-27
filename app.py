import streamlit as st
import pandas as pd
import plotly.express as px

# =======================================================
# CONFIGURACIÓN DE LA PÁGINA
# =======================================================
st.set_page_config(
    page_title="🏨 Ocupación Turística España 2024",
    layout="wide"
)

# =======================================================
# CARGA DE DATOS
# =======================================================
df = pd.read_csv("ocupacion_ciudades.csv", sep=",", encoding="utf-8")
df["Tasa_ocupacion"] = df["Plazas_ocupadas"] / df["Plazas_oferta"]
df["Ingreso_medio_plaza"] = df["Ingresos_generados"] / df["Plazas_ocupadas"]
df["REVPAR"] = df["Ingresos_generados"] / df["Plazas_oferta"]

# =======================================================
# HEADER CENTRADO
# =======================================================
st.markdown(
    """
    <div style="text-align:center; background-color:#dbe9ff; padding:15px; border-radius:8px">
        <h1>🏨 Ocupación Turística España 2024</h1>
        <p style="font-size:18px;">
            Análisis de la Ocupación hotelera e Ingresos generados
            por las principales ciudades turísticas españolas: <b>Madrid</b>, <b>Barcelona</b>, <b>Valencia</b> y <b>Sevilla</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =======================================================
# FILTRADO DE DATOS INICIAL
# =======================================================
col_filters, col_main = st.columns([1, 5])

with col_filters:
    st.markdown(
        """
        <div style="background-color:#dbe9ff;padding:10px;border-radius:8px">
        <h4>🎛️ Filtros principales</h4>
        </div>
        """, unsafe_allow_html=True
    )
    ciudad = st.selectbox(
        "🏙️ Selecciona ciudad",
        ["Todas"] + sorted(df["Ciudad"].unique().tolist())
    )
    mes = st.slider("🗓️ Selecciona rango de meses", 1, 12, (1, 12))

# Filtrado según selección
df_filtrado = df[(df["Mes"] >= mes[0]) & (df["Mes"] <= mes[1])]
if ciudad != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Ciudad"] == ciudad]

# =======================================================
# KPIs Y CONTENIDO PRINCIPAL
# =======================================================
with col_main:
    plazas_oferta = df_filtrado["Plazas_oferta"].sum()
    plazas_ocupadas = df_filtrado["Plazas_ocupadas"].sum()
    tasa_media = (plazas_ocupadas / plazas_oferta) if plazas_oferta else 0
    ingresos_totales = df_filtrado["Ingresos_generados"].sum()
    ingreso_medio = ingresos_totales / plazas_ocupadas if plazas_ocupadas else 0

    st.subheader("📍 Indicadores clave (KPIs)")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    kpi_col1.metric("🏢 Plazas ofertadas", f"{plazas_oferta:,.0f}")
    kpi_col2.metric("🛏️ Plazas ocupadas", f"{plazas_ocupadas:,.0f}")
    kpi_col3.metric("📊 Tasa media ocupación", f"{tasa_media:.2%}")
    kpi_col4.metric("💶 Ingresos totales", f"€{ingresos_totales:,.0f}")
    kpi_col5.metric("💰 Ingreso medio por plaza ocupada", f"€{ingreso_medio:.2f}")

    st.markdown("---")

    # GRÁFICOS PRINCIPALES
    colA, colB = st.columns(2)

    fig_bar = px.bar(
        df_filtrado,
        x="Mes",
        y="Tasa_ocupacion",
        color="Ciudad",
        barmode="group",
        title="📅 Tasa de ocupación Mensual por Ciudad",
        color_discrete_map={
            "Madrid": "#1f77b4",
            "Barcelona": "#ff7f0e",
            "Valencia": "#2ca02c",
            "Sevilla": "#d62728"
        },
        height=500
    )
    fig_bar.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#ffffff", font=dict(size=14))
    colA.plotly_chart(fig_bar, use_container_width=True)

    fig_ingresos = px.line(
        df_filtrado.groupby(["Ciudad", "Mes"], as_index=False)["Ingresos_generados"].sum(),
        x="Mes",
        y="Ingresos_generados",
        color="Ciudad",
        markers=True,
        title="💶 Evolución mensual de Ingresos por Ciudad",
        color_discrete_map={
            "Madrid": "#1f77b4",
            "Barcelona": "#ff7f0e",
            "Valencia": "#2ca02c",
            "Sevilla": "#d62728"
        },
        height=500
    )
    fig_ingresos.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#ffffff", font=dict(size=14))
    colB.plotly_chart(fig_ingresos, use_container_width=True)

    # MAPA INTERACTIVO
    st.subheader("🗺️ Distribución geográfica de las Ciudades")
    df_mapa = df_filtrado.groupby("Ciudad", as_index=False).agg({
        "Latitud": "first",
        "Longitud": "first",
        "Plazas_oferta": "sum",
        "Plazas_ocupadas": "sum",
        "Ingresos_generados": "sum"
    })
    df_mapa["Tasa_ocupacion"] = df_mapa["Plazas_ocupadas"] / df_mapa["Plazas_oferta"]

    fig_map = px.scatter_mapbox(
        df_mapa,
        lat="Latitud",
        lon="Longitud",
        size="Ingresos_generados",
        color="Ciudad",
        hover_name="Ciudad",
        hover_data={"Tasa_ocupacion":":.1%", "Ingresos_generados":":,.0f"},
        color_discrete_map={
            "Madrid": "#1f77b4",
            "Barcelona": "#ff7f0e",
            "Valencia": "#2ca02c",
            "Sevilla": "#d62728"
        },
        size_max=40,
        zoom=5,
        mapbox_style="carto-positron",
        title="Mapa interactivo de Ocupación e Ingresos"
    )
    fig_map.update_layout(height=600)
    st.plotly_chart(fig_map, use_container_width=True)

    # =======================================================
    # HEATMAP DE REVPAR Y DONUT DE INGRESOS
    # =======================================================
    colH, colD = st.columns(2)

    # Heatmap de REVPAR
    with colH:
        st.subheader("🔥 Heatmap de REVPAR por Meses y Ciudad")

        # Filtramos meses válidos (1 a 12)
        df_heat = df_filtrado[(df_filtrado["Mes"] >= 1) & (df_filtrado["Mes"] <= 12)]
        df_heat = df_heat.groupby(["Ciudad", "Mes"], as_index=False)["REVPAR"].mean()

        # Creamos DataFrame completo de meses 1-12 para cada ciudad
        meses = pd.DataFrame({"Mes": range(1, 13)})
        df_heat_complete = pd.DataFrame()
        for ciudad in df_heat["Ciudad"].unique():
            temp_ciudad = df_heat[df_heat["Ciudad"] == ciudad]
            temp_complete = meses.merge(temp_ciudad, on="Mes", how="left")
            temp_complete["Ciudad"] = ciudad
            temp_complete["REVPAR"] = temp_complete["REVPAR"].fillna(0)
            df_heat_complete = pd.concat([df_heat_complete, temp_complete], ignore_index=True)

        fig_heat = px.density_heatmap(
            df_heat_complete,
            x="Mes",
            y="Ciudad",
            z="REVPAR",
            color_continuous_scale="Viridis",
            title="REVPAR promedio por Meses y Ciudad",
            height=400
        )
        fig_heat.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#ffffff", font=dict(size=14))
        st.plotly_chart(fig_heat, use_container_width=True)

    # Donut de ingresos
    with colD:
        st.subheader("🍩 Distribución de Ingresos por Ciudad")
        df_donut = df_filtrado.groupby("Ciudad", as_index=False)["Ingresos_generados"].sum()
        fig_donut_ciudad = px.pie(
            df_donut,
            names="Ciudad",
            values="Ingresos_generados",
            hole=0.5,
            title="Comparación de Ingresos generados por Ciudad",
            color="Ciudad",
            color_discrete_map={
                "Madrid": "#1f77b4",
                "Barcelona": "#ff7f0e",
                "Valencia": "#2ca02c",
                "Sevilla": "#d62728"
            }
        )
        fig_donut_ciudad.update_traces(textinfo='percent+label')
        fig_donut_ciudad.update_layout(height=450, paper_bgcolor="#ffffff", font=dict(size=14))
        st.plotly_chart(fig_donut_ciudad, use_container_width=True)

    # =======================================================
    # TABLA DETALLADA CENTRADA
    # =======================================================
    with st.expander("📋 Ver datos filtrados en detalle"):
        st.markdown(
            """
            <div style="display:flex; justify-content:center;">
                <div style="width:95%">
            """,
            unsafe_allow_html=True
        )

        st.dataframe(
            df_filtrado.style.format({
                "Tasa_ocupacion": "{:.2%}",
                "Ingresos_generados": "€{:,}",
                "Ingreso_medio_plaza": "€{:.2f}",
                "REVPAR": "€{:.2f}"
            }),
            use_container_width=True
        )

        st.markdown(
            """
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
