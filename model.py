from datetime import datetime

from gpteasy import GPT, set_prompt_file, get_prompt
from gpteasy.gpt import GptFunction

from calendr import get_calendar_event, get_all_calendar_events, update_calendar_event

_model = None
def get_model():
    global _model
    if not _model:
        set_prompt_file('prompts.toml')
        _model = GPT('gpt-4-1106-preview', temperature=0.3)
        date = datetime.now()
        _model.system_message = get_prompt('SYSTEM', day=date.strftime("%A, %B, %d, %Y"), time=date.strftime("%I:%M %p"))
        _model.add_function(find_calendar_events_factory())
        _model.add_function(find_all_events_factory())
        _model.add_function(update_event_factory())

    return _model


def find_calendar_events_factory():
    func = GptFunction(name = 'find_calendar_events',
                       description = """This function looks up specific events in the calendar. 
                                        It takes a time_min  and time_max, and a query string. All are optional.""")
    func.add_param(name="time_min", type="string", required=False, description="Starting date/datetime")
    func.add_param(name="time_max", type="string", required=False, description="Ending date/datetime")
    func.add_param(name="query", type="string", required=False,
                   description="""Free text search terms to find events that match these terms 
                                  in any field, except for extended properties""")
    func.callback = get_calendar_event  # Actual Python function to call
    return func


def find_all_events_factory():
    func = GptFunction(name = 'find_calendar_events',
                                       description = """This function retrieves events in from calendar. 
                                       It can be used to broaden the search if a specific event is not found.""")
    func.callback = get_all_calendar_events  # Actual Python function to call
    return func


def update_event_factory():
    # Function to update an event
    func = GptFunction(name = 'update_event', description = """This function updates an event in the calendar. 
        It takes a calendar_no, event_id, and optionally a summary, start, end, location, description, attendees.""")
    func.add_param(name="calendar_no", type="string", required=True, description="Calendar number")
    func.add_param(name="event_id", type="string", required=True, description="Calendar event id")
    func.callback = update_calendar_event  # Actual Python function to call
    return func


def instruction(instruction_text):
    modl = get_model()
    events = get_all_calendar_events()
    prompt = get_prompt('INSTRUCTION', instruction=instruction_text, events=events)
    response = modl.chat(prompt)
    return response