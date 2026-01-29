import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title='Evaluación de tecnologías emergentes',
    page_icon=':sparkles:',
    layout='wide',
)

TECH_CATALOG = {
    'IA generativa': {
        'descripcion': (
            'Modelos que crean contenido (texto, imágenes, código) para apoyar la '
            'planificación didáctica, retroalimentación y creación de materiales.'
        ),
        'ejemplos': 'Chatbots, copilotos de escritura, generación de rúbricas.'
    },
    'Realidad aumentada (RA)': {
        'descripcion': (
            'Superposición de información digital en el entorno físico para enriquecer '
            'la exploración y el aprendizaje situado.'
        ),
        'ejemplos': 'Modelos 3D sobre libros, visitas guiadas interactivas.'
    },
    'Realidad virtual (RV)': {
        'descripcion': (
            'Entornos inmersivos que permiten simulaciones y experiencias seguras para '
            'prácticas de alto impacto.'
        ),
        'ejemplos': 'Laboratorios virtuales, recorridos históricos.'
    },
    'Analítica del aprendizaje': {
        'descripcion': (
            'Uso de datos educativos para monitorear el progreso y tomar decisiones '
            'pedagógicas informadas.'
        ),
        'ejemplos': 'Dashboards de seguimiento, alertas tempranas.'
    },
    'Microcredenciales digitales': {
        'descripcion': (
            'Reconocimientos modulares de competencias que facilitan trayectorias '
            'formativas flexibles.'
        ),
        'ejemplos': 'Badges, certificaciones por competencias.'
    },
}

EVALUATION_CRITERIA = {
    'Pertinencia pedagógica': {
        'weight': 0.30,
        'help': 'Alineación con objetivos de aprendizaje y modelos pedagógicos.'
    },
    'Facilidad de implementación': {
        'weight': 0.20,
        'help': 'Requerimientos técnicos, tiempo y esfuerzo para adoptarla.'
    },
    'Accesibilidad e inclusión': {
        'weight': 0.20,
        'help': 'Considera diversidad, accesibilidad y equidad.'
    },
    'Evidencia de impacto': {
        'weight': 0.20,
        'help': 'Disponibilidad de evidencia o casos de éxito.'
    },
    'Costo-beneficio': {
        'weight': 0.10,
        'help': 'Relación entre inversión y valor educativo.'
    },
}

if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []

if 'custom_tech' not in st.session_state:
    st.session_state.custom_tech = {}

st.title('📘 Evaluación de tecnologías emergentes en educación')
st.markdown(
    'Aplicación para estudiantes de la maestría en eInnovación Educativa. '
    'Aquí puedes evaluar tecnologías emergentes y comparar su potencial '
    'para apoyar experiencias de aprendizaje significativas.'
)

st.divider()

with st.sidebar:
    st.header('Catálogo de tecnologías')
    st.caption('Gestiona el listado base o agrega nuevas tecnologías.')

    custom_name = st.text_input('Nueva tecnología')
    custom_description = st.text_area('Descripción breve', height=120)
    custom_examples = st.text_input('Ejemplos o usos sugeridos')

    if st.button('Agregar al catálogo', use_container_width=True):
        if not custom_name.strip():
            st.warning('Agrega un nombre para la tecnología.')
        else:
            st.session_state.custom_tech[custom_name.strip()] = {
                'descripcion': custom_description.strip() or 'Descripción pendiente.',
                'ejemplos': custom_examples.strip() or 'Ejemplos por definir.'
            }
            st.success('Tecnología agregada al catálogo.')

catalog = {**TECH_CATALOG, **st.session_state.custom_tech}

main_col, summary_col = st.columns([2, 1], gap='large')

with main_col:
    st.subheader('Nueva evaluación')
    selected_tech = st.selectbox(
        'Selecciona la tecnología a evaluar',
        options=sorted(catalog.keys()),
    )

    tech_info = catalog.get(selected_tech, {})
    st.markdown(f"**Descripción:** {tech_info.get('descripcion', 'Sin descripción')}" )
    st.markdown(f"**Ejemplos:** {tech_info.get('ejemplos', 'Sin ejemplos')}" )

    with st.form('evaluation_form', clear_on_submit=False):
        st.markdown('### Criterios de evaluación (1 = Bajo, 5 = Alto)')
        scores = {}

        for criteria, metadata in EVALUATION_CRITERIA.items():
            scores[criteria] = st.slider(
                criteria,
                min_value=1,
                max_value=5,
                value=3,
                help=metadata['help'],
            )

        notes = st.text_area('Observaciones o recomendaciones', height=120)
        submit = st.form_submit_button('Guardar evaluación')

    if submit:
        weighted_score = sum(
            scores[criteria] * metadata['weight']
            for criteria, metadata in EVALUATION_CRITERIA.items()
        )
        st.session_state.evaluations.append({
            'Tecnología': selected_tech,
            'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
            **scores,
            'Puntaje ponderado': round(weighted_score, 2),
            'Observaciones': notes.strip(),
        })
        st.success('Evaluación registrada.')
        st.progress(min(weighted_score / 5, 1.0))

with summary_col:
    st.subheader('Resumen')

    if st.session_state.evaluations:
        eval_df = pd.DataFrame(st.session_state.evaluations)
        st.metric('Evaluaciones registradas', len(eval_df))
        st.metric(
            'Puntaje promedio',
            f"{eval_df['Puntaje ponderado'].mean():.2f} / 5"
        )

        st.markdown('**Promedio por tecnología**')
        avg_scores = (
            eval_df.groupby('Tecnología')['Puntaje ponderado']
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(avg_scores)
    else:
        st.info('Aún no hay evaluaciones. Completa el formulario para iniciar.')

st.divider()

st.subheader('Historial de evaluaciones')

if st.session_state.evaluations:
    eval_df = pd.DataFrame(st.session_state.evaluations)
    filter_tech = st.multiselect(
        'Filtrar por tecnología',
        options=sorted(eval_df['Tecnología'].unique()),
        default=sorted(eval_df['Tecnología'].unique()),
    )
    filtered_df = eval_df[eval_df['Tecnología'].isin(filter_tech)]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        'Descargar CSV',
        data=csv,
        file_name='evaluaciones_tecnologias.csv',
        mime='text/csv',
    )
else:
    st.warning('No hay evaluaciones para mostrar todavía.')
