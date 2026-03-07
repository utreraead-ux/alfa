from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Demo de automatización financiera", page_icon="📊", layout="wide")

DATA_FILENAME = Path(__file__).parent / "data" / "accounting_transactions.csv"


@st.cache_data
def load_accounting_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILENAME)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    return df


def build_income_statement(df: pd.DataFrame) -> pd.DataFrame:
    pivot = (
        df[df["tipo"].isin(["ingreso", "gasto"])]
        .pivot_table(index="mes", columns="tipo", values="monto", aggfunc="sum", fill_value=0)
        .reset_index()
    )
    pivot["ingreso"] = pivot.get("ingreso", 0)
    pivot["gasto"] = pivot.get("gasto", 0)
    pivot["utilidad_operativa"] = pivot["ingreso"] - pivot["gasto"]
    pivot["margen_operativo_pct"] = (pivot["utilidad_operativa"] / pivot["ingreso"].replace(0, pd.NA) * 100).fillna(0)
    return pivot


def build_cashflow(df: pd.DataFrame) -> pd.DataFrame:
    temp = df.copy()
    temp["monto_signed"] = temp["monto"]
    temp.loc[temp["tipo"].str.contains("salida"), "monto_signed"] *= -1

    flow = (
        temp[temp["tipo"].str.startswith("flujo")]
        .pivot_table(index="mes", columns="categoria", values="monto_signed", aggfunc="sum", fill_value=0)
        .reset_index()
    )

    for col in [
        "Flujo de caja operativo",
        "Flujo de caja inversion",
        "Flujo de caja financiamiento",
    ]:
        if col not in flow:
            flow[col] = 0

    flow["flujo_neto"] = flow[
        ["Flujo de caja operativo", "Flujo de caja inversion", "Flujo de caja financiamiento"]
    ].sum(axis=1)

    return flow


def to_currency(value: float) -> str:
    return f"${value:,.0f}"


st.title("📈 Automatización de reportes financieros")
st.write(
    "Genera automáticamente informes financieros, reportes de gestión e indicadores KPI "
    "a partir de datos del sistema contable."
)

data = load_accounting_data()

meses = sorted(data["mes"].unique())
selected_months = st.multiselect("Meses a analizar", meses, default=meses)
if not selected_months:
    st.warning("Selecciona al menos un mes para generar los reportes.")
    st.stop()

filtered = data[data["mes"].isin(selected_months)].copy()

income = build_income_statement(filtered)
cashflow = build_cashflow(filtered)

# Indicadores de gestión
ventas_totales = income["ingreso"].sum()
gastos_totales = income["gasto"].sum()
utilidad_total = income["utilidad_operativa"].sum()
margen_promedio = (utilidad_total / ventas_totales * 100) if ventas_totales else 0
runway_meses = (cashflow["flujo_neto"].sum() / (gastos_totales / max(len(income), 1))) if gastos_totales else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ventas acumuladas", to_currency(ventas_totales))
k2.metric("Gastos acumulados", to_currency(gastos_totales))
k3.metric("Utilidad operativa", to_currency(utilidad_total), f"{margen_promedio:.1f}% margen")
k4.metric("Runway estimado", f"{runway_meses:.1f} meses")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Informe financiero: Estado de resultados")
    st.dataframe(
        income.rename(
            columns={
                "mes": "Mes",
                "ingreso": "Ingresos",
                "gasto": "Gastos",
                "utilidad_operativa": "Utilidad operativa",
                "margen_operativo_pct": "Margen operativo %",
            }
        ),
        width="stretch",
    )
    st.line_chart(income, x="mes", y=["ingreso", "gasto", "utilidad_operativa"])

with right:
    st.subheader("Reporte de gestión: Flujo de caja")
    st.dataframe(cashflow.rename(columns={"mes": "Mes"}), width="stretch")
    st.bar_chart(cashflow, x="mes", y=["Flujo de caja operativo", "Flujo de caja inversion", "Flujo de caja financiamiento", "flujo_neto"])

st.divider()
st.subheader("Análisis de indicadores")

monthly_kpi = income[["mes", "ingreso", "gasto", "utilidad_operativa", "margen_operativo_pct"]].copy()
monthly_kpi["ratio_gasto_sobre_ventas_pct"] = (
    monthly_kpi["gasto"] / monthly_kpi["ingreso"].replace(0, pd.NA) * 100
).fillna(0)

st.dataframe(monthly_kpi.rename(columns={
    "mes": "Mes",
    "ingreso": "Ingresos",
    "gasto": "Gastos",
    "utilidad_operativa": "Utilidad",
    "margen_operativo_pct": "Margen %",
    "ratio_gasto_sobre_ventas_pct": "Ratio gasto/ventas %",
}), width="stretch")

csv_export = monthly_kpi.to_csv(index=False).encode("utf-8")
st.download_button(
    "Descargar análisis de indicadores (CSV)",
    data=csv_export,
    file_name="analisis_indicadores.csv",
    mime="text/csv",
)

st.caption("Demo generada con Streamlit. Datos contables simulados para fines de demostración.")
