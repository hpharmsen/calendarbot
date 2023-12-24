import sys

from model import CalendarGPT


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
    model = CalendarGPT()
    match query := get_mode():
        case '':
            print('Usage: python main.py [-i] [-t] [query]')
        case 'interactive':
            interactive(model)
        case 'test':
            model.run("Onthoud: Mijn vrouw heet Monique, zij is gids en tourmanager")
            model.run("Wat heb ik op vier januari?")
            model.run("Gooi die afspraak met Michael eruit")
            model.run("Maak van vijf uur 's middags tot 11 uur een afspraak met Michael voor de 27e.")
            model.run("Schuif de afspraak met Michael naar 15:00 en vul als locatie Laren in")
            model.run("Gooi die afspraak met Michael eruit")
            model.run("Geef me alle softbaltrainingen")
        case _:
            model.run(query)
