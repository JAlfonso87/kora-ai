from app.toolbox_module.rag_tools.tool_functions_rag import RAGTool
from app.toolbox_module.tool_input_models import RAGQueryRequirements

tools_rag = [
    {
        "type": "function",
        "function": {
            "name": "rag_query",
            "description": """
                Busca información relevante en la base de conocimiento
                nutricional de Kora AI. Utilízala cuando el usuario
                pregunte por conceptos, evidencia, alimentos, nutrientes
                o información nutricional que requiera consultar las
                fuentes documentales. No inventes fuentes ni afirmes que
                la base contiene información que no fue recuperada.   
            """,
            "parameters": RAGQueryRequirements.model_json_schema(),
        }
    },
]

tool_specs_rag = {
    "rag_query": {
        "function": RAGTool().execute,
        "params_model": RAGQueryRequirements
    },
}