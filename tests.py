import plotly.express as px
import pandas as pd

# Crear un DataFrame más definido
df = pd.DataFrame({
    "Tiempo": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Valor_A": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
    "Valor_B": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
})

# Transformar los datos para que sean compatibles con la animación
df_melted = df.melt(id_vars=["Tiempo"], var_name="Categoría", value_name="Valor")

# Crear el gráfico de líneas animado
fig = px.line(df_melted, x="Tiempo", y="Valor", color="Categoría", animation_frame="Tiempo")

# Mostrar el gráfico
fig.show()