# 🎓 Análisis Estratégico de la Matrícula Universitaria en Cuba (2015-2025)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cuba-matricle-university.streamlit.app/)
<!-- 🔗 Reemplaza 'https://cuba-matricle-university.streamlit.app/' con el enlace real a tu app desplegada en Streamlit Community Cloud -->

## 🌟 Descripción del Proyecto

Este proyecto presenta una aplicación web interactiva para el análisis exhaustivo de los datos de matrícula en las universidades de Cuba, cubriendo el período académico desde 2015-2016 hasta 2024-2025. Desarrollada con Streamlit, la herramienta permite a los usuarios explorar tendencias nacionales, la distribución de estudiantes por ramas del saber y carreras específicas, análisis de equidad de género, la especialización de las universidades, y proyecciones futuras basadas en modelos de regresión lineal.

El objetivo principal es proporcionar *insights* visuales y basados en datos que sirvan de apoyo fundamental para la toma de decisiones estratégicas por parte de la Sede Central que gestiona las universidades cubanas. Adicionalmente, busca ofrecer información valiosa y accesible para investigadores, planificadores educativos, estudiantes y el público general interesado en el panorama de la educación superior en Cuba.

## ✨ Características Clave

*   **Visión Histórica Detallada:** Evolución de la matrícula a nivel nacional, por rama de ciencias y por carrera individual.
*   **Proyecciones a Futuro:** Estimaciones a 2 años para la matrícula total, por ramas y para carreras seleccionadas interactivamente, utilizando regresión lineal sobre los últimos 6 años de datos.
*   **Análisis de Género:** Visualización clara de la participación femenina en diferentes áreas del conocimiento y carreras específicas, destacando avances y desafíos.
*   **Dinámica Institucional:** Exploración de la concentración y especialización de las universidades, y comparativas de matrícula para carreras estratégicas entre diferentes instituciones.
*   **Identificación de Áreas de Atención:** Detección proactiva de carreras con matrícula reducida, posibles nuevas ofertas o ceses de programas.
*   **Interfaz Intuitiva y Dinámica:** Navegación fluida por secciones temáticas, gráficos interactivos generados con Plotly y la capacidad para que el usuario seleccione carreras de interés para análisis específicos.
*   **Narrativa Basada en Datos (Storytelling):** Presentación de los hallazgos estructurada y con interpretaciones para facilitar la comprensión del impacto de los datos.

## 🛠️ Stack Tecnológico

*   **Lenguaje Principal:** Python 3.13.1
*   **Framework de la Aplicación Web:** Streamlit
*   **Manipulación y Análisis de Datos:** Pandas
*   **Visualizaciones Interactivas:** Plotly
*   **Operaciones Numéricas:** NumPy
*   **Modelado (Regresión Lineal):** Scikit-learn

## 🚀 Despliegue y Ejecución Local

### Acceder a la Aplicación Desplegada

Puedes interactuar con la versión desplegada de esta aplicación directamente en Streamlit Community Cloud:
[**Acceder a la App en Streamlit**](https://cuba-matricle-university.streamlit.app/)

### Ejecutar en tu Máquina Local

Si deseas ejecutar la aplicación en tu propio entorno para desarrollo o pruebas:

1.  **Clona el Repositorio:**
    ```bash
    git clone https://github.com/Retype15/cuba_matricle_university.git
    cd cuba_matricle_university
    ```

2.  **Crea y Activa un Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    ```
    *   Windows: `.\venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Instala las Dependencias:**
    Con el entorno virtual activado, instala los paquetes necesarios:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepara el Archivo de Datos:**
    Asegúrate de que el archivo de datos `db_long.csv` se encuentre en la raíz del directorio del proyecto.

5.  **Ejecuta la Aplicación:**
    Utiliza el siguiente comando en tu terminal:
    ```bash
    streamlit run streamlit_app.py
    ```
    Streamlit iniciará un servidor local y la aplicación se abrirá en tu navegador (usualmente en `http://localhost:8501`).

## 📊 Datos
La aplicación se basa en un conjunto de datos (`db_long.csv`) que detalla la matrícula en universidades cubanas por rama de ciencias, carrera, entidad (universidad) y género, para los cursos académicos desde 2015-2016 hasta 2024-2025.

## 🧑‍💻 Colaboradores del Proyecto

*   Reynier Ramos
*   Ernesto [Apellido Pendiente]

## 📜 Licencia

Este proyecto se distribuye bajo los términos de la **Licencia Apache 2.0**.
Puedes encontrar el texto completo de la licencia en el archivo `LICENSE` de este repositorio o en:
[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

---

Esperamos que esta herramienta analítica sea de gran utilidad. ¡Cualquier feedback es bienvenido!