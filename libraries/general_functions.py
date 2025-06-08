import io

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