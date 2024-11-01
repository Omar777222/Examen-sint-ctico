from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Expresiones regulares para validar CURP y tokens
curp_pattern = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$')
states = {
    "AS": "Aguascalientes", "BC": "Baja California", "BS": "Baja California Sur", 
    "CC": "Campeche", "CL": "Coahuila", "CM": "Colima", "CS": "Chiapas", 
    "CH": "Chihuahua", "DF": "Ciudad de México", "DG": "Durango", "GT": "Guanajuato", 
    "GR": "Guerrero", "HG": "Hidalgo", "JC": "Jalisco", "MC": "Estado de México", 
    "MN": "Michoacán", "MS": "Morelos", "NT": "Nayarit", "NL": "Nuevo León", 
    "OC": "Oaxaca", "PL": "Puebla", "QT": "Querétaro", "QR": "Quintana Roo", 
    "SP": "San Luis Potosí", "SL": "Sinaloa", "SR": "Sonora", "TC": "Tabasco", 
    "TS": "Tamaulipas", "TL": "Tlaxcala", "VZ": "Veracruz", "YN": "Yucatán", 
    "ZS": "Zacatecas"
}

def es_bisiesto(anio):
    """Verifica si un año es bisiesto."""
    anio = int(anio)
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

def fecha_valida(anio, mes, dia):
    """Verifica si una fecha es válida."""
    anio = int(anio)
    mes = int(mes)
    dia = int(dia)
    
    # Días por mes
    dias_por_mes = {
        1: 31, 2: 28, 3: 31,
        4: 30, 5: 31, 6: 30, 7: 31,
        8: 31, 9: 30, 10: 31,
        11: 30, 12: 31
    }
    
    # Si es 29 de febrero, lo marcamos como inválido aunque sea bisiesto
    if mes == 2 and dia == 29 and es_bisiesto(anio):
        return False
    
    return mes in dias_por_mes and 1 <= dia <= dias_por_mes[mes]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    curp = data.get('curp', '').upper()

    tokens = []
    token_counts = {
        "Letras": 0,
        "Números": 0,
        "Símbolos": 0
    }
    
    # Analizador Léxico
    if len(curp) == 18 and curp_pattern.match(curp):
        # Extraer datos de la CURP
        tokens.append({"token": "Primer letra del apellido paterno", "valor": curp[0], "tipo": "Primera letra del primer apellido"})
        tokens.append({"token": "Primera vocal interna del apellido paterno", "valor": curp[1], "tipo": "Primera vocal en el apellido paterno"})
        tokens.append({"token": "Primera letra del apellido materno", "valor": curp[2], "tipo": "Primera letra del segundo apellido"})
        tokens.append({"token": "Primer letra del nombre", "valor": curp[3], "tipo": "Primera letra del nombre"})
        
        # Separación de fecha de nacimiento (Año, Mes, Día)
        anio = int("19" + curp[4:6]) if int(curp[4:6]) > 22 else int("20" + curp[4:6])
        mes = int(curp[6:8])
        dia = int(curp[8:10])
        tokens.append({"token": "Año de nacimiento", "valor": curp[4:6], "tipo": "Año (AA)"})
        tokens.append({"token": "Mes de nacimiento", "valor": curp[6:8], "tipo": "Mes (MM)"})
        tokens.append({"token": "Día de nacimiento", "valor": curp[8:10], "tipo": "Día (DD)"})

        # Sexo
        sexo = "Hombre" if curp[10] == "H" else "Mujer"
        tokens.append({"token": "Género de la persona", "valor": curp[10], "tipo": sexo})

        # Entidad Federativa
        estado_codigo = curp[11:13]
        estado_nombre = states.get(estado_codigo, "Entidad no válida")
        tokens.append({"token": "Entidad federativa", "valor": estado_codigo, "tipo": estado_nombre})

        tokens.append({"token": "Primera consonante interna del apellido paterno", "valor": curp[13], "tipo": "Primera consonante interna del apellido paterno"})
        tokens.append({"token": "Primera consonante interna del apellido materno", "valor": curp[14], "tipo": "Primera consonante interna del apellido materno"})
        tokens.append({"token": "Primera consonante interna del nombre", "valor": curp[15], "tipo": "Primera consonante interna del nombre"})
        tokens.append({"token": "Dígito de homonimia", "valor": curp[16], "tipo": "Dígito asignado para evitar duplicados"})
        tokens.append({"token": "Dígito verificador", "valor": curp[17], "tipo": "Dígito para verificación de la CURP"})

        # Contar tipos de tokens
        for char in curp:
            if char.isalpha():
                token_counts["Letras"] += 1
            elif char.isdigit():
                token_counts["Números"] += 1
            else:
                token_counts["Símbolos"] += 1
    else:
        tokens.append({"token": "Error", "valor": curp, "tipo": "La CURP no tiene el formato correcto"})

    # Analizador Sintáctico: Validar si la cadena es válida y rechazar años bisiestos
    is_valid_syntax = bool(curp_pattern.match(curp)) and fecha_valida(anio, mes, dia)

    response = {
        "tokens": tokens,
        "token_counts": token_counts,
        "is_valid_syntax": is_valid_syntax
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
