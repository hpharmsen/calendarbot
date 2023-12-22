# https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html

from model import instruction


def interactive(model):
    user_input = ''
    while user_input != 'exit':
        user_input = input('> ')
        response = model.chat(user_input)
        print(response)


if __name__ == '__main__':
    #interactive(model)
    response = instruction('Verander de locatie van de afspraak met Marcel en Lenny naar Windjammerdijk 14')
    print(response)
