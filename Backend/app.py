import os
from groq import Groq  # Importamos Groq en lugar de Gemini
from flask import Flask, request, jsonify, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError

# Límite de caracteres para el texto del usuario (evita gastar la cuota de la API)
MAX_CARACTERES = 2000

# 1. Iniciar Flask (el "mesero")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]  # nunca lo escribas en el código
csrf = CSRFProtect(app)

# 2. Configurar la API de IA (la "cocina" de Groq)
client = None
try:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )
except Exception as e:
    print(f"ERROR: No se pudo configurar el cliente de Groq. Revisa la API Key. {e}", flush=True)


# Si el token CSRF falta o expiró, respondemos en JSON (el HTML lo muestra en pantalla)
@app.errorhandler(CSRFError)
def error_csrf(e):
    print(f"CSRF rechazado: {e.description}", flush=True)
    return jsonify({'respuesta': 'La sesión expiró o la petición no es válida. Recarga la página e inténtalo de nuevo.'}), 400


# 3. Ruta principal: Sirve la página web
@app.route('/')
def index():
    return render_template('index.html')

# 4. Ruta de la IA: Recibe peticiones del HTML
@app.route('/procesar', methods=['POST'])
def procesar_texto():
    # Recibe el texto y la tarea (y valida que lleguen bien)
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}
    texto_usuario = str(datos.get('texto', '')).strip()
    tarea_usuario = str(datos.get('tarea', '')).strip()

    if not texto_usuario or not tarea_usuario:
        return jsonify({'respuesta': 'Escribe un texto y elige una tarea.'}), 400
    if len(texto_usuario) > MAX_CARACTERES:
        return jsonify({'respuesta': f'El texto es muy largo (máximo {MAX_CARACTERES} caracteres).'}), 400
    if client is None:
        return jsonify({'respuesta': 'El servicio de IA no está disponible en este momento.'}), 503

    try:
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
            model="llama-3.1-8b-instant"
        )

        # Obtenemos la respuesta
        respuesta_texto = respuesta_ia.choices[0].message.content

        # Devuelve la respuesta al HTML
        return jsonify({'respuesta': respuesta_texto})

    except Exception as e:
        # El detalle del error se queda en el log; al usuario le damos un mensaje genérico
        print(f"¡¡¡ERROR CAPTURADO!!!: {e}", flush=True)
        return jsonify({'respuesta': 'Ocurrió un error al procesar tu texto. Inténtalo de nuevo.'}), 500

# Esta parte solo se usa si lo corres localmente
if __name__ == '__main__':
    # El modo debug queda apagado salvo que definas FLASK_DEBUG=1 (solo en tu PC)
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")