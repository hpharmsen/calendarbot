import os.path
from pathlib import Path

fact_file = Path(__file__).parent / 'facts.txt'


def save_fact(fact):
    facts = get_facts()
    if fact in facts:
        return 'Wist ik al.'
    with open(fact_file, 'w') as f:
        f.write(facts + '\n' + fact)
    return "Ok, ik zal het onthouden."


def get_facts():
    if os.path.isfile(fact_file):
        with open(fact_file, 'r') as f:
            return f.read()
    else:
        return ''
