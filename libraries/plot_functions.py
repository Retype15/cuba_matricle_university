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
        df.rename(columns={'Ano_Inicio_Curso': 'ano_inicio_curso', 'Curso_Academico': 'curso_academico', 'Matricula_Total': 'matricula_total', 'Matricula_Mujeres': 'matricula_mujeres', 'Matricula_Hombres': 'matricula_hombres'}, inplace=True)
        if 'ano_inicio_curso' in df.columns:
            df['ano_inicio_curso'] = pd.to_numeric(df['ano_inicio_curso'], errors='coerce').fillna(0).astype(int)
        if 'curso_academico' not in df.columns and 'ano_inicio_curso' in df.columns:
            df['curso_academico'] = df['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
        for col in ['matricula_total', 'Matricula_Mujeres', 'matricula_mujeres']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df.sort_values(by=['entidad', 'carrera', 'ano_inicio_curso'], inplace=True)
        
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
        
    anos_disponibles_carrera = sorted(df_evolucion_total_carrera['ano_inicio_curso'].unique())
    
    if len(anos_disponibles_carrera) < 2 or ano_inicio_cagr is None or ano_fin_cagr is None:
        result["status"] = "ERROR_INSUFFICIENT_GLOBAL_DATA"
        return result

    if ano_inicio_cagr >= ano_fin_cagr:
        result["status"] = "ERROR_INVALID_RANGE"
        return result
        
    datos_cagr_periodo = df_evolucion_total_carrera[
        (df_evolucion_total_carrera['ano_inicio_curso'] >= ano_inicio_cagr) &
        (df_evolucion_total_carrera['ano_inicio_curso'] <= ano_fin_cagr)
    ]
    
    period_years = sorted(datos_cagr_periodo['ano_inicio_curso'].unique())
    len_period_years = len(period_years)
    
    if len_period_years < 2:
        result["status"] = "ERROR_INSUFFICIENT_PERIOD_DATA"
        return result
        
    min_period_year = period_years[0]
    max_period_year = period_years[-1]

    matricula_inicio_c = datos_cagr_periodo[datos_cagr_periodo['ano_inicio_curso'] == min_period_year]['matricula_total'].sum()
    matricula_fin_c = datos_cagr_periodo[datos_cagr_periodo['ano_inicio_curso'] == max_period_year]['matricula_total'].sum()
    
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

def grouped_dot_plot(
    df: pd.DataFrame,
    /,
    x: str,
    y: str,
    *,
    title: str|None=None,
    yaxis_title: str|None =None,
    annotation_text: str='elements',
    color_scale: str = 'Viridis_r',
    marker_symbol: str = 'circle-open',
    **kwargs
) -> go.Figure:
    """ Info: Docstring generado por IA, no es culpa mia si es impreciso.
    Genera un gráfico de puntos agrupados (dot plot) interactivo y personalizable.

    Este gráfico visualiza la distribución de elementos por categorías numéricas o discretas.
    Cada punto representa una entrada en el DataFrame, agrupada por la columna `x` en el eje Y
    y distribuida horizontalmente (`x_pos`) para evitar superposiciones, lo que permite visualizar
    la cantidad de elementos en cada nivel de agrupación.

    Args:
        df (pd.DataFrame): DataFrame de entrada que contiene los datos a graficar.
                           Debe contener las columnas especificadas por `x` y `y`.
        x (str): Nombre de la columna en `df` que se usará para definir las categorías
                 del eje Y y para agrupar los puntos. Los valores de esta columna también
                 se usarán para colorear los puntos.
        y (str): Nombre de la columna en `df` que contiene la etiqueta textual principal
                 para cada punto. Esta etiqueta se mostrará de forma destacada al pasar
                 el cursor sobre el punto (`hover_name`).
        title (str, optional): Título principal del gráfico. Por defecto es una cadena vacía.
        yaxis_title (str, optional): Etiqueta para el eje Y. Por defecto es una cadena vacía.
        annotation_text (str, optional): Texto descriptivo para las anotaciones que
                                         indican la cantidad de elementos por grupo (ej. 'carreras').
                                         Se concatenará con el conteo numérico. Por defecto es una cadena vacía.
        color_scale (str, optional): Nombre de la escala de colores secuencial de Plotly
                                     (ej. 'Viridis_r', 'thermal_r'). Por defecto es 'Viridis_r'.
        marker_symbol (str, optional): Símbolo de los marcadores de los puntos (ej. 'circle',
                                       'circle-open', 'square'). Por defecto es 'circle-open'. reference: https://plotly.com/python/marker-style/#custom-marker-symbols

    Returns:
        go.Figure: Objeto de figura de Plotly (`plotly.graph_objects.Figure`) que representa
                   el gráfico de puntos agrupados. Retorna una figura vacía si el DataFrame
                   está vacío o las columnas requeridas no existen.

    """
    if df.empty or x not in df.columns or y not in df.columns:
        return go.Figure()

    df_plot = df.sort_values(by=[x, y]).copy()
    df_plot['group_index'] = df_plot.groupby(x).cumcount()
    
    counts = df_plot[x].value_counts().sort_index()
    
    fig = px.scatter(
        df_plot,
        x='group_index',
        y=x,
        hover_name=y,
        hover_data={x: False, 'group_index': False}, 
        color=x,
        color_continuous_scale=color_scale,
        title=title,
        labels={
            x: yaxis_title
        },
        **kwargs
    )

    fig.update_traces(
        marker=dict(size=12, symbol=marker_symbol, line=dict(width=1, color='DarkSlateGrey')),
        mode='markers'
    )
    
    fig.update_layout(
        height=max(400, len(counts) * 45 + 70), 
        showlegend=False,
        coloraxis_showscale=False,
        template='plotly_dark',
        xaxis=dict(
            title='',
            showticklabels=False,
            zeroline=False,
            showgrid=False
        ),
        yaxis=dict(
            type='category',
            title_standoff=15,
            showgrid=False, 
        ),
        hoverlabel=dict(
            bgcolor="black",
            font_size=14,
        )
    )

    for i, ( _, count) in enumerate(counts.items()):
        fig.add_annotation(
            x=count,
            y=i,
            text=f"<b>{count}</b> {annotation_text}",
            showarrow=False,
            font=dict(size=11, color="white"),
            bgcolor="rgba(40, 40, 40, 0.7)",
            xanchor='left',
            yanchor='middle',
            xshift=5
        )
        
    return fig

#------------------------------------------------------------------------------------------------

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

    evolucion_genero_carrera = df_carrera_completa.groupby('ano_inicio_curso').agg(
        matricula_total=('matricula_total', 'sum'),
        matricula_mujeres=('matricula_mujeres', 'sum'),
        matricula_hombres=('matricula_hombres', 'sum')
    ).reset_index()

    if 'curso_academico' not in evolucion_genero_carrera.columns and not evolucion_genero_carrera.empty:
        evolucion_genero_carrera['curso_academico'] = evolucion_genero_carrera['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
    
    ano_mas_reciente_global = int(df['ano_inicio_curso'].max())
    
    df_unis_carrera = df_carrera_completa[df_carrera_completa['ano_inicio_curso'] == ano_mas_reciente_global]\
                        .groupby('entidad')['matricula_total'].sum().reset_index()
    
    df_unis_carrera = df_unis_carrera[df_unis_carrera['matricula_total'] > 0]\
                        .sort_values(by='matricula_total', ascending=False)
                        
    df_unis_carrera = df_unis_carrera.rename(
        columns={
            'entidad': 'Universidad',
            'matricula_total': f'Matricula_{ano_mas_reciente_global}-{ano_mas_reciente_global+1}'
        }
    )

    datos_genero_ultimo_ano = None
    if not evolucion_genero_carrera.empty:
        ultimo_ano_data = evolucion_genero_carrera[evolucion_genero_carrera['ano_inicio_curso'] == ano_mas_reciente_global]
        if not ultimo_ano_data.empty:
            datos_genero_ultimo_ano = {
                'Mujeres': ultimo_ano_data['matricula_mujeres'].iloc[0],
                'Hombres': ultimo_ano_data['matricula_hombres'].iloc[0],
                'Total': ultimo_ano_data['matricula_total'].iloc[0]
            }
            
    return evolucion_genero_carrera, df_unis_carrera, datos_genero_ultimo_ano, rama_identificada, "success_profile_generated"

# A1: Evolución Histórica y Proyectada de la Matrícula Nacional
@st.cache_data
def analisis_A1(df: pd.DataFrame, projection: bool = False) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, str | None, int | None]:
    
    if df.empty:
        return None, None, "error_empty_df", None

    datos_agrupados = df.groupby('ano_inicio_curso').agg(
        matricula_total=('matricula_total', 'sum'),
        matricula_hombres=('matricula_hombres', 'sum'),
        matricula_mujeres=('matricula_mujeres', 'sum')
    ).reset_index()
    
    for col in ['matricula_total', 'matricula_hombres', 'matricula_mujeres']:
        datos_agrupados[col] = datos_agrupados[col].astype(int)

    if datos_agrupados.empty:
        return None, None, "error_no_data_A1", None

    datos_agrupados['curso_academico'] = datos_agrupados['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
    
    if not projection:
        return datos_agrupados, None, "success_historical_only", None

    df_proyeccion = None
    n_puntos_historicos = len(datos_agrupados)
    N_ULTIMOS_ANOS_REGRESION = 6
    
    if n_puntos_historicos < 2:
        return datos_agrupados, None, "error_insufficient_data_for_projection", None
    
    datos_regresion = datos_agrupados.tail(N_ULTIMOS_ANOS_REGRESION) if n_puntos_historicos >= N_ULTIMOS_ANOS_REGRESION else datos_agrupados
    num_anos_regresion = len(datos_regresion)
    
    X_reg = datos_regresion['ano_inicio_curso'].values.reshape(-1, 1)#type:ignore
    y_reg_total = datos_regresion['matricula_total'].values
    model_total = LinearRegression().fit(X_reg, y_reg_total) #type:ignore
    
    ultimo_ano_historico_num = datos_agrupados['ano_inicio_curso'].max()
    ultimo_dato_historico = datos_agrupados[datos_agrupados['ano_inicio_curso'] == ultimo_ano_historico_num].iloc[0]
    
    ultima_matricula_total_historica = int(ultimo_dato_historico['matricula_total'])
    ultima_matricula_hombres_historica = int(ultimo_dato_historico['matricula_hombres'])

    ratio_hombres = 0.5
    if ultima_matricula_total_historica > 0:
        ratio_hombres = ultima_matricula_hombres_historica / ultima_matricula_total_historica

    anos_proyeccion_puros = np.array([ultimo_ano_historico_num + 1, ultimo_ano_historico_num + 2])
    matricula_proyectada_total_pura = model_total.predict(anos_proyeccion_puros.reshape(-1,1)).round(0).astype(int).clip(min=0)
    
    df_proyeccion = pd.DataFrame({
        'ano_inicio_curso': np.concatenate(([ultimo_ano_historico_num], anos_proyeccion_puros)),
        'matricula_total': np.concatenate(([ultima_matricula_total_historica], matricula_proyectada_total_pura)).astype(int),
    })
    
    df_proyeccion['matricula_hombres'] = (df_proyeccion['matricula_total'] * ratio_hombres).round().astype(int)
    df_proyeccion['matricula_mujeres'] = df_proyeccion['matricula_total'] - df_proyeccion['matricula_hombres']
    df_proyeccion['curso_academico'] = df_proyeccion['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
    
    return datos_agrupados, df_proyeccion, "success_with_projection", num_anos_regresion

def graficate_A1(
    df_historico: pd.DataFrame, 
    ts: 'Translator',
    df_proyeccion: pd.DataFrame | None = None, 
    n_anos_reg: int = 0
) -> go.Figure:
    
    incluir_proyeccion = df_proyeccion is not None and not df_proyeccion.empty
    
    df_barras = df_historico.copy()
    if incluir_proyeccion:
        df_barras = pd.concat([df_historico, df_proyeccion[~df_proyeccion['curso_academico'].isin(df_historico['curso_academico'])]], ignore_index=True) #type:ignore

    df_barras['Pct_Hombres'] = np.where(df_barras['matricula_total'] > 0, (df_barras['matricula_hombres'] / df_barras['matricula_total']) * 100, 0)
    df_barras['Pct_Mujeres'] = np.where(df_barras['matricula_total'] > 0, (df_barras['matricula_mujeres'] / df_barras['matricula_total']) * 100, 0)
    df_barras['Texto_Hombres'] = df_barras.apply(lambda r: f"{r['matricula_hombres']:,}<br>({r['Pct_Hombres']:.1f}%)", axis=1)
    df_barras['Texto_Mujeres'] = df_barras.apply(lambda r: f"{r['matricula_mujeres']:,}<br>({r['Pct_Mujeres']:.1f}%)", axis=1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_barras['curso_academico'], y=df_barras['matricula_mujeres'],
        name=ts.translate('_women', 'Mujeres'), marker_color='hotpink', opacity=0.7,
        text=df_barras['Texto_Mujeres'], textposition='auto', textfont_size=12
    ))
    fig.add_trace(go.Bar(
        x=df_barras['curso_academico'], y=df_barras['matricula_hombres'],
        name=ts.translate('_men', 'Hombres'), marker_color='skyblue', opacity=0.7,
        text=df_barras['Texto_Hombres'], textposition='auto', textfont_size=12
    ))

    if incluir_proyeccion:
        fig.add_trace(go.Scatter(
            x=df_proyeccion['curso_academico'], y=df_proyeccion['matricula_total'], #type:ignore
            name=ts.translate('_total_enrollment_projected', 'Matrícula Total (Proyectada)'),
            mode='lines+markers', line=dict(color='royalblue', width=4, dash='dash'),
            marker=dict(size=10, symbol='diamond', color='royalblue', line=dict(width=2, color='white'))
        ))
    
    if incluir_proyeccion and len(df_historico) >= 2:
        fig.add_vline(
            x=len(df_historico['curso_academico'].unique()) - 0.5, line_width=3, line_dash="dot", line_color="rgba(255,255,0,0.7)",
            annotation_text=ts.translate('_projection_start', "Inicio Proyección"),
            annotation_position="top right", annotation_font_size=15, annotation_font_color="rgba(255,255,0,0.9)"
        )
    
    
    fig.add_trace(go.Scatter(
        x=df_historico['curso_academico'], y=df_historico['matricula_total'],
        name=ts.translate('_total_enrollment_historical', 'Matrícula Total (Histórica)'),
        mode='lines+markers', line=dict(color='mediumpurple', width=4), marker=dict(size=12, color='mediumpurple', line=dict(width=2, color='white'))
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
        uniformtext_minsize=10, uniformtext_mode='hide', yaxis=dict(tickformat=","),
        xaxis=dict(type='category')
    )
        
    return fig

# A2: Distribución y Evolución de la Matrícula por Rama de Ciencias

@st.cache_data
def analisis_A2(df: pd.DataFrame, projection: bool = False) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, str | None, int | None]:
    if df.empty:
        return None, None, "error_empty_df", None
    
    rama_evolucion_historica = df.groupby(['ano_inicio_curso', 'rama_ciencias'])['matricula_total'].sum().reset_index()
    if rama_evolucion_historica.empty:
        return None, None, "error_no_historical_data", None
        
    rama_evolucion_historica['curso_academico'] = rama_evolucion_historica['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")

    total_anual_hist = rama_evolucion_historica.groupby('ano_inicio_curso')['matricula_total'].sum().rename('Total_Anual_Rama')
    rama_evolucion_pct = rama_evolucion_historica.merge(total_anual_hist, on='ano_inicio_curso')
    rama_evolucion_pct['Porcentaje'] = np.where(
        rama_evolucion_pct['Total_Anual_Rama'] > 0,
        (rama_evolucion_pct['matricula_total'] / rama_evolucion_pct['Total_Anual_Rama']) * 100, 0
    )

    df_proj_concat = None
    num_anos_regresion = 0
    if projection:
        df_proj_concat = pd.DataFrame()
        ramas_unicas = rama_evolucion_historica['rama_ciencias'].unique()
        N_ULTIMOS_ANOS_REGRESION = 6
        num_anos_regresion = N_ULTIMOS_ANOS_REGRESION

        for rama in ramas_unicas:
            data_rama_hist = rama_evolucion_historica[rama_evolucion_historica['rama_ciencias'] == rama]
            if len(data_rama_hist) < 2: continue
            
            datos_regresion_rama = data_rama_hist.tail(N_ULTIMOS_ANOS_REGRESION) if len(data_rama_hist) >= N_ULTIMOS_ANOS_REGRESION else data_rama_hist
            X_reg_rama = datos_regresion_rama['ano_inicio_curso'].values.reshape(-1, 1)
            y_reg_rama = datos_regresion_rama['matricula_total'].values
            model_rama = LinearRegression().fit(X_reg_rama, y_reg_rama)
            
            ultimo_ano_hist_rama = data_rama_hist['ano_inicio_curso'].max()
            ultima_mat_hist_rama = data_rama_hist[data_rama_hist['ano_inicio_curso'] == ultimo_ano_hist_rama]['matricula_total'].iloc[0]
            anos_proy_puros_rama = np.array([ultimo_ano_hist_rama + 1, ultimo_ano_hist_rama + 2])
            mat_proy_pura_rama = model_rama.predict(anos_proy_puros_rama.reshape(-1,1))

            df_proy_rama_graf = pd.DataFrame({
                'ano_inicio_curso': np.concatenate(([ultimo_ano_hist_rama], anos_proy_puros_rama)),
                'matricula_total': np.concatenate(([ultima_mat_hist_rama], mat_proy_pura_rama.round(0).clip(min=0))),
                'rama_ciencias': rama
            })
            df_proy_rama_graf['curso_academico'] = df_proy_rama_graf['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
            df_proj_concat = pd.concat([df_proj_concat, df_proy_rama_graf], ignore_index=True)
            
    return rama_evolucion_historica, rama_evolucion_pct, df_proj_concat, num_anos_regresion #type:ignore

def graficate_A2_evolucion(df_historico: pd.DataFrame, ts: 'Translator', df_proyeccion: pd.DataFrame = None, n_anos_reg: int = 0) -> go.Figure:#type:ignore
    fig = go.Figure()
    ramas_unicas = df_historico['rama_ciencias'].unique()
    colores_plotly = px.colors.qualitative.Plotly
    incluir_proyeccion = df_proyeccion is not None
    
    for i, rama in enumerate(ramas_unicas):
        color_actual = colores_plotly[i % len(colores_plotly)]
        df_hist_rama_actual = df_historico[df_historico['rama_ciencias'] == rama]
        if not df_hist_rama_actual.empty:
            fig.add_trace(go.Scatter(
                x=df_hist_rama_actual['curso_academico'], y=df_hist_rama_actual['matricula_total'],
                mode='lines+markers', name=rama, legendgroup=rama,
                line=dict(color=color_actual, dash='solid'), showlegend=True
            ))
        if incluir_proyeccion:
            df_proy_rama_actual = df_proyeccion[df_proyeccion['rama_ciencias'] == rama]
            if not df_proy_rama_actual.empty:
                fig.add_trace(go.Scatter(
                    x=df_proy_rama_actual['curso_academico'], y=df_proy_rama_actual['matricula_total'],
                    mode='lines+markers', name=f"{rama} ({ts.translate('_projected_short', 'Proy.')})", legendgroup=rama,
                    line=dict(color=color_actual, dash='dash'), showlegend=False
                ))
    
    title = ts.translate('A2_chart_title_evolution', "Evolución Histórica por Rama")
    if incluir_proyeccion:
        title = ts.translate('A6_chart_title_branches_projection', "Evolución y Proyección por Rama (Reg. Lin. {n_years} últimos años o menos)").format(n_years=n_anos_reg)

    fig.update_layout(
        title=title,
        xaxis_title=ts.translate('_academic_year', 'Curso Académico'),
        yaxis_title=ts.translate('A2_yaxis_title_enrollment_branch', 'Matrícula en Rama de Ciencias'),
        legend_title_text=ts.translate('A2_legend_title_branch', 'Rama de Ciencias')
    )
    
    if incluir_proyeccion and not df_historico.empty:
        x_vline_pos = len(df_historico['curso_academico'].unique()) - 0.5
        fig.add_vline(x=x_vline_pos, line_width=2, line_dash="dot", line_color="grey",
                      annotation_text=ts.translate('_projection_start', "Inicio Proyección"),
                      annotation_position="top right",
                      annotation_font_size=10, annotation_font_color="grey")
    return fig

def graficate_A2_distribucion(df_distribucion_pct: pd.DataFrame, ts: 'Translator') -> go.Figure:
    fig = px.area(
        df_distribucion_pct,
        x='curso_academico',
        y='Porcentaje',
        color='rama_ciencias',
        title=ts.translate('A2_chart_title_distribution', 'Distribución Porcentual Histórica de la Matrícula por Rama de Ciencias'),
        labels={
            'Porcentaje': ts.translate('A2_yaxis_label_percentage', '% Matrícula'),
            'curso_academico': ts.translate('_academic_year', 'Curso Académico'),
            'rama_ciencias': ts.translate('A2_legend_title_branch', 'Rama de Ciencias')
        }
    )
    return fig

def graficate_A2_correlacion(df: pd.DataFrame, ts: 'Translator') -> Tuple[go.Figure | None, pd.DataFrame | None, str | None]:
    if df.empty or not all(c in df.columns for c in ['ano_inicio_curso', 'rama_ciencias', 'matricula_total']):
        return None, None, "error_insufficient_columns"

    matricula_anual_rama = df.groupby(['ano_inicio_curso', 'rama_ciencias'])['matricula_total'].sum().unstack(level='rama_ciencias').dropna(axis=1, how='all')
    valid_cols = [col for col in matricula_anual_rama.columns if matricula_anual_rama[col].count() >= 2]
    
    if len(valid_cols) < 2:
        return None, None, "error_insufficient_branches"
        
    cambio_pct_ramas = matricula_anual_rama[valid_cols].pct_change() * 100
    cambio_pct_ramas.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    min_periods = max(2, len(cambio_pct_ramas.dropna(how='all')) // 3)
    df_correlacion = cambio_pct_ramas.corr(min_periods=min_periods).dropna(axis=0, how='all').dropna(axis=1, how='all')

    if df_correlacion.empty or df_correlacion.shape[0] < 2:
        return None, None, "error_correlation_matrix"

    fig = px.imshow(
        df_correlacion, text_auto=".2f", aspect="auto", #type:ignore
        color_continuous_scale='ice_r', zmin=-1, zmax=1,
        labels=dict(color=ts.translate('A2_corr_legend', "Coef. Correlación")),
        title=ts.translate('A2_corr_title', 'Matriz de Correlación del Crecimiento Anual entre Ramas de Ciencias')
    )
    fig.update_layout(
        template='plotly_dark',
        xaxis_title=ts.translate('A2_legend_title_branch', 'Rama de Ciencias'),
        yaxis_title=ts.translate('A2_legend_title_branch', 'Rama de Ciencias'),
        height=max(450, 55 * len(df_correlacion.columns)),
        width=max(550, 70 * len(df_correlacion.columns)),
        xaxis_showgrid=False, yaxis_showgrid=False,
        margin=dict(l=100, r=50, t=80, b=120)
    )
    fig.update_xaxes(tickangle=45, side="bottom")
    
    return fig, df_correlacion, "success"

# A3: Ranking y Evolución de Carreras por demanda

@st.cache_data
def analisis_A3(df: pd.DataFrame, top_n: int = 10) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, str | None, str | None]:
    if df.empty:
        return None, None, None, "error_empty_df"
    
    ano_mas_reciente = int(df['ano_inicio_curso'].max())
    curso_reciente_str = f"{ano_mas_reciente}-{ano_mas_reciente+1}"
    
    df_reciente = df[df['ano_inicio_curso'] == ano_mas_reciente]
    if df_reciente.empty:
        return None, None, curso_reciente_str, "error_no_data_for_year"

    df_ranking_reciente = df_reciente.groupby('carrera')['matricula_total'].sum().sort_values(ascending=False).reset_index()
    
    if df_ranking_reciente.empty:
        return None, None, curso_reciente_str, "error_no_ranking_data"

    carreras_top_list = df_ranking_reciente.head(top_n)['carrera'].tolist()
    
    df_evolucion_top = df[df['carrera'].isin(carreras_top_list)].groupby(['ano_inicio_curso', 'carrera'])['matricula_total'].sum().reset_index()
    
    if df_evolucion_top.empty:
        return df_ranking_reciente, None, curso_reciente_str, "error_no_evolution_data"

    df_evolucion_top['curso_academico'] = df_evolucion_top['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")

    return df_ranking_reciente, df_evolucion_top, curso_reciente_str, "success"

def graficate_A3_evolucion(df_evolucion: pd.DataFrame, ts: 'Translator', top_n: int) -> go.Figure:
    
    orden_carreras = category_order(df=df_evolucion, y_col='matricula_total', color_col='carrera')
    
    fig = px.line(
        df_evolucion, 
        x='curso_academico', 
        y='matricula_total', 
        color='carrera',
        title=ts.translate('A3_chart_title_evolution', "Evolución Histórica (Top {n} Carreras Actuales)").format(n=top_n),
        markers=True, 
        labels={
            'matricula_total': ts.translate('A3_chart_yaxis_enrollment', 'Matrícula Total en Carrera'),
            'curso_academico': ts.translate('_academic_year', 'Curso Académico'),
            'carrera': ts.translate('_career', 'Carrera')
        },
        category_orders={'carrera': orden_carreras}
    )
    fig.update_layout(template='plotly_dark')
    return fig

@st.cache_data
def analisis_A3_cagr(df: pd.DataFrame) -> Tuple[pd.DataFrame | None, str | None, str]:
    """
    Calcula la Tasa de Crecimiento Anual Compuesto (CAGR) para todas las carreras.
    Retorna un DataFrame con los resultados y el período analizado.
    """
    if df.empty or df['ano_inicio_curso'].nunique() < 2:
        return None, None, "error_insufficient_data"
    
    cagr_data = []
    min_year = int(df['ano_inicio_curso'].min())
    max_year = int(df['ano_inicio_curso'].max())

    matricula = df.groupby(['carrera', 'ano_inicio_curso'])['matricula_total'].sum().unstack()

    for carrera, row in matricula.iterrows():
        anos = row.dropna().index
        if len(anos) < 2:
            continue

        ano_inicio = anos.min()
        ano_fin = anos.max()
        n_anos_periodo = ano_fin - ano_inicio
        
        if n_anos_periodo >= 1:
            matr_primero = row.loc[ano_inicio]
            matr_ultimo = row.loc[ano_fin]

            if matr_primero > 0 and matr_ultimo > 0:
                cagr_val = ((matr_ultimo / matr_primero)**(1 / n_anos_periodo) - 1) * 100
                cagr_data.append({
                    'carrera': carrera, 
                    'CAGR': cagr_val, 
                    'Matricula_Inicio': matr_primero, 
                    'Matricula_Fin': matr_ultimo,
                    'Periodo_Anos': n_anos_periodo
                })
    
    if not cagr_data: 
        return None, None, "error_no_cagr_calculated"
    
    df_cagr = pd.DataFrame(cagr_data).sort_values('CAGR', ascending=False).dropna()
    if df_cagr.empty: 
        return None, None, "error_no_valid_cagr"

    periodo_str = f"({min_year}-{max_year})"
    
    return df_cagr, periodo_str, "success"

def graficate_A3_cagr(df_cagr: pd.DataFrame, periodo: str, ts: 'Translator') -> Tuple[go.Figure, go.Figure]:

    # Menor Crecimiento
    fig_top_cagr = px.bar(
        df_cagr.head(15), 
        x='carrera', 
        y='CAGR',
        title=ts.translate('A3_chart_title_cagr_top', "Top 15 por Mayor Crecimiento Promedio Anual {periodo}").format(periodo=periodo),
        labels={'carrera': ts.translate('_career', 'Carrera'), 'CAGR': 'CAGR (%)'},
        template='plotly_dark'
    )
    fig_top_cagr.update_traces(marker_color='#3D9970')

    # Mayor crecimiento
    fig_bottom_cagr = px.bar(
        df_cagr.tail(15).sort_values('CAGR', ascending=True), 
        x='carrera', 
        y='CAGR', 
        title=ts.translate('A3_chart_title_cagr_bottom', "Top 15 por Mayor Decrecimiento Promedio Anual {periodo}").format(periodo=periodo),
        labels={'carrera': ts.translate('_career', 'Carrera'), 'CAGR': 'CAGR (%)'},
        template='plotly_dark'
    )
    fig_bottom_cagr.update_traces(marker_color='#FF4136')

    return fig_top_cagr, fig_bottom_cagr

# A4: Analisis de la Brecha de Genero
@st.cache_data
def analisis_A4(df: pd.DataFrame, min_enrollment_for_career: int = 30) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None, str | None, str]:
    if df.empty:
        return None, None, None, None, "error_empty_df"

    df_genero = df.copy()
    df_genero['Porcentaje_Mujeres'] = np.where(
        df_genero['matricula_total'] > 0,
        (df_genero['matricula_mujeres'] / df_genero['matricula_total']) * 100, np.nan
    )

    ano_mas_reciente = int(df_genero['ano_inicio_curso'].max())
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"

    df_reciente = df_genero[df_genero['ano_inicio_curso'] == ano_mas_reciente]
    if df_reciente.empty:
        return None, None, None, curso_mas_reciente, "error_no_data_for_year"

    genero_rama_reciente = df_reciente.groupby('rama_ciencias').agg(
        Total_Mujeres=('matricula_mujeres', 'sum'),
        Total_Hombres=('matricula_hombres', 'sum'),
        Total_General=('matricula_total', 'sum')
    ).reset_index()
    genero_rama_reciente['Porcentaje_Mujeres'] = np.where(
        genero_rama_reciente['Total_General'] > 0,
        (genero_rama_reciente['Total_Mujeres'] / genero_rama_reciente['Total_General']) * 100, np.nan
    )
    df_genero_ramas = genero_rama_reciente.dropna(subset=['Porcentaje_Mujeres'])

    genero_carrera_reciente = df_reciente.groupby('carrera').agg(
        Total_Mujeres=('matricula_mujeres', 'sum'),
        Total_Hombres=('matricula_hombres', 'sum'),
        Total_General=('matricula_total', 'sum')
    ).reset_index()
    genero_carrera_reciente['Porcentaje_Mujeres'] = np.where(
        genero_carrera_reciente['Total_General'] > 0,
        (genero_carrera_reciente['Total_Mujeres'] / genero_carrera_reciente['Total_General']) * 100, np.nan
    )
    
    carreras_filtrado = genero_carrera_reciente[
        genero_carrera_reciente['Total_General'] >= min_enrollment_for_career
    ].dropna(subset=['Porcentaje_Mujeres'])

    df_top_fem = carreras_filtrado.sort_values('Porcentaje_Mujeres', ascending=False).head(10)
    df_top_masc = carreras_filtrado.sort_values('Porcentaje_Mujeres', ascending=True).head(10)

    return df_genero_ramas, df_top_fem, df_top_masc, curso_mas_reciente, "success"

def graficate_A4_ramas(df_ramas: pd.DataFrame, ts: 'Translator', curso_reciente: str) -> go.Figure:
    df_sorted = df_ramas.sort_values('Porcentaje_Mujeres', ascending=True)
    
    fig = px.bar(
        df_sorted,
        x='Porcentaje_Mujeres', 
        y='rama_ciencias', 
        orientation='h',
        title=ts.translate('A4_chart_title_branches', 'Porcentaje de Mujeres por Rama de Ciencias ({curso})').format(curso=curso_reciente),
        labels={
            'Porcentaje_Mujeres': ts.translate('A4_chart_yaxis_women_pct', '% Mujeres'),
            'rama_ciencias': ts.translate('A2_legend_title_branch', 'Rama de Ciencias')
        },
        color='Porcentaje_Mujeres',
        color_continuous_scale='Plasma',
        range_color=[df_sorted['Porcentaje_Mujeres'].min() - 5, 100],
        template='plotly_dark',
        text='Porcentaje_Mujeres'
    )
    
    fig.update_traces(
        texttemplate='%{x:.1f}%', 
        textposition='outside',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5, 
        opacity=0.8
    )
    
    fig.add_vline(
        x=50, 
        line_width=3, 
        line_dash="dash", 
        line_color="red",
        annotation_text=ts.translate('_50_parity', "50% Paridad"),
        annotation_position="bottom right",
        annotation_font_size=16,
        annotation_font_color="red"
    )
    
    fig.update_layout(
        yaxis_title=None,
        xaxis_range=[0, 105],
        coloraxis_showscale=False,
        height=450
    )
    return fig

def graficate_A4_carreras(df_fem: pd.DataFrame, df_masc: pd.DataFrame, ts: 'Translator', curso_reciente: str) -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=False
    )

    # Mayoría
    if not df_fem.empty:
        fig.add_trace(go.Bar(
            y=df_fem['carrera'], 
            x=df_fem['Porcentaje_Mujeres'], 
            name=ts.translate('A4_legend_major_women', 'Mayoría Mujeres'),
            orientation='h',
            marker_color='#E040FB',
            text=df_fem['Porcentaje_Mujeres'].apply(lambda x: f'{x:.1f}%')
        ), row=1, col=1)

    # Minoría
    if not df_masc.empty:
        df_masc_sorted = df_masc.sort_values('Porcentaje_Mujeres', ascending=False)
        df_masc_sorted['-Porcentaje_Mujeres'] = -df_masc_sorted['Porcentaje_Mujeres']

        fig.add_trace(go.Bar(
            y=df_masc_sorted['carrera'], 
            x=df_masc_sorted['-Porcentaje_Mujeres'],
            name=ts.translate('A4_legend_minor_women', 'Minoría Mujeres'),
            orientation='h',
            marker_color='#00B8D4',
            text=df_masc_sorted['Porcentaje_Mujeres'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        ), row=1, col=2)

    fig.update_layout(
        title_text=ts.translate('A4_chart_title_careers_gender', 'Desbalance de Género en Carreras ({curso}, Matrícula >= 30)').format(curso=curso_reciente),
        showlegend=False, 
        height=550,
        template='plotly_dark',
        bargap=0.20
    )

    y_axis_title = ts.translate('A4_chart_yaxis_women_pct', '% Mujeres')

    fig.update_xaxes(
        title_text=y_axis_title, 
        row=1, col=1,
        range=[80, 105]
    )

    fig.update_xaxes(
        title_text=y_axis_title, 
        row=1, col=2,
        range=[-50, 0],
        tickvals=[-x for x in range(0, 51, 10)],
        ticktext=[str(x) for x in range(0, 51, 10)]
    )


    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=2)

    fig.update_yaxes(side="right", row=1, col=2)

    fig.add_annotation(
        text=ts.translate('A4_subplot_title_top_women', "Top 10 Carreras con Mayor % de Mujeres"),
        x=0, y=1.07, xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=14)
    )

    fig.add_annotation(
        text=ts.translate('A4_subplot_title_low_women', "Top 10 Carreras con Menor % de Mujeres"),
        x=1.2, y=1.12, xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=14)
    )


    return fig


# A5: Análisis de Concentración y Especialización

@st.cache_data
def analisis_A5(df: pd.DataFrame) -> Tuple[pd.DataFrame | None, pd.DataFrame | None, str | None, str]:
    if df.empty:
        return None, None, None, "error_empty_df"
    
    ano_mas_reciente = int(df['ano_inicio_curso'].max())
    curso_mas_reciente = f"{ano_mas_reciente}-{ano_mas_reciente+1}"
    df_reciente = df[df['ano_inicio_curso'] == ano_mas_reciente]

    if df_reciente.empty:
        return None, None, curso_mas_reciente, "error_no_data_for_year"

    df_treemap = df_reciente[df_reciente['matricula_total'] > 0]
    
    df_oferta_limitada = None
    carreras_oferta_data = df_reciente[df_reciente['matricula_total'] > 0]\
        .groupby('carrera')['entidad'].nunique().sort_values(ascending=True)
        
    if not carreras_oferta_data.empty:
        df_oferta_limitada = carreras_oferta_data.reset_index()\
            .rename(columns={'entidad': 'Num_Universidades_Ofertan'})

    return df_treemap, df_oferta_limitada, curso_mas_reciente, "success"

def graficate_A5_treemap(df_treemap: pd.DataFrame, ts: 'Translator', curso: str) -> go.Figure:
    fig = px.treemap(
        df_treemap, 
        path=[px.Constant(ts.translate('A5_treemap_root_label', "Todas las Universidades")), 'entidad', 'rama_ciencias', 'carrera'], 
        values='matricula_total',
        title=ts.translate('A5_treemap_title', 'Distribución de Matrícula ({curso})').format(curso=curso),
        color='matricula_total', 
        hover_data={'matricula_total': ':,d'},
        color_continuous_scale=['#1E88E5', '#AED581', '#FFF176']

,
        height=700,
        template='plotly_dark'
    )
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.update_traces(textinfo="label+value", textfont_size=14)
    return fig

@st.cache_data
def analisis_A5_comparativa(df: pd.DataFrame, carreras_a_comparar: List[str]) -> Tuple[pd.DataFrame | None, str]:
    if df.empty: 
        return None, "error_empty_df"
    
    if not carreras_a_comparar:
        return None, "error_no_careers_selected"

    df_filtrado = df[(df['carrera'].isin(carreras_a_comparar)) & (df['matricula_total'] > 0)].copy()
    if df_filtrado.empty: 
        return None, f"error_no_data_for_careers"

    if 'curso_academico' not in df_filtrado.columns:
        df_filtrado['curso_academico'] = df_filtrado['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")

    return df_filtrado, "success"

def graficate_A5_comparativa(df_comparativa: pd.DataFrame, ts: 'Translator') -> go.Figure:
    carreras_clave = df_comparativa['carrera'].unique().tolist()
    
    fig = px.line(
        df_comparativa, x='curso_academico', y='matricula_total', color='entidad',
        facet_row='carrera', markers=True,
        title=ts.translate('A5_chart_title_uni_comparison', 'Evolución por Universidad para: {careers}').format(careers=", ".join(carreras_clave)),
        labels={
            'matricula_total': ts.translate('A5_chart_yaxis_enrollment', 'Matrícula Total'), 
            'entidad': ts.translate('_university', 'Universidad'),
            'curso_academico': ts.translate('_academic_year', 'Curso Académico')
        },
        template='plotly_dark'
    )
    fig.update_layout(
        height=min(1200, 350 * len(carreras_clave)),
        legend_title_text=ts.translate('_university', 'Universidad')
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig

# A6: Proyecciones de Matrícula para Carreras Seleccionadas

@st.cache_data
def analisis_A6(df: pd.DataFrame, carreras_seleccionadas: List[str] | None = None, n_ultimos_anos_regresion: int = 6) -> Tuple[pd.DataFrame | None, str | None]:
    if df.empty: 
        return None, "error_empty_df"
        
    ano_mas_reciente_global = int(df['ano_inicio_curso'].max())

    if not carreras_seleccionadas: 
        carreras_recientes_data = df[df['ano_inicio_curso'] == ano_mas_reciente_global]
        if carreras_recientes_data.empty: 
            return None, "error_no_data_for_default_selection"
        carreras_a_analizar = carreras_recientes_data.groupby('carrera')['matricula_total'].sum().nlargest(3).index.tolist()
        if not carreras_a_analizar: 
            return None, "error_no_default_careers_found"
        info_seleccion = "Proyectando las 3 carreras más demandadas actualmente."
    else:
        carreras_a_analizar = carreras_seleccionadas
        info_seleccion = f"Proyectando para: {', '.join(carreras_a_analizar)}."

    df_historico_general = df[df['carrera'].isin(carreras_a_analizar)]\
        .groupby(['ano_inicio_curso', 'carrera'])['matricula_total'].sum().reset_index()
    
    if df_historico_general.empty:
        return None, "error_no_historical_data_for_selection"
        
    df_historico_general['Tipo'] = 'Histórica'

    df_proyeccion_combinado = pd.DataFrame()
    msg_detalle_proy = []

    for carrera_nombre in carreras_a_analizar:
        data_carrera_hist = df_historico_general[df_historico_general['carrera'] == carrera_nombre].copy()
        
        if len(data_carrera_hist) < 2: 
            msg_detalle_proy.append(f"{carrera_nombre} (datos históricos insuficientes)")
            continue
        
        datos_reg_carrera = data_carrera_hist.tail(n_ultimos_anos_regresion)
        
        X_c = datos_reg_carrera['ano_inicio_curso'].values.reshape(-1, 1) #type:ignore
        y_c = datos_reg_carrera['matricula_total'].values
        model_c = LinearRegression().fit(X_c, y_c) #type:ignore
            
        ultimo_ano_hist_c = data_carrera_hist['ano_inicio_curso'].max()
        ultimo_dato_hist = data_carrera_hist[data_carrera_hist['ano_inicio_curso'] == ultimo_ano_hist_c]
        last_hist_enrollment = ultimo_dato_hist['matricula_total'].iloc[0]

        anos_proy_c = np.array([ultimo_ano_hist_c + 1, ultimo_ano_hist_c + 2])
        matricula_proyectada_c = model_c.predict(anos_proy_c.reshape(-1,1)).round(0).clip(min=0)

        df_proy_carrera = pd.DataFrame({
            'ano_inicio_curso': np.concatenate(([ultimo_ano_hist_c], anos_proy_c)),
            'matricula_total': np.concatenate(([last_hist_enrollment], matricula_proyectada_c)),
            'carrera': carrera_nombre, 'Tipo': 'Proyectada'
        })
        df_proyeccion_combinado = pd.concat([df_proyeccion_combinado, df_proy_carrera], ignore_index=True)
        msg_detalle_proy.append(f"{carrera_nombre} (Reg. Lin. {len(datos_reg_carrera)} años)")

    if df_proyeccion_combinado.empty:
        return df_historico_general, f"No se pudieron generar proyecciones. Mostrando solo histórico. Detalles: {'; '.join(msg_detalle_proy)}"

    df_graficar_final = pd.concat([df_historico_general, df_proyeccion_combinado], ignore_index=True)
    df_graficar_final['curso_academico'] = df_graficar_final['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
    
    return df_graficar_final, f"{info_seleccion} Métodos: {'; '.join(msg_detalle_proy)}."

def graficate_A6_proyeccion_carreras(df_graficar: pd.DataFrame, ts: 'Translator') -> go.Figure:
    fig = px.line(
        df_graficar, x='curso_academico', y='matricula_total', 
        color='carrera', line_dash='Tipo', markers=True, 
        labels={
            'matricula_total': ts.translate('A7_chart_yaxis_enrollment', 'Matrícula Total'), 
            'Tipo': ts.translate('_date', 'Dato'), 
            'carrera': ts.translate('_career', 'Carrera')
        },
        title=ts.translate('A7_chart_title_projection', 'Proyección de Matrícula para Carreras Seleccionadas'),
        template='plotly_dark',
        line_dash_map={
            'Histórica': 'solid',
            'Proyectada': 'dash'
        },
        symbol='Tipo',
        symbol_map={
            'Histórica': 'circle',
            'Proyectada': 'diamond'
        }
    )
    fig.update_traces(marker_size=10, line_width=3)
    fig.update_layout(
        xaxis_title=ts.translate('_academic_year', 'Curso Académico'), 
        yaxis_title=ts.translate('_enrollment', 'Matrícula'),
        legend_title_text=ts.translate('_career', 'Carrera')
    )
    
    df_historico_cursos = df_graficar[df_graficar['Tipo'] == 'Histórica']['curso_academico'].unique()
    if len(df_historico_cursos) > 0:
        punto_transicion_x = len(df_historico_cursos) - 0.5
        fig.add_vline(x=punto_transicion_x, line_width=2, line_dash="dot", line_color="grey",
                      annotation_text=ts.translate('_projection_start', "Inicio Proyección"), 
                      annotation_position="top right",
                      annotation_font_size=12, annotation_font_color="grey")
                      
    return fig

# A8: Análisis de la matricula muy baja

@st.cache_data
def analisis_A7(df: pd.DataFrame) -> Tuple[pd.DataFrame|None, pd.DataFrame|None, pd.DataFrame|None, int, str | None]:
    if df.empty:
        return None, None, None, 10, "error_empty_df"
    
    primer_ano_datos = df['ano_inicio_curso'].min()
    max_year = df['ano_inicio_curso'].max()
    umbral_bajo = 10 

    carreras_nuevas_ofertas = []
    for (entidad, carrera), group in df.groupby(['entidad', 'carrera']):
        primera_aparicion_ano = group[group['matricula_total'] > 0]['ano_inicio_curso'].min()
        mat_ultimo_ano = group[group['ano_inicio_curso'] == max_year]['matricula_total'].sum()

        if pd.notna(primera_aparicion_ano) and primera_aparicion_ano > primer_ano_datos and mat_ultimo_ano > 0:
            carreras_nuevas_ofertas.append({
                'university': entidad, 
                'career': carrera, 
                'detected_start_year': int(primera_aparicion_ano), 
                'current_enrollment': int(mat_ultimo_ano)
            })
    df_nuevas = pd.DataFrame(carreras_nuevas_ofertas).sort_values(['detected_start_year', 'university', 'career'])
    nuevas_ofertas = df_nuevas.reset_index(drop=True)

    carreras_cesadas_ofertas = []
    for (entidad, carrera), group in df.groupby(['entidad', 'carrera']):
        mat_primer_ano_dataset = group[group['ano_inicio_curso'] == primer_ano_datos]['matricula_total'].sum()
        mat_ultimo_ano_dataset = group[group['ano_inicio_curso'] == max_year]['matricula_total'].sum()
        if mat_primer_ano_dataset > 0 and mat_ultimo_ano_dataset == 0:
            ultimo_ano_con_matricula = group[group['matricula_total'] > 0]['ano_inicio_curso'].max()
            if pd.notna(ultimo_ano_con_matricula) and ultimo_ano_con_matricula < max_year:
                carreras_cesadas_ofertas.append({
                    'university': entidad, 
                    'career': carrera, 
                    'last_enrollment_year': int(ultimo_ano_con_matricula) 
                })
    df_cesadas = pd.DataFrame(carreras_cesadas_ofertas).sort_values(['last_enrollment_year', 'university', 'career'], ascending=[False, True, True])
    cesadas_ofertas = df_cesadas.reset_index(drop=True)
    
    df_reciente = df[df['ano_inicio_curso'] == max_year]
    matricula_baja_reciente = df_reciente[(df_reciente['matricula_total'] > 0) & (df_reciente['matricula_total'] < umbral_bajo)]\
        .groupby(['entidad', 'carrera'])['matricula_total'].sum().astype(int).reset_index()\
        .sort_values('matricula_total').rename(columns={'entidad': 'university', 'carrera': 'career', 'matricula_total': 'enrollment'})
    baja_matricula = matricula_baja_reciente.reset_index(drop=True)
    
    return nuevas_ofertas, cesadas_ofertas, baja_matricula, umbral_bajo, "success"

def graficate_A7_nuevas_ofertas(df_nuevas: pd.DataFrame, ts: 'Translator') -> go.Figure:
    df_nuevas['display_label'] = df_nuevas['career'] + ' (' + df_nuevas['university'] + ')'
    
    fig = grouped_dot_plot(
        df_nuevas,
        x='detected_start_year',
        y='display_label',
        title=ts.translate('A7_chart_title_new_offers', 'Nuevas Ofertas o Reactivaciones Detectadas por Año'),
        yaxis_title=ts.translate('A7_chart_xaxis_year_new_offers', 'Año de Detección/Reactivación'),
        annotation_text=ts.translate('_offers', 'ofertas'),
        color_scale='Greens',
        marker_symbol='star'
    )
    return fig

def graficate_A7_cesadas_ofertas(df_cesadas: pd.DataFrame, ts: 'Translator') -> go.Figure:
    df_cesadas['display_label'] = df_cesadas['career'] + ' (' + df_cesadas['university'] + ')'
    
    fig = grouped_dot_plot(
        df_cesadas,
        x='last_enrollment_year',
        y='display_label',
        title=ts.translate('A7_chart_title_ceased_offers', 'Posibles Ceses de Oferta por Último Año con Matrícula'),
        yaxis_title=ts.translate('A7_chart_xaxis_last_year', 'Último Año con Matrícula'),
        annotation_text=ts.translate('_offers', 'ofertas'),
        color_scale='Oranges',
        marker_symbol='x'
    )
    return fig

def graficate_A7_baja_matricula(df_baja: pd.DataFrame, ts: 'Translator', curso: str, umbral: int) -> go.Figure:
    df_baja['display_label'] = df_baja['career'] + ' (' + df_baja['university'] + ')'
    
    title = ts.translate('A7_chart_title_low_enrollment', 
                         "Ofertas con Matrícula Reducida (Curso {curso}, < {umbral} Estudiantes)"
                        ).format(curso=curso, umbral=umbral)

    fig = grouped_dot_plot(
        df_baja,
        x='enrollment',
        y='display_label',
        title=title,
        yaxis_title=ts.translate('A7_chart_yaxis_low_enrollment', 'Número de Estudiantes'),
        annotation_text=ts.translate('_elements', 'elementos'),
        color_scale='Reds',
        marker_symbol='diamond-open'
    )
    return fig

@st.cache_data
def analisis_perfil_carrera_historico(df: pd.DataFrame, carrera_seleccionada: str) -> Tuple[pd.DataFrame | None, str | None, str]:
    if df.empty or not carrera_seleccionada:
        return None, None, "error_invalid_input"
    
    df_carrera = df[df['carrera'] == carrera_seleccionada].copy()
    if df_carrera.empty:
        return None, None, "error_no_data_for_career"

    rama = df_carrera['rama_ciencias'].iloc[0] if not df_carrera.empty else None

    df_evol_genero = df_carrera.groupby('ano_inicio_curso').agg(
        matricula_total=('matricula_total', 'sum'),
        matricula_mujeres=('matricula_mujeres', 'sum'),
        matricula_hombres=('matricula_hombres', 'sum')
    ).reset_index()
    
    if 'curso_academico' not in df_evol_genero.columns:
        df_evol_genero['curso_academico'] = df_evol_genero['ano_inicio_curso'].apply(lambda x: f"{x}-{x+1}")
        
    return df_evol_genero, rama, "success"

#B1: Perfil Detallado

@st.cache_data
def analisis_perfil_carr(df: pd.DataFrame, carrera_seleccionada: str, anio_seleccionado: int) -> Tuple[pd.DataFrame | None, Dict | None, str]:
    if df.empty or not carrera_seleccionada:
        return None, None, "error_invalid_input"

    df_carrera_anio = df[(df['carrera'] == carrera_seleccionada) & (df['ano_inicio_curso'] == anio_seleccionado)].copy()
    if df_carrera_anio.empty:
        return None, None, "error_no_data_for_year"

    df_unis = df_carrera_anio.groupby('entidad')['matricula_total'].sum().reset_index()
    df_unis = df_unis[df_unis['matricula_total'] > 0].sort_values(by='matricula_total', ascending=False)
    df_unis = df_unis.rename(columns={
        'entidad': 'Universidad',
        'matricula_total': f'Matricula_{anio_seleccionado}-{anio_seleccionado+1}'
    })

    total_mujeres = df_carrera_anio['matricula_mujeres'].sum()
    total_hombres = df_carrera_anio['matricula_hombres'].sum()
    datos_genero = {
        'Mujeres': total_mujeres,
        'Hombres': total_hombres,
        'Total': total_mujeres + total_hombres
    }

    return df_unis, datos_genero, "success"

def graficate_B1_evolucion_genero(df_evolucion: pd.DataFrame, ts: 'Translator', carrera_nombre: str) -> go.Figure:
    df_plot = df_evolucion.sort_values('ano_inicio_curso').copy()

    women_label = ts.translate('_women', 'Mujeres')
    men_label = ts.translate('_men', 'Hombres')
    total_label = ts.translate('_total_enrollment', 'Matrícula Total')
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_plot['curso_academico'],
        y=df_plot['matricula_mujeres'],
        mode='lines',
        line=dict(width=0.5, color='rgba(238, 130, 238, 0.8)'),
        fillcolor='rgba(238, 130, 238, 0.4)',
        fill='tozeroy',
        name=women_label,
        stackgroup='genero',
        hoverinfo='x+y',
        text=df_plot['matricula_mujeres'],
        hovertemplate=f'<b>{women_label}</b><br>%{{x}}: %{{y:,}}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_plot['curso_academico'],
        y=df_plot['matricula_hombres'],
        mode='lines',
        line=dict(width=0.5, color='rgba(30, 144, 255, 0.8)'),
        fillcolor='rgba(30, 144, 255, 0.4)',
        fill='tonexty',
        name=men_label,
        stackgroup='genero',
        hoverinfo='x+y',
        text=df_plot['matricula_hombres'],
        hovertemplate=f'<b>{men_label}</b><br>%{{x}}: %{{y:,}}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_plot['curso_academico'],
        y=df_plot['matricula_total'],
        mode='lines+markers',
        line=dict(color='white', width=3),
        marker=dict(size=8, symbol='circle', line=dict(width=1.5, color='black')),
        name=total_label,
        hoverinfo='x+y',
        text=df_plot['matricula_total'],
        hovertemplate=f'<b>{total_label}</b><br>%{{x}}: %{{y:,}}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': ts.translate('B1_chart_title_evolution_stacked', "Evolución y Composición de Matrícula: {career}").format(career=carrera_nombre),
            'xanchor': 'center',
            'x':0.5
        },
        template='plotly_dark',
        xaxis_title=ts.translate('_academic_year', 'Curso Académico'),
        yaxis_title=ts.translate('_number_of_students', 'Número de Estudiantes'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    return fig

def graficate_B1_distribucion_genero(datos_genero: dict, ts: 'Translator', carrera_nombre: str, ano: int) -> go.Figure:
    labels = {
        'women': ts.translate('_women', 'Mujeres'),
        'men': ts.translate('_men', 'Hombres')
    }
    df_pie = pd.DataFrame({
        'genero': [labels['women'], labels['men']],
        'cantidad': [datos_genero.get('Mujeres', 0), datos_genero.get('Hombres', 0)]
    })
    
    curso_str = f"{ano}-{ano+1}"
    fig = px.pie(
        df_pie, values='cantidad', names='genero',
        title=ts.translate('B1_pie_title_genero_yearly', "Distribución de Género ({curso})").format(curso=curso_str),
        color='genero',
        color_discrete_map={labels['women']: 'orchid', labels['men']: 'royalblue'},
        template='plotly_dark'
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05, 0])
    return fig

def graficate_B1_distribucion_unis(df_unis: pd.DataFrame, ts: 'Translator', carrera_nombre: str) -> go.Figure:
    matricula_col_name = df_unis.columns[1] 
    
    fig = px.bar(
        df_unis,
        x=matricula_col_name, y='Universidad', orientation='h',
        title=ts.translate('b1_bar_chart_title', "Matrícula por Universidad").format(career=carrera_nombre),
        labels={
            'Universidad': ts.translate('_university', 'Universidad'),
            matricula_col_name: ts.translate('_enrollment', 'Matrícula')
        },
        height=max(300, len(df_unis) * 30),
        template='plotly_dark',
        text=matricula_col_name
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title=ts.translate('_enrollment', 'Matrícula')
    )
    fig.update_traces(textposition='outside')
    return fig

@st.cache_data
def analisis_guia_universidades_basic(
    df_instituciones: pd.DataFrame, 
    df_matricula: pd.DataFrame, 
    provincia_seleccionada: str|None = None, 
    municipio_seleccionado: str|None = None
) -> Tuple[pd.DataFrame | None, str | None, str]:
    
    if df_instituciones.empty:
        return None, None, "error_institutions_empty"

    ano_mas_reciente_matricula = 0
    curso_str = "N/D"
    
    if not df_matricula.empty and 'ano_inicio_curso' in df_matricula.columns:
        ano_mas_reciente_matricula = int(df_matricula['ano_inicio_curso'].max())
        curso_str = f"{ano_mas_reciente_matricula}-{ano_mas_reciente_matricula+1}"
        
        df_matricula_ultimo_ano_general_uni = df_matricula[df_matricula['ano_inicio_curso'] == ano_mas_reciente_matricula].groupby('entidad').agg(
            Matricula_Total_Uni_Ultimo_Ano=('matricula_total', 'sum')
        ).reset_index().rename(columns={'entidad': 'sigla_institucion'})
        
        df_guia_base = pd.merge(
            df_instituciones,
            df_matricula_ultimo_ano_general_uni,
            on='sigla_institucion',
            how='left'
        )
        df_guia_base['Matricula_Total_Uni_Ultimo_Ano'] = df_guia_base['Matricula_Total_Uni_Ultimo_Ano'].fillna(0).astype(int)
    else:
        df_guia_base = df_instituciones.copy()
        df_guia_base['Matricula_Total_Uni_Ultimo_Ano'] = 0

    df_filtrado = df_guia_base.copy()
    if provincia_seleccionada:
        df_filtrado = df_filtrado[df_filtrado['provincia'] == provincia_seleccionada]
    if municipio_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_seleccionado]

    df_filtrado = df_filtrado.sort_values(
        by=['Matricula_Total_Uni_Ultimo_Ano', 'nombre_institucion'],
        ascending=[False, True]
    ).reset_index(drop=True)

    if df_filtrado.empty:
        return pd.DataFrame(), curso_str, "info_no_institutions_filtered"

    return df_filtrado, curso_str, "success"

#B2: Guía de Instituciones

@st.cache_data
def get_uni_academic_offer(df_matricula: pd.DataFrame, sigla_institucion: str, anio_seleccionado: int) -> Tuple[pd.DataFrame | None, Dict | None, str]:
    if df_matricula.empty:
        return None, None, "error_matricula_empty"

    df_uni_anio = df_matricula[
        (df_matricula['entidad'] == sigla_institucion) & 
        (df_matricula['ano_inicio_curso'] == anio_seleccionado)
    ].copy()

    if df_uni_anio.empty:
        return None, None, "info_no_data_for_uni_year"

    df_oferta = df_uni_anio[df_uni_anio['matricula_total'] > 0]\
        .groupby(['rama_ciencias', 'carrera'])['matricula_total'].sum().reset_index()
    df_oferta = df_oferta.rename(columns={'matricula_total': 'Matricula_Carrera_Anio'})
    df_oferta = df_oferta.sort_values(by=['rama_ciencias', 'Matricula_Carrera_Anio'], ascending=[True, False])

    total_mujeres = df_uni_anio['matricula_mujeres'].sum()
    total_hombres = df_uni_anio['matricula_hombres'].sum()
    datos_genero_uni = {
        'Mujeres': total_mujeres,
        'Hombres': total_hombres,
        'Total': total_mujeres + total_hombres
    }

    return df_oferta, datos_genero_uni, "success"

def graficate_B2_distribution(datos_genero: dict, ts: 'Translator', curso_str: str) -> go.Figure:
    labels = {
        'women': ts.translate('_women', 'Mujeres'),
        'men': ts.translate('_men', 'Hombres')
    }
    df_pie = pd.DataFrame({
        'genero': [labels['women'], labels['men']],
        'cantidad': [datos_genero.get('Mujeres', 0), datos_genero.get('Hombres', 0)]
    })
    
    fig = px.pie(
        df_pie, values='cantidad', names='genero',
        title=ts.translate('b2_pie_title_gender_total', "Género Total ({curso})").format(curso=curso_str),
        color='genero',
        color_discrete_map={labels['women']: 'orchid', labels['men']: 'royalblue'},
        height=250, template='plotly_dark'
    )
    fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig