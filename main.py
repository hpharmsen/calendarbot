# https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html
import json

from calendr import create_calendar_event, get_calendar_event, delete_calendar_event, update_calendar_event
from model import instruction


def interactive(model):
    user_input = ''
    while user_input != 'exit':
        user_input = input('> ')
        print(run(user_input))

def run(query):
    print('>> ' + query)
    response = instruction(query)
    #print(json.dumps(response, indent=2))

    match response['actie']:
        case 'create':
            create_calendar_event(response)
        case 'delete':
            delete_calendar_event(response)
        case 'update':
            update_calendar_event(response)
    print(response['answer'])

if __name__ == '__main__':
    run("In welk continent ligt Namibië?")
    run("Wat heb ik op vier januari?")
    run("Gooi die afspraak met Michael eruit")
    run("Maak van vijf uur 's middags tot 11 uur een afspraak met Michael voor de 27e.")
    run("Schuif de afspraak met Michael naar 15:00 en vul als locatie Laren in")
    run("Gooi die afspraak met Michael eruit")
