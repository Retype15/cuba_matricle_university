import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import streamlit as st

import pandas as pd
from typing import Optional, List

def category_order(df: pd.DataFrame, * , y_col: str, color_col: str, top_n: Optional[int] = None) -> List[str]:
    """
    Filtra y ordena las categorías por la suma de valores numéricos en orden descendente.

    Parámetros:
    - df (pd.DataFrame): DataFrame con los datos.
    - y_col (str): Nombre de la columna con valores numéricos (ej. matrícula total).
    - color_col (str): Nombre de la columna de categorías (ej. carreras).
    - top_n (Optional[int]): Número máximo de categorías a incluir en el orden. Si es None, se incluirán todas.

    Retorna:
    - List[str]: Lista ordenada de categorías de mayor a menor según la suma de `y_col`.
    """
    orden_categorias = df.groupby(color_col)[y_col].sum().sort_values(ascending=False).index.tolist()
    
    if top_n is not None:
        orden_categorias = orden_categorias[:top_n]
    
    return orden_categorias

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
        return cagr_info

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
                else: cagr_info["valor"] = "Período corto"
            else: cagr_info["valor"] = "Matrícula cero"
        else: cagr_info["valor"] = "Datos insuficientes"
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
        msg = "No se encontraron instituciones"
        if provincia_seleccionada and provincia_seleccionada != "TODAS LAS PROVINCIAS":
            msg += f" en la provincia de '{provincia_seleccionada}'"
        if municipio_seleccionado and municipio_seleccionado != "TODOS LOS MUNICIPIOS":
            msg += f" en el municipio de '{municipio_seleccionado}'"
        msg += "."
        return {}, msg

    ano_mas_reciente_matricula = 0
    df_matricula_ultimo_ano_carreras = pd.DataFrame()
    df_matricula_ultimo_ano_general_uni = pd.DataFrame()

    if not df_matricula.empty:
        ano_mas_reciente_matricula = df_matricula['Ano_Inicio_Curso'].max()
        
        df_matricula_ultimo_ano_carreras = df_matricula[df_matricula['Ano_Inicio_Curso'] == ano_mas_reciente_matricula]\
                                    .groupby(['entidad', 'rama_ciencias', 'carrera'])['Matricula_Total'].sum().reset_index()
        df_matricula_ultimo_ano_carreras = df_matricula_ultimo_ano_carreras[df_matricula_ultimo_ano_carreras['Matricula_Total'] > 0]

        df_matricula_ultimo_ano_general_uni = df_matricula[df_matricula['Ano_Inicio_Curso'] == ano_mas_reciente_matricula]\
                                    .groupby('entidad').agg(
                                        Total_General_Uni=('Matricula_Total', 'sum'),
                                        Total_Mujeres_Uni=('Matricula_Mujeres', 'sum'),
                                        Total_Hombres_Uni=('Matricula_Hombres', 'sum')
                                    ).reset_index()

    guia_data = {}
    columnas_oferta_ramas = [col for col in df_instituciones.columns if col.startswith('oferta_')]
    mapa_oferta_a_rama = { 
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
            "modalidad_estudio": uni_row.get('modalidad_estudio', 'N/D'),
            "datos_genero_uni": {
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
def analisis_perfil_carrera(df, carrera_seleccionada):
    if df.empty:
        # fig_evol_gen, df_evol_para_cagr, df_unis, porc_mujeres, rama, msg
        return None, None, None, None, None, "DataFrame vacío." 
    if not carrera_seleccionada:
        return None, None, None, None, None, "Carrera no seleccionada."

    df_carrera_completa = df[df['carrera'] == carrera_seleccionada]
    if df_carrera_completa.empty:
        return None, None, None, None, None, f"No hay datos para la carrera '{carrera_seleccionada}'."

    rama_identificada = df_carrera_completa['rama_ciencias'].iloc[0] if not df_carrera_completa.empty else "No identificada"

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
            color='Tipo_Matricula_Display',
            title=f"Evolución Histórica Matrícula y Género: {carrera_seleccionada}",
            markers=True,
            labels={'Cantidad': 'Número de Estudiantes', 'Tipo_Matricula_Display': 'Desglose Matrícula'}
        )
        fig_evolucion_genero.update_layout(xaxis_title='Curso Académico', yaxis_title='Número de Estudiantes')

    df_evolucion_para_cagr = evolucion_genero_carrera[['Ano_Inicio_Curso', 'Matricula_Total']].copy()

    ano_mas_reciente_global = df['Ano_Inicio_Curso'].max()
    df_unis_carrera = df_carrera_completa[df_carrera_completa['Ano_Inicio_Curso'] == ano_mas_reciente_global]\
                        .groupby('entidad')['Matricula_Total'].sum().sort_values(ascending=False).reset_index()
    df_unis_carrera = df_unis_carrera[df_unis_carrera['Matricula_Total'] > 0]
    df_unis_carrera.rename(columns={'entidad':'Universidad', 'Matricula_Total':f'Matrícula {ano_mas_reciente_global}-{ano_mas_reciente_global+1}'}, inplace=True)

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

    datos_agrupados = df.groupby('Ano_Inicio_Curso').agg(
        Matricula_Total=('Matricula_Total', 'sum'),
        Matricula_Hombres=('Matricula_Hombres', 'sum'),
        Matricula_Mujeres=('Matricula_Mujeres', 'sum')
    ).reset_index()
    
    for col in ['Matricula_Total', 'Matricula_Hombres', 'Matricula_Mujeres']:
        datos_agrupados[col] = datos_agrupados[col].astype(int)

    if datos_agrupados.empty:
        return None, "No hay datos para el análisis A1."

    datos_agrupados['Tipo'] = 'Histórica'
    datos_agrupados['Curso_Academico'] = datos_agrupados['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    df_para_graficar_barras = datos_agrupados.copy()
    titulo_info = "Evolución Histórica"
    
    ultimo_ano_historico_num = -1
    n_puntos_historicos = len(datos_agrupados)
    df_proyeccion_para_linea = pd.DataFrame()


    if incluir_proyeccion:
        N_ULTIMOS_ANOS_REGRESION = 6
        if n_puntos_historicos < 2:
            return None, "Datos históricos insuficientes para proyección."
        
        if n_puntos_historicos < N_ULTIMOS_ANOS_REGRESION:
            datos_regresion = datos_agrupados
            msg_regresion = f"Usando todos los {len(datos_regresion)} años"
        else:
            datos_regresion = datos_agrupados.tail(N_ULTIMOS_ANOS_REGRESION)
            msg_regresion = f"Basada en {N_ULTIMOS_ANOS_REGRESION} últimos años"

        X_reg = datos_regresion['Ano_Inicio_Curso'].values.reshape(-1, 1)
        y_reg_total = datos_regresion['Matricula_Total'].values
        
        model_total = LinearRegression().fit(X_reg, y_reg_total)
        
        ultimo_ano_historico_num = datos_agrupados['Ano_Inicio_Curso'].max()
        ultimo_dato_historico = datos_agrupados[datos_agrupados['Ano_Inicio_Curso'] == ultimo_ano_historico_num].iloc[0]
        
        ultima_matricula_total_historica = int(ultimo_dato_historico['Matricula_Total'])
        ultima_matricula_hombres_historica = int(ultimo_dato_historico['Matricula_Hombres'])
        ultima_matricula_mujeres_historica = int(ultimo_dato_historico['Matricula_Mujeres'])

        ratio_hombres = 0.0
        ratio_mujeres = 0.0
        if ultima_matricula_total_historica > 0:
            ratio_hombres = ultima_matricula_hombres_historica / ultima_matricula_total_historica
            ratio_mujeres = ultima_matricula_mujeres_historica / ultima_matricula_total_historica
            if abs(ratio_hombres + ratio_mujeres - 1.0) > 1e-9:
                 ratio_mujeres = 1.0 - ratio_hombres
            ratio_hombres = 0.5 
            ratio_mujeres = 0.5

        anos_proyeccion_puros = np.array([ultimo_ano_historico_num + 1, ultimo_ano_historico_num + 2])
        matricula_proyectada_total_pura = model_total.predict(anos_proyeccion_puros.reshape(-1,1)).round(0).astype(int).clip(min=0)
         
        df_proyeccion_para_linea = pd.DataFrame({
            'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_historico_num], anos_proyeccion_puros)),
            'Matricula_Total': np.concatenate(([ultima_matricula_total_historica], matricula_proyectada_total_pura)).astype(int),
            'Tipo': 'Proyectada'
        })
        
        df_proyeccion_para_linea['Matricula_Hombres'] = 0
        df_proyeccion_para_linea['Matricula_Mujeres'] = 0

        df_proyeccion_para_linea.loc[0, 'Matricula_Hombres'] = ultima_matricula_hombres_historica
        df_proyeccion_para_linea.loc[0, 'Matricula_Mujeres'] = ultima_matricula_mujeres_historica
        
        for i in range(1, len(df_proyeccion_para_linea)):
            total_proy = df_proyeccion_para_linea.loc[i, 'Matricula_Total']
            hombres_proy = np.round(total_proy * ratio_hombres).astype(int).clip(min=0)
            mujeres_proy = (total_proy - hombres_proy).astype(int).clip(min=0)
            
            df_proyeccion_para_linea.loc[i, 'Matricula_Hombres'] = hombres_proy
            df_proyeccion_para_linea.loc[i, 'Matricula_Mujeres'] = mujeres_proy
        
        df_proyeccion_para_linea['Curso_Academico'] = df_proyeccion_para_linea['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
        
        df_para_graficar_barras = pd.concat([
            datos_agrupados[datos_agrupados['Ano_Inicio_Curso'] < ultimo_ano_historico_num], 
            df_proyeccion_para_linea
        ], ignore_index=True)
        
        titulo_info = f"Evolución y Proyección (Reg. Lin. {msg_regresion})"

    df_para_graficar_barras['Pct_Hombres'] = df_para_graficar_barras.apply(
        lambda row: (row['Matricula_Hombres'] / row['Matricula_Total'] * 100) if row['Matricula_Total'] > 0 else 0, axis=1
    )
    df_para_graficar_barras['Pct_Mujeres'] = df_para_graficar_barras.apply(
        lambda row: (row['Matricula_Mujeres'] / row['Matricula_Total'] * 100) if row['Matricula_Total'] > 0 else 0, axis=1
    )

    df_para_graficar_barras['Texto_Hombres'] = df_para_graficar_barras.apply(
        lambda row: f"{row['Matricula_Hombres']:,}<br>({row['Pct_Hombres']:.1f}%)" if row['Matricula_Total'] > 0 and row['Matricula_Hombres'] > 0 else f"{row['Matricula_Hombres']:,}", axis=1
    )
    df_para_graficar_barras['Texto_Mujeres'] = df_para_graficar_barras.apply(
        lambda row: f"{row['Matricula_Mujeres']:,}<br>({row['Pct_Mujeres']:.1f}%)" if row['Matricula_Total'] > 0 and row['Matricula_Mujeres'] > 0 else f"{row['Matricula_Mujeres']:,}", axis=1
    )
    
    fig = go.Figure()

    color_mujeres_barra = 'hotpink'
    color_hombres_barra = 'skyblue'
    color_linea_hist = 'mediumpurple'
    color_linea_proy = 'royalblue'

    fig.add_trace(go.Bar(
        x=df_para_graficar_barras['Curso_Academico'],
        y=df_para_graficar_barras['Matricula_Mujeres'],
        name='Mujeres',
        marker_color=color_mujeres_barra,
        marker_line=dict(color='rgba(255,100,155,0.9)', width=2),
        text=df_para_graficar_barras['Texto_Mujeres'],
        textposition='outside',
        textfont=dict(color='white', size=16)
    ))

    fig.add_trace(go.Bar(
        x=df_para_graficar_barras['Curso_Academico'],
        y=df_para_graficar_barras['Matricula_Hombres'],
        name='Hombres',
        marker_color=color_hombres_barra,
        marker_line=dict(color='rgba(200,200,255,0.9)', width=2),
        text=df_para_graficar_barras['Texto_Hombres'],
        textposition='inside',
        textfont=dict(color='white', size=16)
    ))
    
    if incluir_proyeccion:
        fig.add_trace(go.Scatter(
            x=df_proyeccion_para_linea['Curso_Academico'],
            y=df_proyeccion_para_linea['Matricula_Total'],
            name='Matrícula Total (Proyectada)',
            mode='lines+markers',
            line=dict(color=color_linea_proy, width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond', color=color_linea_proy)
        ))
        fig.add_trace(go.Scatter(
            x=datos_agrupados['Curso_Academico'],
            y=datos_agrupados['Matricula_Total'],
            name='Matrícula Total (Histórica)',
            mode='lines+markers',
            line=dict(color=color_linea_hist, width=3),
            marker=dict(size=11, color=color_linea_hist)
        ))
        

    else:
        fig.add_trace(go.Scatter(
            x=datos_agrupados['Curso_Academico'],
            y=datos_agrupados['Matricula_Total'],
            name='Matrícula Total',
            mode='lines+markers',
            line=dict(color=color_linea_hist, width=3),
            marker=dict(size=10, color=color_linea_hist)
        ))

    fig.update_layout(
        template='plotly_dark',
        barmode='stack',
        title=f'Matrícula Nacional: {titulo_info}',
        xaxis_title='Curso Académico',
        yaxis_title='Matrícula',
        legend_title_text='Leyenda',
        showlegend=showlegend,
        uniformtext_minsize=8, 
        uniformtext_mode='hide',
        yaxis=dict(tickformat=","),
        xaxis=dict(type='category')
    )

    if incluir_proyeccion and n_puntos_historicos >= 2 and not df_proyeccion_para_linea.empty:
        x_vline_pos = n_puntos_historicos - 0.5 
        fig.add_vline(
            x=x_vline_pos, 
            line_width=2, 
            line_dash="dot", 
            line_color="rgba(255,255,0,0.7)",
            annotation_text="Inicio Proyección", 
            annotation_position="top right",
            annotation_font_size=15, 
            annotation_font_color="rgba(255,255,0,0.9)"
        )
    
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

    df_proj_concat = pd.DataFrame()
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
            df_proj_concat = pd.concat([df_proj_concat, df_proy_rama_graf], ignore_index=True)
            proyeccion_realizada_alguna_rama = True
            if df_proy_rama_graf['Matricula_Total'].max() > max_y_value_for_annotation:
                max_y_value_for_annotation = df_proy_rama_graf['Matricula_Total'].max()
        titulo_abs = f"Evolución y Proyección por Rama (Reg. Lin. {N_ULTIMOS_ANOS_REGRESION} últimos años o menos)"
    
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
            df_proy_rama_actual = df_proj_concat[df_proj_concat['rama_ciencias'] == rama]
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

    fig_pct = None
    if not rama_evolucion_historica.empty:
        total_anual_hist = rama_evolucion_historica.groupby('Ano_Inicio_Curso')['Matricula_Total'].sum().rename('Total_Anual_Rama')
        if not total_anual_hist.empty:
            rama_evolucion_pct_hist = rama_evolucion_historica.set_index('Ano_Inicio_Curso').join(total_anual_hist).reset_index()
            rama_evolucion_pct_hist['Porcentaje'] = np.where(
                rama_evolucion_pct_hist['Total_Anual_Rama'] > 0,
                (rama_evolucion_pct_hist['Matricula_Total'] / rama_evolucion_pct_hist['Total_Anual_Rama']) * 100, 0 )
            if 'Curso_Academico' not in rama_evolucion_pct_hist.columns:
                rama_evolucion_pct_hist['Curso_Academico'] = rama_evolucion_pct_hist['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
            fig_pct = px.area(rama_evolucion_pct_hist, x='Curso_Academico', y='Porcentaje', color='rama_ciencias',
                        title='Distribución Porcentual Histórica de la Matrícula por Rama de Ciencias',
                        labels={'Porcentaje': '% Matrícula'})
            fig_pct.update_layout(xaxis_title='Curso Académico', yaxis_title='Porcentaje de Matrícula (%)')
    return fig_abs, fig_pct, None


def analisis_A2_correlacion_crecimiento_ramas(df: pd.DataFrame):
    if df.empty:
        return None, None, "DataFrame de entrada vacío para análisis de correlación."
    if not all(col in df.columns for col in ['Ano_Inicio_Curso', 'rama_ciencias', 'Matricula_Total']):
        return None, None, "El DataFrame debe contener 'Ano_Inicio_Curso', 'rama_ciencias', y 'Matricula_Total' para correlación."

    matricula_anual_rama = df.groupby(['Ano_Inicio_Curso', 'rama_ciencias'])['Matricula_Total'].sum().unstack(level='rama_ciencias')
    matricula_anual_rama = matricula_anual_rama.dropna(axis=1, how='all')
    
    columnas_validas_para_pct_change = [col for col in matricula_anual_rama.columns if matricula_anual_rama[col].count() >= 2]
    
    if len(columnas_validas_para_pct_change) < 2:
        return None, None, "No hay suficientes ramas con datos (>1 año) para calcular una matriz de correlación."
        
    matricula_pivot_filtrada = matricula_anual_rama[columnas_validas_para_pct_change]
    cambio_pct_ramas = matricula_pivot_filtrada.pct_change() * 100
    cambio_pct_ramas.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    min_periods_corr = max(2, len(cambio_pct_ramas.dropna(how='all')) // 3) 
    
    df_correlacion = cambio_pct_ramas.corr(min_periods=min_periods_corr)
    df_correlacion = df_correlacion.dropna(axis=0, how='all').dropna(axis=1, how='all')

    if df_correlacion.empty or df_correlacion.shape[0] < 2 or df_correlacion.shape[1] < 2:
        return None, None, "Error al generar una matriz de correlación significativa (datos insuficientes tras el procesamiento)."

    fig = px.imshow(
        df_correlacion,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale='ice_r',
        zmin=-1, zmax=1,
        labels=dict(color="Coef. Correlación"),
        title='Matriz de Correlación del Crecimiento Anual entre Ramas de Ciencias'
    )

    fig.update_layout(
        template='plotly_dark',
        xaxis_title='Rama de Ciencias',
        yaxis_title='Rama de Ciencias',
        height=max(450, 55 * len(df_correlacion.columns)),
        width=max(550, 70 * len(df_correlacion.columns)),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        margin=dict(l=100, r=50, t=80, b=120)
    )
    
    fig.update_xaxes(
        tickangle=45, 
        side="bottom", 
    )
    
    return fig, df_correlacion, None

# A3: Ranking y Evolución de Carreras por Demanda
@st.cache_data
def analisis_A3(df):
    if df.empty:
        return None, None, "DataFrame vacío."
    
    ano_mas_reciente = df['Ano_Inicio_Curso'].max()
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"
    carreras_demanda_reciente = df[df['Ano_Inicio_Curso'] == ano_mas_reciente].groupby('carrera')['Matricula_Total'].sum().sort_values(ascending=False)
    
    if carreras_demanda_reciente.empty:
        return None, None, f"No hay datos de demanda de carreras para {curso_mas_reciente}."

    df_todas_carreras_ranking = carreras_demanda_reciente.reset_index()
    
    top_n_grafico = 10
    carreras_para_grafico = df_todas_carreras_ranking.head(top_n_grafico)['carrera'].tolist()
    
    fig = None
    if carreras_para_grafico:
        evolucion_carreras = df[df['carrera'].isin(carreras_para_grafico)].groupby(['Ano_Inicio_Curso', 'carrera'])['Matricula_Total'].sum().reset_index()
        if not evolucion_carreras.empty:
            evolucion_carreras['Curso_Academico'] = evolucion_carreras['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
            orden_carreras = category_order(df=evolucion_carreras, y_col='Matricula_Total',color_col='carrera')
            fig = px.line(evolucion_carreras, x='Curso_Academico', y='Matricula_Total', color='carrera',
                        title=f'Evolución Histórica de Matrícula (Top {top_n_grafico} Carreras Actuales)',
                        markers=True, labels={'Matricula_Total': 'Matrícula Total'},
                        category_orders={'carrera': orden_carreras})
            fig.update_layout(xaxis_title='Curso Académico', yaxis_title='Matrícula en Carrera')
    
    return fig, df_todas_carreras_ranking, None

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
    genero_carrera_reciente_filtrado = genero_carrera_reciente[genero_carrera_reciente['Total_General'] >= 30].dropna(subset=['Porcentaje_Mujeres'])
    
    top_fem = genero_carrera_reciente_filtrado.sort_values('Porcentaje_Mujeres', ascending=False).head(10)
    top_masc = genero_carrera_reciente_filtrado.sort_values('Porcentaje_Mujeres', ascending=True).head(10)
    
    fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Top 10 Carreras con Mayor % de Mujeres", "Top 10 Carreras con Menor % de Mujeres"))
    if not top_fem.empty:
        fig2.add_trace(go.Bar(x=top_fem['carrera'], y=top_fem['Porcentaje_Mujeres'], name='Mayoría Mujeres'), row=1, col=1)
    if not top_masc.empty:
        fig2.add_trace(go.Bar(x=top_masc['carrera'], y=top_masc['Porcentaje_Mujeres'], name='Minoría Mujeres'), row=1, col=2)
    fig2.update_layout(title_text=f'Desbalance de Género en Carreras ({curso_mas_reciente}, Matrícula >= 30)',
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
    return fig_treemap, df_treemap_data, df_carreras_pocas_unis, None

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
def analisis_A7(df, carreras_seleccionadas=None):
    if df.empty: return None, "DataFrame vacío."
        
    ano_mas_reciente_global = df['Ano_Inicio_Curso'].max()
    if pd.isna(ano_mas_reciente_global): return None, "No se pudo determinar el año más reciente."

    if not carreras_seleccionadas: 
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
            (df_historico_general['Tipo'] == 'Histórica')
        ]
        
        if len(data_carrera_hist) < 2: 
            msg_detalle_proy.append(f"{carrera_nombre} (datos históricos insuficientes para regresión)")
            continue 
        
        datos_reg_carrera = data_carrera_hist.tail(N_ULTIMOS_ANOS_REGRESION) if len(data_carrera_hist) >= N_ULTIMOS_ANOS_REGRESION else data_carrera_hist
        
        X_c = datos_reg_carrera['Ano_Inicio_Curso'].values.reshape(-1, 1)
        y_c = datos_reg_carrera['Matricula_Total'].values
        model_c = LinearRegression().fit(X_c, y_c)
            
        ultimo_ano_hist_c_val = data_carrera_hist['Ano_Inicio_Curso'].max()
        last_hist_enrollment_series = data_carrera_hist[data_carrera_hist['Ano_Inicio_Curso'] == ultimo_ano_hist_c_val]['Matricula_Total']
        if last_hist_enrollment_series.empty:
             msg_detalle_proy.append(f"{carrera_nombre} (no se encontró matrícula para el último año histórico)")
             continue
        last_hist_enrollment = last_hist_enrollment_series.iloc[0]

        anos_proy_c = np.array([ultimo_ano_hist_c_val + 1, ultimo_ano_hist_c_val + 2])
        matricula_proyectada_carrera_final = model_c.predict(anos_proy_c.reshape(-1,1))

        df_proy_carrera_graf = pd.DataFrame({
            'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_hist_c_val], anos_proy_c)),
            'Matricula_Total': np.concatenate(([last_hist_enrollment], matricula_proyectada_carrera_final.round(0).clip(min=0))),
            'carrera': carrera_nombre, 'Tipo': 'Proyectada'})
        df_proy_carrera_graf['Curso_Academico'] = df_proy_carrera_graf['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
        
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
    
    primer_ano_datos = df['Ano_Inicio_Curso'].min()
    max_year = df['Ano_Inicio_Curso'].max()
    resultados = {}
    umbral_bajo = 10 

    carreras_nuevas_ofertas = []
    for (entidad, carrera), group in df.groupby(['entidad', 'carrera']):
        primera_aparicion_ano = group[group['Matricula_Total'] > 0]['Ano_Inicio_Curso'].min()
        mat_ultimo_ano = group[group['Ano_Inicio_Curso'] == max_year]['Matricula_Total'].sum()

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
        if mat_primer_ano_dataset > 0 and mat_ultimo_ano_dataset == 0:
            ultimo_ano_con_matricula = group[group['Matricula_Total'] > 0]['Ano_Inicio_Curso'].max()
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