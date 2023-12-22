# https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html
import json
from datetime import datetime

from gcsa.google_calendar import GoogleCalendar, Credentials
from gcsa.event import Event
from gpteasy import GPT
from gpteasy.gpt import GptFunction


def get_model():
    model = GPT('gpt-4-1106-preview', temperature=0.3)
    date = datetime.now()
    model.system_message = f"""
        Vandaag is {date:%A}, {date:%B} {date.day}, {date.year}. The time is {date:%I}:{date:%M} {date:%p}.
        Je bent mijn personal assistant. Je beheert mijn ageinda.
        Ik stuur vraag je dingen over mijn agenda en vraag je om agenda afspraken aan te maken of te wijzigen.
        Je antwoord als een goede PA zou doen. Spreek me aan met "je". Vraag om meer informatie als je dat nodig hebt."""
    find_calendar_events = GptFunction(name = 'find_calendar_events',
                                       description = """This function looks up events in the calendar. It takes a time_min 
                                                        and time_max, and a query string. All are optional.""")
    find_calendar_events.add_param(name="time_min", type="string", required=False, description="Starting date/datetime")
    find_calendar_events.add_param(name="time_max", type="string", required=False, description="Ending date/datetime")
    find_calendar_events.add_param(name="query", type="string", required=False,
                                   description="""Free text search terms to find events that match these terms 
                                                  in any field, except for extended properties""")
    find_calendar_events.callback = get_calendar_event  # Actual Python function to call
    model.add_function(find_calendar_events)
    return model

def get_calendar_event(time_min=None, time_max=None, query=None):
    cal = get_calendar()

    if time_min: time_min = datetime.fromisoformat(time_min)
    if time_max: time_max = datetime.fromisoformat(time_max)
    events = cal.get_events(time_min, time_max, query=query, order_by="startTime", single_events=True)
    events = list(events)
    result = [{'summary': event.summary, 'start': str(event.start), 'end': str(event.end), 'location': event.location,
               'description': event.description, 'attendees': str(event.attendees)} for event in events]
    return json.dumps(result)

def create_calendar_event(summary, start, end, location=None, description=None, attendees=None):
    cal = get_calendar()
    event = Event(summary, start, end, location=location, description=description, attendees=attendees)
    cal.add_event(event)
    # event = Event(
    #     'The Glass Menagerie',
    #     start=datetime(2020, 7, 10, 19, 0),
    #     location='Záhřebská 468/21',
    #     minutes_before_popup_reminder=15
    # )


def get_calendar():
    return GoogleCalendar('hp@harmsen.nl', credentials_path="client_secret_573107433733-cr8pq51ig2f9n3i6aueevvj0tp9kskbb.apps.googleusercontent.com.json")


def interactive(model):
    user_input = ''
    while user_input != 'exit':
        user_input = input('> ')
        response = model.chat(user_input)
        print(response)


if __name__ == '__main__':
    model = get_model()
    #interactive(model)
    response = model.chat('Wanneer is de pubquiz?')
    print(response)
    response = model.chat('Wanneer zijn de zaaltrainingen?')
    print(response)
    response = model.chat('Ik bedoel softbal')
    print(response)