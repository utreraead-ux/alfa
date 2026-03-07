# 📊 Demo de automatización de reportes financieros

Aplicación en **Streamlit** para generar automáticamente:

- **Informes financieros** (estado de resultados por mes)
- **Reportes de gestión** (flujo de caja operativo, inversión y financiamiento)
- **Análisis de indicadores (KPIs)** como margen operativo y ratio gasto/ventas

La demo toma datos desde un archivo contable simulado (`data/accounting_transactions.csv`) y construye reportes listos para visualizar y exportar.

## Cómo ejecutar

1. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta la app:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Abre en el navegador la URL local que muestra Streamlit.

## Datos

El archivo `data/accounting_transactions.csv` representa movimientos de un sistema contable con campos:

- `fecha`
- `centro_costo`
- `categoria`
- `monto`
- `tipo`
- `descripcion`

Puedes reemplazarlo con una exportación real de tu ERP/contabilidad para adaptar la demo a un caso productivo.
