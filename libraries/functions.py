import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import streamlit as st

# --- FUNCIONES PARA CARGAR DATOS ---
@st.cache_resource
def cargar_datos_matricula(rute:str):
    try:
        df = pd.read_parquet(rute)
        if 'Ano_Inicio_Curso' in df.columns:
            df['Ano_Inicio_Curso'] = pd.to_numeric(df['Ano_Inicio_Curso'], errors='coerce').fillna(0).astype(int)
        if 'Curso_Academico' not in df.columns and 'Ano_Inicio_Curso' in df.columns:
            df['Curso_Academico'] = df['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
        for col in ['Matricula_Total', 'Matricula_Mujeres', 'Matricula_Hombres']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df.sort_values(by=['entidad', 'carrera', 'Ano_Inicio_Curso'], inplace=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data
def cargar_datos_instituciones(rute:str):
    try:
        df_uni = pd.read_parquet(rute)
        return df_uni
    except FileNotFoundError:
        return pd.DataFrame()
#-----------------------------------------------------

def calcular_cagr_dinamico(df_evolucion_total_carrera, ano_inicio_cagr, ano_fin_cagr):
    cagr_info = {"valor": "No calculable", "periodo": ""}
    if df_evolucion_total_carrera is None or df_evolucion_total_carrera.empty:
        return cagr_info
        
    anos_disponibles_carrera = sorted(df_evolucion_total_carrera['Ano_Inicio_Curso'].unique())
    
    if len(anos_disponibles_carrera) < 2 or ano_inicio_cagr is None or ano_fin_cagr is None:
        return cagr_info # No hay suficientes datos o no se seleccionó período

    if ano_inicio_cagr < ano_fin_cagr:
        datos_cagr_periodo = df_evolucion_total_carrera[
            (df_evolucion_total_carrera['Ano_Inicio_Curso'] >= ano_inicio_cagr) &
            (df_evolucion_total_carrera['Ano_Inicio_Curso'] <= ano_fin_cagr)
        ]
        if len(datos_cagr_periodo['Ano_Inicio_Curso'].unique()) >= 2:
            matricula_inicio_c = datos_cagr_periodo[datos_cagr_periodo['Ano_Inicio_Curso'] == datos_cagr_periodo['Ano_Inicio_Curso'].min()]['Matricula_Total'].sum()
            matricula_fin_c = datos_cagr_periodo[datos_cagr_periodo['Ano_Inicio_Curso'] == datos_cagr_periodo['Ano_Inicio_Curso'].max()]['Matricula_Total'].sum()
            if matricula_inicio_c > 0 and matricula_fin_c > 0:
                n_anos_efectivos_cagr = datos_cagr_periodo['Ano_Inicio_Curso'].nunique()
                if n_anos_efectivos_cagr > 1:
                    cagr_val_c = ((matricula_fin_c / matricula_inicio_c)**(1 / (n_anos_efectivos_cagr - 1)) - 1) * 100
                    cagr_info["valor"] = f"{cagr_val_c:.2f}%"
                    cagr_info["periodo"] = f"({datos_cagr_periodo['Ano_Inicio_Curso'].min()}-{datos_cagr_periodo['Ano_Inicio_Curso'].max()})"
                else: cagr_info["valor"] = "Período corto" # Muy corto
            else: cagr_info["valor"] = "Matrícula cero"
        else: cagr_info["valor"] = "Datos insuficientes" # Insuficientes en período
    else: cagr_info["valor"] = "Rango inválido"
    return cagr_info

#------------------------------------------------------------------------------------------------
@st.cache_data
def analisis_guia_universidades(df_instituciones, df_matricula, provincia_seleccionada=None, municipio_seleccionado=None):
    if df_instituciones.empty:
        return {}, "Datos de instituciones no disponibles."

    df_unis_filtradas = df_instituciones.copy()
    if provincia_seleccionada and provincia_seleccionada != "TODAS LAS PROVINCIAS":
        df_unis_filtradas = df_unis_filtradas[df_unis_filtradas['provincia'] == provincia_seleccionada]
    if municipio_seleccionado and municipio_seleccionado != "TODOS LOS MUNICIPIOS":
        df_unis_filtradas = df_unis_filtradas[df_unis_filtradas['municipio'] == municipio_seleccionado]
    
    if df_unis_filtradas.empty:
        # ... (mensaje de error como antes) ...
        msg = "No se encontraron instituciones"
        if provincia_seleccionada and provincia_seleccionada != "TODAS LAS PROVINCIAS":
            msg += f" en la provincia de '{provincia_seleccionada}'"
        if municipio_seleccionado and municipio_seleccionado != "TODOS LOS MUNICIPIOS":
            msg += f" en el municipio de '{municipio_seleccionado}'"
        msg += "."
        return {}, msg

    ano_mas_reciente_matricula = 0
    df_matricula_ultimo_ano_carreras = pd.DataFrame()
    df_matricula_ultimo_ano_general_uni = pd.DataFrame() # Para totales de género por universidad

    if not df_matricula.empty:
        ano_mas_reciente_matricula = df_matricula['Ano_Inicio_Curso'].max()
        
        # Matrícula por carrera para la guía
        df_matricula_ultimo_ano_carreras = df_matricula[df_matricula['Ano_Inicio_Curso'] == ano_mas_reciente_matricula]\
                                    .groupby(['entidad', 'rama_ciencias', 'carrera'])['Matricula_Total'].sum().reset_index()
        df_matricula_ultimo_ano_carreras = df_matricula_ultimo_ano_carreras[df_matricula_ultimo_ano_carreras['Matricula_Total'] > 0]

        # Totales de género por universidad para el último año
        df_matricula_ultimo_ano_general_uni = df_matricula[df_matricula['Ano_Inicio_Curso'] == ano_mas_reciente_matricula]\
                                    .groupby('entidad').agg(
                                        Total_General_Uni=('Matricula_Total', 'sum'),
                                        Total_Mujeres_Uni=('Matricula_Mujeres', 'sum'),
                                        Total_Hombres_Uni=('Matricula_Hombres', 'sum')
                                    ).reset_index()

    guia_data = {}
    columnas_oferta_ramas = [col for col in df_instituciones.columns if col.startswith('oferta_')]
    mapa_oferta_a_rama = { # Asegúrate que estas claves coincidan con tus columnas
        'oferta_tecnicas': 'Ciencias Técnicas',
        'oferta_naturales_mat': 'Ciencias Naturales y Matemáticas',
        'oferta_agropecuarias': 'Ciencias Agropecuarias',
        'oferta_economicas': 'Ciencias Económicas',
        'oferta_sociales_humanisticas': 'Ciencias Sociales y Humanísticas',
        'oferta_pedagogicas': 'Ciencias Pedagógicas',
        'oferta_cultura_fisica_deporte': 'Ciencias de la Cultura Física y el Deporte',
        'oferta_medicas': 'Ciencias Médicas',
        'oferta_artes': 'Ciencias de las Artes',
        'oferta_militares': 'Ciencias Militares'
    }

    df_unis_filtradas_sorted = df_unis_filtradas.sort_values(by='nombre_institucion')

    for _, uni_row in df_unis_filtradas_sorted.iterrows():
        sigla_uni = uni_row['sigla_institucion']
        nombre_uni = uni_row['nombre_institucion']
        
        # Obtener datos de género para esta universidad
        datos_genero_uni = df_matricula_ultimo_ano_general_uni[
            df_matricula_ultimo_ano_general_uni['entidad'] == sigla_uni
        ]
        
        info_basica_uni = {
            "sigla": sigla_uni,
            "ano_creacion": uni_row.get('ano_creacion', 'N/D'),
            "organismo": uni_row.get('organismo', 'N/D'),
            "direccion": uni_row.get('direccion_fisica', 'N/D'),
            "provincia": uni_row.get('provincia', 'N/D'),
            "municipio": uni_row.get('municipio', 'N/D'),
            "modalidad_estudio": uni_row.get('modalidad_estudio', 'N/D'), # Nueva info
            "datos_genero_uni": { # Para el gráfico de pastel
                'Mujeres': datos_genero_uni['Total_Mujeres_Uni'].iloc[0] if not datos_genero_uni.empty else 0,
                'Hombres': datos_genero_uni['Total_Hombres_Uni'].iloc[0] if not datos_genero_uni.empty else 0,
                'Total': datos_genero_uni['Total_General_Uni'].iloc[0] if not datos_genero_uni.empty else 0,
            },
            "ramas_ofertadas": []
        }
        
        ramas_activas_uni = []
        for col_oferta in columnas_oferta_ramas:
            if uni_row[col_oferta] == True:
                nombre_rama_legible = mapa_oferta_a_rama.get(col_oferta, col_oferta.replace("oferta_", "").replace("_", " ").title())
                carreras_info = []
                if not df_matricula_ultimo_ano_carreras.empty:
                    carreras_de_rama_uni = df_matricula_ultimo_ano_carreras[
                        (df_matricula_ultimo_ano_carreras['entidad'] == sigla_uni) &
                        (df_matricula_ultimo_ano_carreras['rama_ciencias'] == nombre_rama_legible)
                    ].sort_values(by='Matricula_Total', ascending=False)
                    for _, carrera_row in carreras_de_rama_uni.iterrows():
                        carreras_info.append({
                            "nombre_carrera": carrera_row['carrera'],
                            "matricula_ultimo_ano": int(carrera_row['Matricula_Total'])
                        })
                if carreras_info or uni_row[col_oferta]:
                    ramas_activas_uni.append({ "nombre_rama": nombre_rama_legible, "carreras": carreras_info })
        
        info_basica_uni["ramas_ofertadas"] = sorted(ramas_activas_uni, key=lambda x: x['nombre_rama'])
        guia_data[nombre_uni] = info_basica_uni

    return guia_data, (f"Guía generada para el curso {ano_mas_reciente_matricula}-{ano_mas_reciente_matricula+1}." 
                       if ano_mas_reciente_matricula > 0 else 
                       "Guía generada (datos de matrícula del último año no disponibles).")

@st.cache_data
def analisis_perfil_carrera(df, carrera_seleccionada): # Eliminados parámetros de CAGR
    if df.empty:
        return None, None, None, None, None, "DataFrame vacío." # fig_evol_gen, df_evol_para_cagr, df_unis, porc_mujeres, rama, msg
    if not carrera_seleccionada:
        return None, None, None, None, None, "Carrera no seleccionada."

    df_carrera_completa = df[df['carrera'] == carrera_seleccionada]
    if df_carrera_completa.empty:
        return None, None, None, None, None, f"No hay datos para la carrera '{carrera_seleccionada}'."

    rama_identificada = df_carrera_completa['rama_ciencias'].iloc[0] if not df_carrera_completa.empty else "No identificada"

    # 1. Evolución histórica de matrícula (Total, Mujeres, Hombres) para ESA CARRERA
    evolucion_genero_carrera = df_carrera_completa.groupby('Ano_Inicio_Curso').agg(
        Matricula_Total=('Matricula_Total', 'sum'),
        Matricula_Mujeres=('Matricula_Mujeres', 'sum'),
        Matricula_Hombres=('Matricula_Hombres', 'sum')
    ).reset_index()

    if 'Curso_Academico' not in evolucion_genero_carrera.columns and not evolucion_genero_carrera.empty:
        evolucion_genero_carrera['Curso_Academico'] = evolucion_genero_carrera['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    fig_evolucion_genero = None
    if not evolucion_genero_carrera.empty:
        df_melted_evolucion = evolucion_genero_carrera.melt(
            id_vars=['Ano_Inicio_Curso', 'Curso_Academico'], 
            value_vars=['Matricula_Total', 'Matricula_Mujeres', 'Matricula_Hombres'],
            var_name='Tipo_Matricula', 
            value_name='Cantidad'
        )
        # Mapeo de nombres para la leyenda del gráfico de evolución
        mapa_nombres_leyenda = {
            'Matricula_Total': 'Total Estudiantes',
            'Matricula_Mujeres': 'Mujeres',
            'Matricula_Hombres': 'Hombres'
        }
        df_melted_evolucion['Tipo_Matricula_Display'] = df_melted_evolucion['Tipo_Matricula'].map(mapa_nombres_leyenda)
        
        fig_evolucion_genero = px.line(
            df_melted_evolucion, 
            x='Curso_Academico', 
            y='Cantidad', 
            color='Tipo_Matricula_Display', # Usar la columna con nombres amigables
            title=f"Evolución Histórica Matrícula y Género: {carrera_seleccionada}",
            markers=True,
            labels={'Cantidad': 'Número de Estudiantes', 'Tipo_Matricula_Display': 'Desglose Matrícula'}
        )
        fig_evolucion_genero.update_layout(xaxis_title='Curso Académico', yaxis_title='Número de Estudiantes')

    # 2. Devolver DataFrame para cálculo de CAGR (evolucion_genero_carrera contiene Matricula_Total y Ano_Inicio_Curso)
    df_evolucion_para_cagr = evolucion_genero_carrera[['Ano_Inicio_Curso', 'Matricula_Total']].copy()

    # 3. Universidades que la imparten y matrícula en último año
    ano_mas_reciente_global = df['Ano_Inicio_Curso'].max()
    df_unis_carrera = df_carrera_completa[df_carrera_completa['Ano_Inicio_Curso'] == ano_mas_reciente_global]\
                        .groupby('entidad')['Matricula_Total'].sum().sort_values(ascending=False).reset_index()
    df_unis_carrera = df_unis_carrera[df_unis_carrera['Matricula_Total'] > 0]
    df_unis_carrera.rename(columns={'entidad':'Universidad', 'Matricula_Total':f'Matrícula {ano_mas_reciente_global}-{ano_mas_reciente_global+1}'}, inplace=True)

    # 4. Datos de género para el último año (para gráfico de pastel y métrica)
    # (Matricula_Mujeres y Matricula_Hombres ya están en evolucion_genero_carrera para el último año)
    datos_genero_ultimo_ano = None
    if not evolucion_genero_carrera.empty:
        ultimo_ano_data = evolucion_genero_carrera[evolucion_genero_carrera['Ano_Inicio_Curso'] == ano_mas_reciente_global]
        if not ultimo_ano_data.empty:
            datos_genero_ultimo_ano = {
                'Mujeres': ultimo_ano_data['Matricula_Mujeres'].iloc[0],
                'Hombres': ultimo_ano_data['Matricula_Hombres'].iloc[0],
                'Total': ultimo_ano_data['Matricula_Total'].iloc[0]
            }
    
    return fig_evolucion_genero, df_evolucion_para_cagr, df_unis_carrera, datos_genero_ultimo_ano, rama_identificada, None


# A1: Evolución Histórica y Proyectada de la Matrícula Nacional
@st.cache_data
def analisis_A1(df, incluir_proyeccion=False, showlegend=False):
    if df.empty:
        return None, "DataFrame vacío."
    
    nacional_evolucion_completa = df.groupby('Ano_Inicio_Curso')['Matricula_Total'].sum().reset_index()
    if nacional_evolucion_completa.empty:
        return None, "No hay datos para el análisis A1."
        
    nacional_evolucion_completa['Tipo'] = 'Histórica'
    nacional_evolucion_completa['Curso_Academico'] = nacional_evolucion_completa['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    df_para_graficar = nacional_evolucion_completa.copy()
    titulo_info = "Evolución Histórica"

    if incluir_proyeccion:
        N_ULTIMOS_ANOS_REGRESION = 6
        if len(nacional_evolucion_completa) < 2:
            return None, "Datos históricos insuficientes para proyección."
        
        if len(nacional_evolucion_completa) < N_ULTIMOS_ANOS_REGRESION:
            datos_regresion = nacional_evolucion_completa
            msg_regresion = f"Usando todos los {len(datos_regresion)} años"
        else:
            datos_regresion = nacional_evolucion_completa.tail(N_ULTIMOS_ANOS_REGRESION)
            msg_regresion = f"Basada en {N_ULTIMOS_ANOS_REGRESION} últimos años"

        X_reg = datos_regresion['Ano_Inicio_Curso'].values.reshape(-1, 1)
        y_reg = datos_regresion['Matricula_Total'].values
        model = LinearRegression().fit(X_reg, y_reg) 
        
        ultimo_ano_historico_num = nacional_evolucion_completa['Ano_Inicio_Curso'].max()
        ultima_matricula_historica = nacional_evolucion_completa[nacional_evolucion_completa['Ano_Inicio_Curso'] == ultimo_ano_historico_num]['Matricula_Total'].iloc[0]
        anos_proyeccion_puros = np.array([ultimo_ano_historico_num + 1, ultimo_ano_historico_num + 2])
        matricula_proyectada_pura = model.predict(anos_proyeccion_puros.reshape(-1,1))
         
        df_proyeccion_graf = pd.DataFrame({
            'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_historico_num], anos_proyeccion_puros)),
            'Matricula_Total': np.concatenate(([ultima_matricula_historica], matricula_proyectada_pura.round(0).clip(min=0))),
            'Tipo': 'Proyectada'
        })
        df_proyeccion_graf['Curso_Academico'] = df_proyeccion_graf['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
        df_para_graficar = pd.concat([nacional_evolucion_completa, df_proyeccion_graf], ignore_index=True)
        titulo_info = f"Evolución y Proyección (Reg. Lin. {msg_regresion})"

    fig = px.line(df_para_graficar, x='Curso_Academico', y='Matricula_Total', 
                  line_dash='Tipo' if incluir_proyeccion else None, 
                  color='Tipo' if incluir_proyeccion else None, 
                  markers=True, 
                  labels={'Matricula_Total': 'Matrícula Total Nacional', 'Tipo': 'Dato'},
                  title=f'Matrícula Nacional Total: {titulo_info}')
    fig.update_layout(xaxis_title='Curso Académico', yaxis_title='Matrícula Total',showlegend=showlegend)
    
    if incluir_proyeccion and len(nacional_evolucion_completa) >= 2:
        x_vline_pos = len(nacional_evolucion_completa) -1 # El índice del último punto histórico
        fig.add_vline(x=x_vline_pos, line_width=2, line_dash="dot", line_color="purple",
                      annotation_text="Inicio Proyección", annotation_position="top right",
                      annotation_font_size=10, annotation_font_color="grey")
    return fig, None

# A2: Distribución y Evolución de la Matrícula por Rama de Ciencias
@st.cache_data
def analisis_A2(df, incluir_proyeccion=False):
    if df.empty:
        return None, None, "DataFrame vacío."
    
    rama_evolucion_historica = df.groupby(['Ano_Inicio_Curso', 'rama_ciencias'])['Matricula_Total'].sum().reset_index()
    if rama_evolucion_historica.empty:
        return None, None, "No hay datos históricos por rama."
        
    rama_evolucion_historica['Tipo'] = 'Histórica'
    if 'Curso_Academico' not in rama_evolucion_historica.columns:
        rama_evolucion_historica['Curso_Academico'] = rama_evolucion_historica['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")

    df_proyecciones_ramas_concat = pd.DataFrame()
    ramas_unicas = rama_evolucion_historica['rama_ciencias'].unique()
    max_y_value_for_annotation = 0
    proyeccion_realizada_alguna_rama = False
    N_ULTIMOS_ANOS_REGRESION = 6
    titulo_abs = "Evolución Histórica por Rama"

    if incluir_proyeccion:
        for rama in ramas_unicas:
            data_rama_hist = rama_evolucion_historica[rama_evolucion_historica['rama_ciencias'] == rama]
            if data_rama_hist['Matricula_Total'].max() > max_y_value_for_annotation:
                 max_y_value_for_annotation = data_rama_hist['Matricula_Total'].max()

            if len(data_rama_hist) < 2: continue
            datos_regresion_rama = data_rama_hist.tail(N_ULTIMOS_ANOS_REGRESION) if len(data_rama_hist) >= N_ULTIMOS_ANOS_REGRESION else data_rama_hist
            
            X_reg_rama = datos_regresion_rama['Ano_Inicio_Curso'].values.reshape(-1, 1)
            y_reg_rama = datos_regresion_rama['Matricula_Total'].values
            model_rama = LinearRegression().fit(X_reg_rama, y_reg_rama)
            
            ultimo_ano_hist_rama = data_rama_hist['Ano_Inicio_Curso'].max()
            ultima_mat_hist_rama = data_rama_hist[data_rama_hist['Ano_Inicio_Curso'] == ultimo_ano_hist_rama]['Matricula_Total'].iloc[0]
            anos_proy_puros_rama = np.array([ultimo_ano_hist_rama + 1, ultimo_ano_hist_rama + 2])
            mat_proy_pura_rama = model_rama.predict(anos_proy_puros_rama.reshape(-1,1))

            df_proy_rama_graf = pd.DataFrame({
                'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_hist_rama], anos_proy_puros_rama)),
                'Matricula_Total': np.concatenate(([ultima_mat_hist_rama], mat_proy_pura_rama.round(0).clip(min=0))),
                'rama_ciencias': rama, 'Tipo': 'Proyectada' })
            if 'Curso_Academico' not in df_proy_rama_graf.columns:
                df_proy_rama_graf['Curso_Academico'] = df_proy_rama_graf['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
            df_proyecciones_ramas_concat = pd.concat([df_proyecciones_ramas_concat, df_proy_rama_graf], ignore_index=True)
            proyeccion_realizada_alguna_rama = True
            if df_proy_rama_graf['Matricula_Total'].max() > max_y_value_for_annotation:
                max_y_value_for_annotation = df_proy_rama_graf['Matricula_Total'].max()
        titulo_abs = f"Evolución y Proyección por Rama (Reg. Lin. {N_ULTIMOS_ANOS_REGRESION} últimos años o menos)"
    
    # Gráfico Absoluto
    fig_abs = go.Figure()
    colores_plotly = px.colors.qualitative.Plotly 
    for i, rama in enumerate(ramas_unicas):
        color_actual = colores_plotly[i % len(colores_plotly)]
        df_hist_rama_actual = rama_evolucion_historica[rama_evolucion_historica['rama_ciencias'] == rama]
        if not df_hist_rama_actual.empty:
            fig_abs.add_trace(go.Scatter(
                x=df_hist_rama_actual['Curso_Academico'], y=df_hist_rama_actual['Matricula_Total'],
                mode='lines+markers', name=rama, legendgroup=rama,
                line=dict(color=color_actual, dash='solid'), showlegend=True ))
        if incluir_proyeccion:
            df_proy_rama_actual = df_proyecciones_ramas_concat[df_proyecciones_ramas_concat['rama_ciencias'] == rama]
            if not df_proy_rama_actual.empty:
                fig_abs.add_trace(go.Scatter(
                    x=df_proy_rama_actual['Curso_Academico'], y=df_proy_rama_actual['Matricula_Total'],
                    mode='lines+markers', name=rama + " (Proy.)", legendgroup=rama,
                    line=dict(color=color_actual, dash='dash'), showlegend=False ))
    
    fig_abs.update_layout(title=titulo_abs, xaxis_title='Curso Académico', 
                          yaxis_title='Matrícula en Rama de Ciencias', legend_title_text='Rama de Ciencias')
    
    if incluir_proyeccion and proyeccion_realizada_alguna_rama and not rama_evolucion_historica.empty:
        x_vline_pos = rama_evolucion_historica['Ano_Inicio_Curso'].max()-rama_evolucion_historica['Ano_Inicio_Curso'].min() -1
        fig_abs.add_vline(x=x_vline_pos, line_width=2, line_dash="dot", line_color="grey",
                          annotation_text="Inicio Proyección", annotation_position="top right",
                          annotation_font_size=10, annotation_font_color="grey")

    # Gráfico Porcentual (siempre histórico)
    fig_pct = None
    if not rama_evolucion_historica.empty:
        total_anual_hist = rama_evolucion_historica.groupby('Ano_Inicio_Curso')['Matricula_Total'].sum().rename('Total_Anual_Rama')
        if not total_anual_hist.empty:
            rama_evolucion_pct_hist = rama_evolucion_historica.set_index('Ano_Inicio_Curso').join(total_anual_hist).reset_index()
            rama_evolucion_pct_hist['Porcentaje'] = np.where(
                rama_evolucion_pct_hist['Total_Anual_Rama'] > 0,
                (rama_evolucion_pct_hist['Matricula_Total'] / rama_evolucion_pct_hist['Total_Anual_Rama']) * 100, 0 )
            if 'Curso_Academico' not in rama_evolucion_pct_hist.columns: # Asegurar columna
                rama_evolucion_pct_hist['Curso_Academico'] = rama_evolucion_pct_hist['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
            fig_pct = px.area(rama_evolucion_pct_hist, x='Curso_Academico', y='Porcentaje', color='rama_ciencias',
                        title='Distribución Porcentual Histórica de la Matrícula por Rama de Ciencias',
                        labels={'Porcentaje': '% Matrícula'})
            fig_pct.update_layout(xaxis_title='Curso Académico', yaxis_title='Porcentaje de Matrícula (%)')
    return fig_abs, fig_pct, None

# A3: Ranking y Evolución de Carreras por Demanda
@st.cache_data
def analisis_A3(df):
    if df.empty:
        return None, None, None, "DataFrame vacío."
    
    ano_mas_reciente = df['Ano_Inicio_Curso'].max()
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"
    carreras_demanda_reciente = df[df['Ano_Inicio_Curso'] == ano_mas_reciente].groupby('carrera')['Matricula_Total'].sum().sort_values(ascending=False)
    
    if carreras_demanda_reciente.empty:
        return None, None, None, f"No hay datos de demanda de carreras para {curso_mas_reciente}."

    df_todas_carreras_ranking = carreras_demanda_reciente.reset_index()
    
    # Para el gráfico de evolución, tomaremos las N más demandadas actualmente
    top_n_grafico = 10
    carreras_para_grafico = df_todas_carreras_ranking.head(top_n_grafico)['carrera'].tolist()
    
    fig = None
    if carreras_para_grafico:
        evolucion_carreras = df[df['carrera'].isin(carreras_para_grafico)].groupby(['Ano_Inicio_Curso', 'carrera'])['Matricula_Total'].sum().reset_index()
        if not evolucion_carreras.empty:
            evolucion_carreras['Curso_Academico'] = evolucion_carreras['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
            fig = px.line(evolucion_carreras, x='Curso_Academico', y='Matricula_Total', color='carrera',
                        title=f'Evolución Histórica de Matrícula (Top {top_n_grafico} Carreras Actuales)',
                        markers=True, labels={'Matricula_Total': 'Matrícula Total'})
            fig.update_layout(xaxis_title='Curso Académico', yaxis_title='Matrícula en Carrera')
    
    return fig, df_todas_carreras_ranking, None, None # Fig, Df ranking, Df bottom (None por ahora), Msg (None)

# A4: Análisis de la Brecha de Género
@st.cache_data
def analisis_A4(df):
    if df.empty:
        return None, None, "DataFrame vacío."
    
    df_genero = df.copy()
    df_genero['Porcentaje_Mujeres'] = np.where(
        df_genero['Matricula_Total'] > 0,
        (df_genero['Matricula_Mujeres'] / df_genero['Matricula_Total']) * 100, np.nan )
    
    ano_mas_reciente = df_genero['Ano_Inicio_Curso'].max()
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"

    genero_rama_reciente = df_genero[df_genero['Ano_Inicio_Curso'] == ano_mas_reciente]\
        .groupby('rama_ciencias').agg(
            Total_Mujeres=('Matricula_Mujeres', 'sum'), Total_Hombres=('Matricula_Hombres', 'sum'),
            Total_General=('Matricula_Total', 'sum')).reset_index()
    genero_rama_reciente['Porcentaje_Mujeres'] = np.where(
        genero_rama_reciente['Total_General'] > 0,
        (genero_rama_reciente['Total_Mujeres'] / genero_rama_reciente['Total_General']) * 100, np.nan )
    fig1 = px.bar(genero_rama_reciente.dropna(subset=['Porcentaje_Mujeres']).sort_values('Porcentaje_Mujeres', ascending=False), 
                  x='rama_ciencias', y='Porcentaje_Mujeres',
                  title=f'Porcentaje de Mujeres por Rama de Ciencias ({curso_mas_reciente})',
                  labels={'Porcentaje_Mujeres': '% Mujeres', 'rama_ciencias': 'Rama de Ciencias'})
    fig1.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="50% Paridad")
    fig1.update_layout(yaxis_range=[0,100])

    genero_carrera_reciente = df_genero[df_genero['Ano_Inicio_Curso'] == ano_mas_reciente]\
        .groupby('carrera').agg(
            Total_Mujeres=('Matricula_Mujeres', 'sum'), Total_Hombres=('Matricula_Hombres', 'sum'),
            Total_General=('Matricula_Total', 'sum')).reset_index()
    genero_carrera_reciente['Porcentaje_Mujeres'] = np.where(
        genero_carrera_reciente['Total_General'] > 0,
        (genero_carrera_reciente['Total_Mujeres'] / genero_carrera_reciente['Total_General']) * 100, np.nan )
    genero_carrera_reciente_filtrado = genero_carrera_reciente[genero_carrera_reciente['Total_General'] >= 20].dropna(subset=['Porcentaje_Mujeres']) # Matrícula >=20
    
    top_fem = genero_carrera_reciente_filtrado.sort_values('Porcentaje_Mujeres', ascending=False).head(10)
    top_masc = genero_carrera_reciente_filtrado.sort_values('Porcentaje_Mujeres', ascending=True).head(10)
    
    fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Top 10 Carreras con Mayor % de Mujeres", "Top 10 Carreras con Menor % de Mujeres"))
    if not top_fem.empty:
        fig2.add_trace(go.Bar(x=top_fem['carrera'], y=top_fem['Porcentaje_Mujeres'], name='Mayoría Mujeres'), row=1, col=1)
    if not top_masc.empty:
        fig2.add_trace(go.Bar(x=top_masc['carrera'], y=top_masc['Porcentaje_Mujeres'], name='Minoría Mujeres'), row=1, col=2)
    fig2.update_layout(title_text=f'Desbalance de Género en Carreras ({curso_mas_reciente}, Matrícula >= 20)',
                       showlegend=False, height=500)
    min_y_fem = top_fem['Porcentaje_Mujeres'].min() if not top_fem.empty else 50
    max_y_masc = top_masc['Porcentaje_Mujeres'].max() if not top_masc.empty else 50
    fig2.update_yaxes(title_text="% Mujeres", row=1, col=1, range=[max(0, min_y_fem - 10 if min_y_fem > 10 else 0), 100])
    fig2.update_yaxes(title_text="% Mujeres", row=1, col=2, range=[0, min(100, max_y_masc + 10 if max_y_masc < 90 else 100)])
    fig2.add_hline(y=50, line_dash="dash", line_color="red", row=1, col=1,annotation_text="50%")
    fig2.add_hline(y=50, line_dash="dash", line_color="red", row=1, col=2,annotation_text="50%")
    return fig1, fig2, None

# A5: Análisis de Concentración y Especialización
@st.cache_data
def analisis_A5(df):
    if df.empty:
        return None, None, "DataFrame vacío."
    
    ano_mas_reciente = df['Ano_Inicio_Curso'].max()
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"
    df_reciente = df[df['Ano_Inicio_Curso'] == ano_mas_reciente]

    df_carreras_pocas_unis = None
    if not df_reciente.empty:
        carreras_pocas_unis_data = df_reciente[df_reciente['Matricula_Total'] > 0].groupby('carrera')['entidad'].nunique().sort_values(ascending=True)
        if not carreras_pocas_unis_data.empty:
            df_carreras_pocas_unis = carreras_pocas_unis_data.reset_index().rename(columns={'entidad': 'Num_Universidades_Ofertan'})

    fig_treemap = None
    df_treemap_data = df_reciente[df_reciente['Matricula_Total'] > 0]
    if not df_treemap_data.empty:
        fig_treemap = px.treemap(df_treemap_data, path=[px.Constant("Todas las Universidades"), 'entidad', 'rama_ciencias', 'carrera'], 
                         values='Matricula_Total', title=f'Distribución de Matrícula ({curso_mas_reciente})',
                         color='Matricula_Total', hover_data=['Matricula_Total'], height=700)
        fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    return fig_treemap, df_carreras_pocas_unis, None

# A6: Tasas de Crecimiento Anual Compuesto (CAGR)
@st.cache_data
def analisis_A6(df):
    if df.empty or len(df['Ano_Inicio_Curso'].unique()) < 2:
        return None, None, "Datos insuficientes para CAGR."
    
    cagr_data = []
    min_year = df['Ano_Inicio_Curso'].min()
    max_year = df['Ano_Inicio_Curso'].max()

    for carrera, group in df.groupby('carrera'):
        matricula_inicio = group[group['Ano_Inicio_Curso'] == min_year]['Matricula_Total'].sum()
        matricula_fin = group[group['Ano_Inicio_Curso'] == max_year]['Matricula_Total'].sum()
        if matricula_inicio > 0 and matricula_fin > 0:
            n_anos_efectivos = group['Ano_Inicio_Curso'].nunique()
            if n_anos_efectivos > 1:
                 cagr_val = ((matricula_fin / matricula_inicio)**(1 / (n_anos_efectivos - 1)) - 1) * 100
                 cagr_data.append({'carrera': carrera, 'CAGR (%)': cagr_val, 'Matricula_Inicio': matricula_inicio, 'Matricula_Fin': matricula_fin})
    
    if not cagr_data: return None, None, "No se calcularon datos de CAGR."
    df_cagr = pd.DataFrame(cagr_data).sort_values('CAGR (%)', ascending=False).dropna()
    if df_cagr.empty: return None, None, "No hay datos de CAGR válidos."

    fig_top_cagr = px.bar(df_cagr.head(15), x='carrera', y='CAGR (%)', 
                 title=f'Top 15 Carreras por Mayor Crecimiento Promedio Anual ({min_year}-{max_year})')
    fig_bottom_cagr = px.bar(df_cagr.tail(15).sort_values('CAGR (%)', ascending=True), x='carrera', y='CAGR (%)', 
                 title=f'Top 15 Carreras por Menor Crecimiento/Mayor Decrecimiento Promedio Anual ({min_year}-{max_year})')
    return fig_top_cagr, fig_bottom_cagr, None

# A7: Proyecciones de Matrícula para Carreras Seleccionadas
@st.cache_data
def analisis_A7(df, carreras_seleccionadas=None): # Nuevo parámetro
    if df.empty: return None, "DataFrame vacío."
        
    ano_mas_reciente_global = df['Ano_Inicio_Curso'].max()
    if pd.isna(ano_mas_reciente_global): return None, "No se pudo determinar el año más reciente."

    if not carreras_seleccionadas: # Si no se pasan carreras, tomar las top 3 por defecto
        carreras_recientes_data = df[df['Ano_Inicio_Curso'] == ano_mas_reciente_global]
        if carreras_recientes_data.empty: return None, f"No hay datos del año {int(ano_mas_reciente_global)} para seleccionar carreras top por defecto."
        carreras_a_analizar = carreras_recientes_data.groupby('carrera')['Matricula_Total'].sum().nlargest(3).index.tolist()
        if not carreras_a_analizar: return None, "No hay carreras top por defecto para proyectar."
        info_seleccion = "Proyectando las 3 carreras más demandadas actualmente."
    else:
        carreras_a_analizar = carreras_seleccionadas
        info_seleccion = f"Proyectando para: {', '.join(carreras_a_analizar)}."

    df_historico_general = df[df['carrera'].isin(carreras_a_analizar)].groupby(['Ano_Inicio_Curso', 'carrera'])['Matricula_Total'].sum().reset_index()
    if df_historico_general.empty:
        return None, f"No se encontraron datos históricos para las carreras seleccionadas: {', '.join(carreras_a_analizar)}."
        
    df_historico_general['Tipo'] = 'Histórica'
    df_historico_general['Curso_Academico'] = df_historico_general['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")

    df_graficar_final_carreras = df_historico_general.copy()
    proyeccion_hecha_alguna_carrera = False
    N_ULTIMOS_ANOS_REGRESION = 6
    msg_detalle_proy = []

    for carrera_nombre in carreras_a_analizar:
        data_carrera_hist = df_historico_general[
            (df_historico_general['carrera'] == carrera_nombre) & 
            (df_historico_general['Tipo'] == 'Histórica') # Asegurar que tomamos solo la data histórica para la regresión
        ]
        
        if len(data_carrera_hist) < 2: 
            msg_detalle_proy.append(f"{carrera_nombre} (datos históricos insuficientes para regresión)")
            continue 
        
        datos_reg_carrera = data_carrera_hist.tail(N_ULTIMOS_ANOS_REGRESION) if len(data_carrera_hist) >= N_ULTIMOS_ANOS_REGRESION else data_carrera_hist
        
        X_c = datos_reg_carrera['Ano_Inicio_Curso'].values.reshape(-1, 1)
        y_c = datos_reg_carrera['Matricula_Total'].values
        model_c = LinearRegression().fit(X_c, y_c)
            
        ultimo_ano_hist_c_val = data_carrera_hist['Ano_Inicio_Curso'].max()
        # Asegurarse de que ultima_mat_hist_c_val es un escalar
        ultima_mat_hist_c_val_series = data_carrera_hist[data_carrera_hist['Ano_Inicio_Curso'] == ultimo_ano_hist_c_val]['Matricula_Total']
        if ultima_mat_hist_c_val_series.empty:
             msg_detalle_proy.append(f"{carrera_nombre} (no se encontró matrícula para el último año histórico)")
             continue
        ultima_mat_hist_c_val = ultima_mat_hist_c_val_series.iloc[0]

        anos_proy_c = np.array([ultimo_ano_hist_c_val + 1, ultimo_ano_hist_c_val + 2])
        matricula_proyectada_carrera_final = model_c.predict(anos_proy_c.reshape(-1,1))

        df_proy_carrera_graf = pd.DataFrame({
            'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_hist_c_val], anos_proy_c)),
            'Matricula_Total': np.concatenate(([ultima_mat_hist_c_val], matricula_proyectada_carrera_final.round(0).clip(min=0))),
            'carrera': carrera_nombre, 'Tipo': 'Proyectada'})
        df_proy_carrera_graf['Curso_Academico'] = df_proy_carrera_graf['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
        
        # Para evitar duplicar los datos históricos que ya están en df_graficar_final_carreras
        # Solo concatenamos la parte proyectada (incluyendo el punto de anclaje)
        df_graficar_final_carreras = pd.concat([df_graficar_final_carreras, df_proy_carrera_graf], ignore_index=True)
        proyeccion_hecha_alguna_carrera = True
        msg_detalle_proy.append(f"{carrera_nombre} (Reg. Lin. {len(datos_reg_carrera)} años)")
        
    if not proyeccion_hecha_alguna_carrera and df_graficar_final_carreras.empty:
        return None, "No se pudieron generar proyecciones para las carreras seleccionadas, mostrando solo histórico si existe."

    if df_graficar_final_carreras.empty:
        return None, "No se generaron datos para graficar A7 (ni históricos ni proyectados)."
        
    fig = px.line(df_graficar_final_carreras, x='Curso_Academico', y='Matricula_Total', 
                  color='carrera', line_dash='Tipo', markers=True, 
                  labels={'Matricula_Total': 'Matrícula Total', 'Tipo': 'Dato', 'carrera': 'Carrera'},
                  title=f'Proyección de Matrícula para Carreras Seleccionadas')
    fig.update_layout(xaxis_title='Curso Académico', yaxis_title='Matrícula')
    
    if proyeccion_hecha_alguna_carrera and not df_historico_general.empty:
        # Vline general para el inicio de proyección
        maxx = df_historico_general['Ano_Inicio_Curso'].max()
        minn = df_historico_general['Ano_Inicio_Curso'].min()
        punto_transicion_x_str_global = maxx-minn-1
        fig.add_vline(x=punto_transicion_x_str_global, line_width=2, line_dash="dot", line_color="grey",
                      annotation_text="Inicio Proyección", annotation_position="top right",
                      annotation_font_size=10, annotation_font_color="grey")
                      
    return fig, f"{info_seleccion} Métodos: {'; '.join(msg_detalle_proy)}."

# A8: Análisis de la Matrícula "Cero" o Muy Baja
@st.cache_data
def analisis_A8(df):
    if df.empty:
        return {}, "DataFrame vacío."
    
    # El primer año real de datos en el dataset.
    primer_ano_datos = df['Ano_Inicio_Curso'].min()
    max_year = df['Ano_Inicio_Curso'].max()
    resultados = {}
    umbral_bajo = 10 

    carreras_nuevas_ofertas = []
    for (entidad, carrera), group in df.groupby(['entidad', 'carrera']):
        # Primera aparición de matrícula > 0 para esta carrera/entidad
        primera_aparicion_ano = group[group['Matricula_Total'] > 0]['Ano_Inicio_Curso'].min()
        # Última matrícula registrada
        mat_ultimo_ano = group[group['Ano_Inicio_Curso'] == max_year]['Matricula_Total'].sum()

        # Si la primera aparición no es NaN (es decir, existe la carrera con matrícula)
        # Y si esta primera aparición es DESPUÉS del primer año del dataset
        # Y si tiene matrícula en el último año (para asegurar que sigue activa)
        if pd.notna(primera_aparicion_ano) and primera_aparicion_ano > primer_ano_datos and mat_ultimo_ano > 0:
            carreras_nuevas_ofertas.append({
                'Entidad': entidad, 'Carrera': carrera, 
                'Año Inicio Oferta Detectado': int(primera_aparicion_ano), 
                'Matrícula Actual (Curso más reciente)': int(mat_ultimo_ano) })
    resultados["nuevas_ofertas"] = pd.DataFrame(carreras_nuevas_ofertas).sort_values(['Año Inicio Oferta Detectado', 'Entidad', 'Carrera'])

    carreras_cesadas_ofertas = []
    for (entidad, carrera), group in df.groupby(['entidad', 'carrera']):
        mat_primer_ano_dataset = group[group['Ano_Inicio_Curso'] == primer_ano_datos]['Matricula_Total'].sum()
        mat_ultimo_ano_dataset = group[group['Ano_Inicio_Curso'] == max_year]['Matricula_Total'].sum()
        if mat_primer_ano_dataset > 0 and mat_ultimo_ano_dataset == 0: # Tenía matrícula al inicio, ya no tiene
            # Último año en que SÍ tuvo matrícula
            ultimo_ano_con_matricula = group[group['Matricula_Total'] > 0]['Ano_Inicio_Curso'].max()
            # Si el último año con matrícula es antes del último año del dataset, se considera cesada
            if pd.notna(ultimo_ano_con_matricula) and ultimo_ano_con_matricula < max_year:
                carreras_cesadas_ofertas.append({
                    'Entidad': entidad, 'Carrera': carrera, 
                    'Último Año Oferta Registrada': int(ultimo_ano_con_matricula) })
    resultados["cesadas_ofertas"] = pd.DataFrame(carreras_cesadas_ofertas).sort_values(['Último Año Oferta Registrada', 'Entidad', 'Carrera'], ascending=[False, True, True])
    
    df_reciente = df[df['Ano_Inicio_Curso'] == max_year]
    matricula_baja_reciente = df_reciente[(df_reciente['Matricula_Total'] > 0) & (df_reciente['Matricula_Total'] < umbral_bajo)]\
        .groupby(['entidad', 'carrera'])['Matricula_Total'].sum().astype(int).reset_index()\
        .sort_values('Matricula_Total').rename(columns={'entidad': 'Entidad', 'carrera': 'Carrera', 'Matricula_Total': f'Matrícula {max_year}-{max_year+1}'})
    resultados["baja_matricula"] = matricula_baja_reciente
    resultados["umbral_bajo"] = umbral_bajo
    return resultados, None

# A9: Comparativa de Universidades para Carreras Clave
@st.cache_data
def analisis_A9(df, carreras_a_comparar=None):
    if df.empty: return None, "DataFrame vacío."
    
    if carreras_a_comparar is None or not carreras_a_comparar:
        carreras_clave = df.groupby('carrera')['Matricula_Total'].sum().nlargest(3).index.tolist()
        if not carreras_clave: return None, "No se determinaron carreras clave."
    else:
        carreras_clave = carreras_a_comparar

    df_clave = df[(df['carrera'].isin(carreras_clave)) & (df['Matricula_Total'] > 0)]
    if df_clave.empty: return None, f"No hay datos para: {', '.join(carreras_clave)}."

    if 'Curso_Academico' not in df_clave.columns:
        df_clave['Curso_Academico'] = df_clave['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")

    fig = px.line(df_clave, x='Curso_Academico', y='Matricula_Total', color='entidad',
                  facet_row='carrera', markers=True,
                  title=f'Evolución Histórica por Universidad para: {", ".join(carreras_clave)}',
                  labels={'Matricula_Total': 'Matrícula Total', 'entidad': 'Universidad'})
    fig.update_layout(xaxis_title='Curso Académico', height=min(1200, 350*len(carreras_clave)))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig, None