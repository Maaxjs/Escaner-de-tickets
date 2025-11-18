import os
import json
from groq import Groq
from config import GROQ_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

try:
    client = Groq()
except Exception as e:
    print(f"Error: {e}")
    print("Asegurate de poner tu API Key en la variable de entorno GROQ_API_KEY")
    exit()

def create_prompt(ticket_text):
    return f"""
    Eres un experto en procesar tickets. Analiza el texto del ticket y devuelve SÓLO el objeto JSON.

    TEXTO DEL TICKET:
    ```
    {ticket_text}
    ```

    EXTRAE:
    1. "nombre_lugar": El nombre de la tienda.
    2. "items": Una lista de objetos con "producto", "cantidad", "precio_unitario" y "precio_total" (como números, no strings).
    3. "precio_total_compra": El número del total final.
    
    TENER EN CUENTA:
    - A veces el "Total" refiere al monto con el que se pagó y luego hay un vuelto, deben considerarse esos casos
    - Si no está disponible la cantidad, estimar 1
    - Si no está disponible el precio unitario, calcular como precio_total / cantidad
    
    Formato de salida:
    ```json
    {{
      "nombre_lugar": "...",
      "items": [
        {{"producto": "...", "cantidad": 1, "precio_unitario": 100.00, "precio_total": 100.00}},
        {{"producto": "...", "cantidad": 2, "precio_unitario": 50.00, "precio_total": 100.00}}
      ],
      "precio_total_compra": 200.00
    }}
    ```

    DESPUES DEL OUTPUT MODO JSON NO PONGAS ABSOLUTAMENTE NADA MÁS
    """


def process_ticket(ticket_data):
    """Procesa un ticket y devuelve el JSON parseado"""
    prompt = create_prompt(ticket_data)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant", 
            
            # Forzamos la respuesta a ser un JSON
            response_format={"type": "json_object"},
            
            temperature=0.0
        )

        # OBTENER EL JSON
        response_content = chat_completion.choices[0].message.content
        parsed_json = json.loads(response_content)
        
        return parsed_json

    except Exception as e:
        return {
            'error': str(e),
            'nombre_lugar': 'Error',
            'items': [],
            'precio_total_compra': 0
        }

    except Exception as e:
        print(f"Error procesando: {e}")
    