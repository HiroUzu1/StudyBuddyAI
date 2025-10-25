import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

# 1. Iniciar Flask (el "mesero")
app = Flask(__name__)

# 2. Configurar la API de IA (la "cocina")
# Usamos os.environ.get para tomar la clave de Render (¡Más seguro!)
api_key = os.environ.get("GEMINI_API_KEY") 
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. Ruta principal: Sirve la página web
@app.route('/')
def index():
    # Busca el archivo "index.html" en la carpeta "templates"
    return render_template('index.html')

# 4. Ruta de la IA: Recibe peticiones del HTML
@app.route('/procesar', methods=['POST'])
def procesar_texto():
    try:
        # Recibe el texto y la tarea (traducir, resumir, etc.)
        datos = request.json
        texto_usuario = datos['texto']
        tarea_usuario = datos['tarea']

        # Crea el prompt (la orden) para la IA
        prompt = f"Tu eres StudyBuddy AI, un asistente para aprender inglés. {tarea_usuario} el siguiente texto: '{texto_usuario}'"

        # Envía la orden a la IA
        respuesta_ia = model.generate_content(prompt)

        # Devuelve la respuesta al HTML
        return jsonify({'respuesta': respuesta_ia.text})

    except Exception as e:
        print(f"¡¡¡ERROR CAPTURADO!!!: {e}", flush=True)
        return jsonify({'respuesta': f"Error: {str(e)}"})

# Esta parte solo se usa si lo corres localmente
if __name__ == '__main__':
    app.run(debug=True)