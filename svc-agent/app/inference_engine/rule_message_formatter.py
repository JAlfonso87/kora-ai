import json
from langchain_core.messages import SystemMessage

from app.inference_engine.required_models import (
    EvaluationResult,
    TruthValue,
)


def evaluation_to_message(
    evaluation: EvaluationResult,
) -> SystemMessage:
    """
    Convierte los resultados del motor de reglas en un mensaje
    que el agente pueda utilizar durante la generación de su respuesta.
    """

    activated = []
    uncertain = []
    rejected = []

    for rule in evaluation.rule_results:
        if rule.status == TruthValue.TRUE:
            if rule.conclusion is not None:
                activated.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "type": rule.conclusion.type,
                    "code": rule.conclusion.code,
                    "message": rule.conclusion.message,
                })

        elif rule.status == TruthValue.UNKNOWN:
            uncertain.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "missing_facts": rule.missing_facts,
            })

        elif rule.status == TruthValue.FALSE:
            rejected.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
            })

    payload = {
        "source": "deterministic_rule_engine",
        "activated_rules": activated,
        "uncertain_rules": uncertain,
        "rejected_rules": rejected,
        "missing_facts": evaluation.missing_facts,
    }

    content = (
        "RESULTADOS DEL MOTOR DE REGLAS NUTRICIONALES\n\n"
        "Estos resultados proceden de un motor determinista, "
        "no de una inferencia del modelo.\n"
        "Respeta las restricciones y conclusiones de seguridad "
        "que estén activadas. No inventes datos ausentes.\n"
        "Una regla UNKNOWN significa que no hay información "
        "suficiente para evaluarla; no significa que el alimento "
        "sea seguro ni que la condición sea falsa.\n"
        "Utiliza los mensajes de las conclusiones activadas para "
        "orientar tu respuesta. No presentes los códigos internos "
        "de las reglas al usuario, salvo que sea necesario.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )

    return SystemMessage(content=content)