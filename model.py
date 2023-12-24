from datetime import datetime

from gpteasy import GPT, set_prompt_file, get_prompt

from calendr import get_all_calendar_events, update_calendar_event, delete_calendar_event, create_calendar_event
from facts import get_facts, save_fact


class CalendarGPT(GPT):
    def __init__(self):
        super().__init__('gpt-4-1106-preview', temperature=0.3)
        set_prompt_file('prompts.toml')
        now = datetime.now()
        self.system_message = get_prompt('SYSTEM', day=now.strftime("%A, %B, %d, %Y"),
                                         time=now.strftime("%I:%M %p"))

    def run(self, query):
        print('>> ' + query)
        prompt = get_prompt('ANALYZE', instruction=query)
        actie = self.chat(prompt, return_json=True)['actie']

        if actie == 'fact':
            res = save_fact(query)
            print(res)
            return res

        facts = get_facts()
        events = [] if actie in ('create', 'other') else get_all_calendar_events()
        prompt = get_prompt(actie.upper(), instruction=query, facts=facts, events=events)
        details = self.chat(prompt, return_json=True)

        match details['actie']:
            case 'create':
                create_calendar_event(details)
            case 'delete':
                delete_calendar_event(details)
            case 'update':
                update_calendar_event(details)
        print('<< ' + details['answer'])
        return details['answer']
