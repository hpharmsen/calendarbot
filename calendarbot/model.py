import os
from datetime import datetime
from pathlib import Path
from gpteasy import GPT, set_prompt_file, get_prompt

from calendars import Calendars
from facts import get_facts, save_fact


class CalendarGPT(GPT):
    def __init__(self, calendars: Calendars):
        super().__init__(os.environ.get('OPENAI_MODEL', 'gpt-4-1106-preview'), temperature=0.3)
        set_prompt_file(Path(__file__).parent / 'prompts.toml')
        now = datetime.now()
        self.system_message = get_prompt('SYSTEM', day=now.strftime("%A, %B, %d, %Y"),
                                         time=now.strftime("%I:%M %p"))
        self.calendars = calendars

    def run(self, query):
        prompt = get_prompt('ANALYZE', instruction=query)
        actie = self.chat(prompt, return_json=True)['actie']

        if actie == 'fact':
            return save_fact(query)

        facts = get_facts()
        events = [] if actie in ('create', 'other') else self.calendars.get_all_events()
        prompt = get_prompt(actie.upper(), instruction=query, facts=facts, events=events)
        details = self.chat(prompt, return_json=True)

        match details['actie']:
            case 'create':
                self.calendars.create_event(details)
            case 'delete':
                self.calendars.delete_event(details)
            case 'update':
                self.calendars.update_event(details)
        return details['answer']
