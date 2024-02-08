# Calendarbot

Chat interface for Google Calendar using OpenAI's models.

## Installation

1. Install dependencies:
```bash
python -m pip install -r requirements.in
```
2. Create an OpenAI acccount [here](chat.openai.com/auth/login)
3. Create OpenAI api keys [here](https://beta.openai.com/account/api-keys)
4. Create a .env file with the following content:
```bash
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-openai-organization-id

OPENAI_MODEL=gpt-4-1106-preview

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
# See https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html

GOOGLE_CALENDAR_1=your_first_calendar_id Normally your en
GOOGLE_CALENDAR_2=your second calendar_id (optional)
GOOGLE_CALENDAR_3=your third calendar_id (optional)
etc...

```

## Usage
```bash
python main.py "Add a meeting with John tomorrow at 3pm"
python main.py "What's in my calendar the coming weekend?"
```
## Interactive mode
```bash
python main.py -i
```

## Facts storage
If you state facts, the bot will remember that
```bash
python main.py "My wifes name is Monique"
OK, I'll remember that.

python main.py "When is my wifes flight"
Monique's flight from Rome is scheduled Thursday at 11:20.
```

## Usage from your Python code

```python
from dotenv import load_dotenv

from calendarbot import Calendars, CalendarAgent

load_dotenv()
calendars = Calendars()
model = CalendarAgent(calendars)
print(model.run("Add a meeting with John tomorrow at 3pm"))
```