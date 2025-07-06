import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import streamlit as st
from .general_functions import Translator

import pandas as pd
from typing import Any, Dict, Optional, List, Tuple

def category_order(df: pd.DataFrame, * , y_col: str, color_col: str, top_n: Optional[int] = None) -> List[str]:
    """
    Filtra y ordena las categorías por la suma de valores numéricos en orden descendente.

    Args:
        df (pd.DataFrame): DataFrame con los datos.
        y_col (str): Nombre de la columna con valores numéricos (ej. matrícula total).
        color_col (str): Nombre de la columna de categorías (ej. carreras).
        top_n (Optional[int]): Número máximo de categorías a incluir en el orden. Si es None, se incluirán todas.

    Returns:
        List[str]: Lista ordenada de categorías de mayor a menor según la suma de `y_col`.
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

def calcular_cagr(df_evolucion_total_carrera: pd.DataFrame, ano_inicio_cagr: int, ano_fin_cagr: int) -> dict:
    
    result = {
        "status": "ERROR_UNSPECIFIED",
        "cagr_value": None,
        "start_year": ano_inicio_cagr,
        "end_year": ano_fin_cagr,
        "start_enrollment": None,
        "end_enrollment": None,
        "num_years": None
    }

    if df_evolucion_total_carrera is None or df_evolucion_total_carrera.empty:
        result["status"] = "ERROR_EMPTY_DF"
        return result
        
    anos_disponibles_carrera = sorted(df_evolucion_total_carrera['Ano_Inicio_Curso'].unique())
    
    if len(anos_disponibles_carrera) < 2 or ano_inicio_cagr is None or ano_fin_cagr is None:
        result["status"] = "ERROR_INSUFFICIENT_GLOBAL_DATA"
        return result

    if ano_inicio_cagr >= ano_fin_cagr:
        result["status"] = "ERROR_INVALID_RANGE"
        return result
        
    datos_cagr_periodo = df_evolucion_total_carrera[
        (df_evolucion_total_carrera['Ano_Inicio_Curso'] >= ano_inicio_cagr) &
        (df_evolucion_total_carrera['Ano_Inicio_Curso'] <= ano_fin_cagr)
    ]
    
    period_years = sorted(datos_cagr_periodo['Ano_Inicio_Curso'].unique())
    len_period_years = len(period_years)
    
    if len_period_years < 2:
        result["status"] = "ERROR_INSUFFICIENT_PERIOD_DATA"
        return result
        
    min_period_year = period_years[0]
    max_period_year = period_years[-1]

    matricula_inicio_c = datos_cagr_periodo[datos_cagr_periodo['Ano_Inicio_Curso'] == min_period_year]['Matricula_Total'].sum()
    matricula_fin_c = datos_cagr_periodo[datos_cagr_periodo['Ano_Inicio_Curso'] == max_period_year]['Matricula_Total'].sum()
    
    result.update({
        "start_year": min_period_year,
        "end_year": max_period_year,
        "start_enrollment": matricula_inicio_c,
        "end_enrollment": matricula_fin_c,
        "num_years": len_period_years
    })

    if matricula_inicio_c <= 0:
        result["status"] = "ERROR_ZERO_START_ENROLLMENT"
        return result

    try:
        if len_period_years <= 1:
             result["status"] = "ERROR_INSUFFICIENT_PERIOD_DATA"
             return result

        cagr_val_c = ((matricula_fin_c / matricula_inicio_c)**(1 / (len_period_years - 1)) - 1)
        
        result["status"] = "SUCCESS"
        result["cagr_value"] = cagr_val_c
        
    except (ZeroDivisionError, ValueError):
        result["status"] = "ERROR_CALCULATION"

    return result

#------------------------------------------------------------------------------------------------
@st.cache_data
def analisis_guia_universidades(
    df_instituciones: pd.DataFrame, 
    df_matricula: pd.DataFrame, 
    lang: str,
    provincia_seleccionada: str|None = None, 
    municipio_seleccionado: str|None = None
) -> Tuple[pd.DataFrame | None, str]:
    
    ts = st.session_state.Translator

    if df_instituciones.empty:
        return None, ts.translate('b2_warning_no_data', "Los datos de instituciones ('db_uni.parquet') no están disponibles o están vacíos.")

    ano_mas_reciente_matricula = 0
    df_matricula_ultimo_ano_carreras = pd.DataFrame()
    df_matricula_ultimo_ano_general_uni = pd.DataFrame()

    if not df_matricula.empty and 'Ano_Inicio_Curso' in df_matricula.columns:
        ano_mas_reciente_matricula = int(df_matricula['Ano_Inicio_Curso'].max())
        df_matricula_reciente = df_matricula[df_matricula['Ano_Inicio_Curso'] == ano_mas_reciente_matricula].copy()

        if not df_matricula_reciente.empty:
            df_matricula_ultimo_ano_carreras = df_matricula_reciente[df_matricula_reciente['Matricula_Total'] > 0]\
                .groupby(['entidad', 'rama_ciencias', 'carrera'])['Matricula_Total'].sum().reset_index()\
                .rename(columns={
                    'entidad': 'sigla_institucion',
                    'Matricula_Total': 'Matricula_Carrera_Ultimo_Ano'
                })

            df_matricula_ultimo_ano_general_uni = df_matricula_reciente.groupby('entidad').agg(
                Matricula_Total_Uni_Ultimo_Ano=('Matricula_Total', 'sum'),
                Matricula_Mujeres_Uni_Ultimo_Ano=('Matricula_Mujeres', 'sum'),
                Matricula_Hombres_Uni_Ultimo_Ano=('Matricula_Hombres', 'sum')
            ).reset_index().rename(columns={'entidad': 'sigla_institucion'})

    df_guia = pd.merge(
        df_instituciones,
        df_matricula_ultimo_ano_general_uni,
        on='sigla_institucion',
        how='left'
    )

    if not df_matricula_ultimo_ano_carreras.empty:
        df_guia = pd.merge(
            df_guia,
            df_matricula_ultimo_ano_carreras,
            on='sigla_institucion',
            how='left'
        )
    else:
        df_guia['rama_ciencias'] = None
        df_guia['carrera'] = None
        df_guia['Matricula_Carrera_Ultimo_Ano'] = None

    cols_matricula = [col for col in df_guia.columns if 'Matricula' in col]
    for col in cols_matricula:
        df_guia[col] = df_guia[col].fillna(0).astype(int)

    na_string = ts.translate('_not_available_short', "N/D")
    df_guia['rama_ciencias'] = df_guia['rama_ciencias'].fillna(na_string)
    df_guia['carrera'] = df_guia['carrera'].fillna(na_string)

    df_guia = df_guia.sort_values(
        by=['nombre_institucion', 'rama_ciencias', 'Matricula_Carrera_Ultimo_Ano'],
        ascending=[True, True, False]
    ).reset_index(drop=True)

    if provincia_seleccionada:
        df_guia = df_guia[df_guia['provincia'] == provincia_seleccionada].copy()
    if municipio_seleccionado:
        df_guia = df_guia[df_guia['municipio'] == municipio_seleccionado].copy()

    if df_guia.empty:
        msg = ts.translate('b2_info_no_institutions_filtered_base', "No se encontraron instituciones")
        if provincia_seleccionada:
            msg += " " + ts.translate('b2_info_in_province', "en la provincia de '{province}'").format(province=provincia_seleccionada)
        if municipio_seleccionado:
            msg += " " + ts.translate('b2_info_in_municipality', "en el municipio de '{municipality}'").format(municipality=municipio_seleccionado)
        return pd.DataFrame(), msg + "."

    if ano_mas_reciente_matricula > 0:
        curso_str = f"{ano_mas_reciente_matricula}-{ano_mas_reciente_matricula + 1}"
        msg = ts.translate('b2_success_guide_generated', "Guía generada para el curso {curso}.").format(curso=curso_str)
    else:
        msg = ts.translate('b2_success_guide_generated_no_year', "Guía generada (datos de matrícula del último año no disponibles).")

    return df_guia, msg

@st.cache_data
def analisis_perfil_carrera(df: pd.DataFrame, carrera_seleccionada: str) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, Dict[str, Any] | None, str | None, str | None]:
    # fig_evol_gen, df_evol_para_cagr, df_unis, porc_mujeres, rama, msg
    if df.empty:
        return None, None, None, None, "error_empty_df"
        
    if not carrera_seleccionada:
        return None, None, None, None, "error_no_career_selected"

    df_carrera_completa = df[df['carrera'] == carrera_seleccionada].copy()
    
    if df_carrera_completa.empty:
        return None, None, None, None, "error_no_data_for_career"

    rama_identificada = df_carrera_completa['rama_ciencias'].iloc[0] if not df_carrera_completa.empty else None

    evolucion_genero_carrera = df_carrera_completa.groupby('Ano_Inicio_Curso').agg(
        Matricula_Total=('Matricula_Total', 'sum'),
        Matricula_Mujeres=('Matricula_Mujeres', 'sum'),
        Matricula_Hombres=('Matricula_Hombres', 'sum')
    ).reset_index()

    if 'Curso_Academico' not in evolucion_genero_carrera.columns and not evolucion_genero_carrera.empty:
        evolucion_genero_carrera['Curso_Academico'] = evolucion_genero_carrera['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    ano_mas_reciente_global = int(df['Ano_Inicio_Curso'].max())
    
    df_unis_carrera = df_carrera_completa[df_carrera_completa['Ano_Inicio_Curso'] == ano_mas_reciente_global]\
                        .groupby('entidad')['Matricula_Total'].sum().reset_index()
    
    df_unis_carrera = df_unis_carrera[df_unis_carrera['Matricula_Total'] > 0]\
                        .sort_values(by='Matricula_Total', ascending=False)
                        
    df_unis_carrera = df_unis_carrera.rename(
        columns={
            'entidad': 'Universidad',
            'Matricula_Total': f'Matricula_{ano_mas_reciente_global}-{ano_mas_reciente_global+1}'
        }
    )

    datos_genero_ultimo_ano = None
    if not evolucion_genero_carrera.empty:
        ultimo_ano_data = evolucion_genero_carrera[evolucion_genero_carrera['Ano_Inicio_Curso'] == ano_mas_reciente_global]
        if not ultimo_ano_data.empty:
            datos_genero_ultimo_ano = {
                'Mujeres': ultimo_ano_data['Matricula_Mujeres'].iloc[0],
                'Hombres': ultimo_ano_data['Matricula_Hombres'].iloc[0],
                'Total': ultimo_ano_data['Matricula_Total'].iloc[0]
            }
            
    return evolucion_genero_carrera, df_unis_carrera, datos_genero_ultimo_ano, rama_identificada, "success_profile_generated"

# A1: Evolución Histórica y Proyectada de la Matrícula Nacional
@st.cache_data
def analisis_A1(df: pd.DataFrame, incluir_proyeccion: bool = False) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, str | None, int | None]:
    
    if df.empty:
        return None, None, "error_empty_df", None

    datos_agrupados = df.groupby('Ano_Inicio_Curso').agg(
        Matricula_Total=('Matricula_Total', 'sum'),
        Matricula_Hombres=('Matricula_Hombres', 'sum'),
        Matricula_Mujeres=('Matricula_Mujeres', 'sum')
    ).reset_index()
    
    for col in ['Matricula_Total', 'Matricula_Hombres', 'Matricula_Mujeres']:
        datos_agrupados[col] = datos_agrupados[col].astype(int)

    if datos_agrupados.empty:
        return None, None, "error_no_data_A1", None

    datos_agrupados['Curso_Academico'] = datos_agrupados['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    if not incluir_proyeccion:
        return datos_agrupados, None, "success_historical_only", None

    df_proyeccion = None
    n_puntos_historicos = len(datos_agrupados)
    N_ULTIMOS_ANOS_REGRESION = 6
    
    if n_puntos_historicos < 2:
        return datos_agrupados, None, "error_insufficient_data_for_projection", None
    
    datos_regresion = datos_agrupados.tail(N_ULTIMOS_ANOS_REGRESION) if n_puntos_historicos >= N_ULTIMOS_ANOS_REGRESION else datos_agrupados
    num_anos_regresion = len(datos_regresion)
    
    X_reg = datos_regresion['Ano_Inicio_Curso'].values.reshape(-1, 1)
    y_reg_total = datos_regresion['Matricula_Total'].values
    model_total = LinearRegression().fit(X_reg, y_reg_total)
    
    ultimo_ano_historico_num = datos_agrupados['Ano_Inicio_Curso'].max()
    ultimo_dato_historico = datos_agrupados[datos_agrupados['Ano_Inicio_Curso'] == ultimo_ano_historico_num].iloc[0]
    
    ultima_matricula_total_historica = int(ultimo_dato_historico['Matricula_Total'])
    ultima_matricula_hombres_historica = int(ultimo_dato_historico['Matricula_Hombres'])

    ratio_hombres = 0.5
    if ultima_matricula_total_historica > 0:
        ratio_hombres = ultima_matricula_hombres_historica / ultima_matricula_total_historica

    anos_proyeccion_puros = np.array([ultimo_ano_historico_num + 1, ultimo_ano_historico_num + 2])
    matricula_proyectada_total_pura = model_total.predict(anos_proyeccion_puros.reshape(-1,1)).round(0).astype(int).clip(min=0)
    
    df_proyeccion = pd.DataFrame({
        'Ano_Inicio_Curso': np.concatenate(([ultimo_ano_historico_num], anos_proyeccion_puros)),
        'Matricula_Total': np.concatenate(([ultima_matricula_total_historica], matricula_proyectada_total_pura)).astype(int),
    })
    
    df_proyeccion['Matricula_Hombres'] = (df_proyeccion['Matricula_Total'] * ratio_hombres).round().astype(int)
    df_proyeccion['Matricula_Mujeres'] = df_proyeccion['Matricula_Total'] - df_proyeccion['Matricula_Hombres']
    df_proyeccion['Curso_Academico'] = df_proyeccion['Ano_Inicio_Curso'].apply(lambda x: f"{x}-{x+1}")
    
    return datos_agrupados, df_proyeccion, "success_with_projection", num_anos_regresion

def graficate_A1(
    df_historico: pd.DataFrame, 
    ts: 'Translator',
    df_proyeccion: pd.DataFrame = None, 
    n_anos_reg: int = 0
) -> go.Figure:
    
    incluir_proyeccion = df_proyeccion is not None
    
    df_para_barras = df_historico.copy()
    if incluir_proyeccion:
        df_para_barras = pd.concat([df_historico, df_proyeccion.iloc[1:]], ignore_index=True)

    df_para_barras['Pct_Hombres'] = np.where(df_para_barras['Matricula_Total'] > 0, (df_para_barras['Matricula_Hombres'] / df_para_barras['Matricula_Total']) * 100, 0)
    df_para_barras['Pct_Mujeres'] = np.where(df_para_barras['Matricula_Total'] > 0, (df_para_barras['Matricula_Mujeres'] / df_para_barras['Matricula_Total']) * 100, 0)
    df_para_barras['Texto_Hombres'] = df_para_barras.apply(lambda r: f"{r['Matricula_Hombres']:,}<br>({r['Pct_Hombres']:.1f}%)", axis=1)
    df_para_barras['Texto_Mujeres'] = df_para_barras.apply(lambda r: f"{r['Matricula_Mujeres']:,}<br>({r['Pct_Mujeres']:.1f}%)", axis=1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_para_barras['Curso_Academico'], y=df_para_barras['Matricula_Mujeres'],
        name=ts.translate('_women', 'Mujeres'), marker_color='hotpink',
        text=df_para_barras['Texto_Mujeres'], textposition='outside', textfont=dict(color='white', size=16)
    ))
    fig.add_trace(go.Bar(
        x=df_para_barras['Curso_Academico'], y=df_para_barras['Matricula_Hombres'],
        name=ts.translate('_men', 'Hombres'), marker_color='skyblue',
        text=df_para_barras['Texto_Hombres'], textposition='inside', textfont=dict(color='white', size=16)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_historico['Curso_Academico'], y=df_historico['Matricula_Total'],
        name=ts.translate('_total_enrollment_historical', 'Matrícula Total (Histórica)'),
        mode='lines+markers', line=dict(color='mediumpurple', width=3), marker=dict(size=11, color='mediumpurple')
    ))
    if incluir_proyeccion:
        fig.add_trace(go.Scatter(
            x=df_proyeccion['Curso_Academico'], y=df_proyeccion['Matricula_Total'],
            name=ts.translate('_total_enrollment_projected', 'Matrícula Total (Proyectada)'),
            mode='lines+markers', line=dict(color='royalblue', width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond', color='royalblue')
        ))
    
    title_text = ts.translate('A1_chart_title_historical', 'Matrícula Nacional: Evolución Histórica')
    if incluir_proyeccion:
        title_text = ts.translate(
            'A6_chart_title_projection', "Evolución y Proyección (Reg. Lin. {n_years} últimos años)"
        ).format(n_years=n_anos_reg)
    
    fig.update_layout(
        template='plotly_dark', barmode='stack', title=title_text,
        xaxis_title=ts.translate('_academic_year', 'Curso Académico'),
        yaxis_title=ts.translate('_enrollment', 'Matrícula'),
        legend_title_text=ts.translate('_legend', 'Leyenda'), showlegend=True,
        uniformtext_minsize=8, uniformtext_mode='hide', yaxis=dict(tickformat=","),
        xaxis=dict(type='category')
    )
    
    if incluir_proyeccion and len(df_historico) >= 2:
        fig.add_vline(
            x=len(df_historico) - 0.5, line_width=2, line_dash="dot", line_color="rgba(255,255,0,0.7)",
            annotation_text=ts.translate('_projection_start', "Inicio Proyección"),
            annotation_position="top right", annotation_font_size=15, annotation_font_color="rgba(255,255,0,0.9)"
        )
        
    return fig

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
        text_auto=".2f", #type: ignore
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

# A3: Ranking y Evolución de Carreras por demanda
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

# A4: Analisis de la Brecha de Género
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
    fig2.add_hline(y=50, line_dash="dash", line_color="red", row=1, col=1,annotation_text="50%")#type: ignore
    fig2.add_hline(y=50, line_dash="dash", line_color="red", row=1, col=2,annotation_text="50%")#type: ignore
    return fig1, fig2, None

# A5: Análisis de Concentración y Especialización
@st.cache_data
def analisis_A5(df):
    if df.empty:
        return None, None, None, "DataFrame vacio."
    
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

# A6: Tasas de Crecimiento Anual Compuesto (Cagr)
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