import json 
from pathlib import Path

from app.toolbox_module.models.tool_requirements import NutritionalContext

from app.inference_module.facts.fact_generator import factorize
from app.inference_module.rules.rule_evaluator import RuleEngine
from app.inference_module.models.required_models import Rule
from app.inference_module.formatters.rule_message_formatter import evaluation_to_message

def start_engine(nutritional_context: NutritionalContext):

    rule_engine = RuleEngine()

    facts = factorize(nutritional_context)
    print("<< LISTA DE HECHOS RECUPERADOS >>")
    print(facts)
    
    RULES_PATH = (
        Path(__file__).resolve().parent
        / "rules_catalog.json"
    )
    
    with open(RULES_PATH, "r", encoding="utf-8") as file:
        rules_data = json.load(file)
    
    rules = [
        Rule.model_validate(data)
        for data in rules_data["rules"]
    ]
    
    rules_result = rule_engine.evaluate(facts, rules)
    
    return [evaluation_to_message(rules_result)]