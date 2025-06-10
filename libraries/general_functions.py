import io
import re

def to_csv_string(list_of_dicts):
    """
    Convierte una lista de diccionarios a una cadena de texto en formato CSV.
    Es mucho más eficiente que JSON para datos tabulares.
    """
    if not list_of_dicts:
        return ""
    
    # Usamos io.StringIO para construir el CSV en memoria, es muy eficiente.
    output = io.StringIO()
    # Los encabezados se toman del primer diccionario
    headers = list_of_dicts[0].keys()
    output.write(','.join(headers) + '\n')
    
    # Escribir las filas
    for row_dict in list_of_dicts:
        row = [str(row_dict.get(h, '')) for h in headers]
        output.write(','.join(row) + '\n')
        
    # Devolver el contenido de la cadena, eliminando el último '\n'
    return output.getvalue().strip()


def parse_blocks(pattern, texto):
    """
    Encuentra bloques de texto delimitados por ```tipo y ``` en el texto dado.
    Devuelve un iterador con tuplas (tipo, contenido) para cada bloque encontrado.

    Args:
        texto (str): El texto a analizar.

    Yields:
        tuple: Una tupla (tipo, contenido) para cada bloque encontrado.
    """
    for match in re.finditer(pattern, texto): #DEBE SER  re.DOTALL el pattern
        yield match.group("tipo"), match.group("contenido")