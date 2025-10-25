import os
from groq import Groq  # Importamos Groq en lugar de Gemini
from flask import Flask, request, jsonify, render_template

# 1. Iniciar Flask (el "mesero")
app = Flask(__name__)

# 2. Configurar la API de IA (la "cocina" de Groq)
try:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )
except Exception as e:
    print(f"ERROR: No se pudo configurar el cliente de Groq. Revisa la API Key. {e}", flush=True)

# 3. Ruta principal: Sirve la página web
@app.route('/')
def index():
    return render_template('index.html')

# 4. Ruta de la IA: Recibe peticiones del HTML
@app.route('/procesar', methods=['POST'])
def procesar_texto():
    try:
        # Recibe el texto y la tarea
        datos = request.json
        texto_usuario = datos['texto']
        tarea_usuario = datos['tarea']
        
        # Crea el prompt (la orden) para la IA
        prompt_completo = f"Tu eres StudyBuddy AI, un asistente para aprender inglés. {tarea_usuario} el siguiente texto: '{texto_usuario}'"
        
        # Envía la orden a la IA (la estructura de Groq es diferente)
        respuesta_ia = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente de IA útil."
                },
                {
                    "role": "user",
                    "content": prompt_completo
                }
            ],
            # Usamos un modelo rápido de Llama 3
            model="llama3-8b-8192" 
        )
        
        # Obtenemos la respuesta
        respuesta_texto = respuesta_ia.choices[0].message.content
        
        # Devuelve la respuesta al HTML
        return jsonify({'respuesta': respuesta_texto})
        
    except Exception as e:
        # Si algo falla, lo imprimimos en el log
        print(f"¡¡¡ERROR CAPTURADO!!!: {e}", flush=True) 
        return jsonify({'respuesta': f"Error: {str(e)}"})

# Esta parte solo se usa si lo corres localmente
if __name__ == '__main__':
    app.run(debug=True)