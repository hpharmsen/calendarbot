import sys

from dotenv import load_dotenv

from calendarbot.calendars import Calendars
from model import CalendarAgent


def interactive(model):
    user_input = ''
    while user_input != 'exit':
        user_input = input('> ')
        model.run(user_input)


def get_mode():
    if '-i' in sys.argv:
        return 'interactive'
    if '-t' in sys.argv:
        return 'test'
    return ' '.join(sys.argv[1:])


if __name__ == '__main__':
    load_dotenv()
    calendars = Calendars()
    model = CalendarAgent(calendars)

    match query := get_mode():
        case '':
            print('Usage: python main.py [-i] [-t] [query]')
        case 'interactive':
            interactive(model)
        case 'test':
            print(model.run("Onthoud: Mijn vrouw heet Monique, zij is gids en tourmanager"))
            print(model.run("Wat heb ik op vier januari?"))
            print(model.run("Gooi die afspraak met Michael eruit"))
            print(model.run("Maak van vijf uur 's middags tot 11 uur een afspraak met Michael voor de 27e."))
            print(model.run("Schuif de afspraak met Michael naar 15:00 en vul als locatie Laren in"))
            print(model.run("Gooi die afspraak met Michael eruit"))
            print(model.run("Geef me alle softbaltrainingen"))
            print(model.run("Douwe wil een afspraak plannen om bier te drinken. Hij wil dit op een avond maar niet in het weekend. Wanneer kan ik?"))
        case _:
            model.run(query)
