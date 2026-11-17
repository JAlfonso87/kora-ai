from app.toolbox_module.vision_tools.tool_functions_vision import VisionTool

tools_vision = [
    {
        "type": "function",
        "function": {
            "name": "load_and_analyze_picture",
            "description": """
                Utiliza esta herramienta SIEMPRE que el usuario solicite identificar, analizar, describir o conocer información nutricional de alimentos mediante una imagen.
                
                **IMPORTANTE: La imagen ya está disponible en una ruta fija dentro del entorno de ejecución. La herramienta accede a ella internamente. No necesita recibir una imagen, una ruta, argumentos ni parámetros adicionales.**
                
                Cuando el usuario solicite analizar una comida, identificar alimentos, estimar calorías, conocer ingredientes o evaluar nutricionalmente un platillo:
                
                1. Invoca DIRECTAMENTE esta herramienta, sin solicitar información adicional.
                2. NO pidas al usuario que adjunte, cargue, envíe o proporcione una fotografía.
                3. NO preguntes dónde está almacenada la imagen.
                4. NO esperes una imagen adjunta para ejecutar la herramienta.
                5. NO intentes describir la imagen por tu cuenta: delega el análisis visual a esta herramienta.
                
                La herramienta debe examinar la imagen disponible, identificar los alimentos, estimar sus porciones y cantidades, reconocer los ingredientes visibles y calcular aproximadamente calorías, proteínas, carbohidratos y grasas.
                
                Devuelve los resultados de forma estructurada, incluyendo:
                - Alimentos identificados.
                - Porciones y cantidades estimadas.
                - Calorías aproximadas.
                - Proteínas, carbohidratos y grasas.
                - Nivel de confianza de la identificación.
                
                **REGLA PRIORITARIA: Si el usuario solicita un análisis visual de alimentos, ejecuta la herramienta inmediatamente. Nunca solicites una imagen al usuario, puesto que la herramienta ya dispone de acceso a ella.**
            """,
        }
    }
]

tool_specs_vision = {
    "load_and_analyze_picture": {
        "function": VisionTool().load_and_analyze_picture,
        "params_model": None
    }
}