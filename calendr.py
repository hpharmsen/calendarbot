import json
from datetime import datetime, timedelta

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

CALENDARS = {1: 'hp@harmsen.nl',
             2: 'c_61bbafb4b74cfe103dec7bc85f942b65db879304d4b6eaae036ef4935fd8a6fa@group.calendar.google.com'}

def get_calendar_event(time_min=None, time_max=None, query=None):
    result = []
    for id in CALENDARS.values():
        cal = get_calendar(id)

        if time_min: time_min = datetime.fromisoformat(time_min)
        if time_max: time_max = datetime.fromisoformat(time_max)
        events = cal.get_events(time_min, time_max, query=query, order_by="startTime", single_events=True)
        result += [{'summary': event.summary, 'start': str(event.start), 'end': str(event.end), 'location': event.location,
                   'description': event.description, 'attendees': str(event.attendees)} for event in events]
    return json.dumps(result)


def get_all_calendar_events():

    def event_str(calendar_no, event):
        start = str(event.start).split("+")[0]
        if start.endswith(':00'): start = start[:-3]
        end = str(event.end).split("+")[0]
        if end.endswith(':00'): end = end[:-3]
        if end[:10] == start[:10]: end = end[11:]
        result = f'{calendar_no} {event.id} -> {start}'
        if end:
            result += '-' + end
        result += f' {event.summary}'
        if event.location: result += ' at ' + event.location.replace('\n',' ').replace(', Netherlands','').replace(', Nederland','')
        if event.description: result += ' (' + event.description[:100].replace('\n',' ') + ')'
        attendees = [a for a in event.attendees if a.display_name and a.display_name != 'Hans-Peter Harmsen'] if event.attendees else []
        if attendees: result += ' with ' + ','.join([str(attendee.display_name) for attendee in attendees])
        return result

    result = ''
    for key, val in CALENDARS.items():
        cal = get_calendar(val)
        events = cal.get_events(time_max=datetime.now() + timedelta(days=180), order_by="startTime", single_events=True)
        result += '\n'.join([event_str(key, event) for event in events])

    return result


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


def update_calendar_event(calendar_no, event_id, summary=None, start=None, end=None, location=None, description=None, attendees=None):
    calendar_id = CALENDARS[int(calendar_no)]
    cal = get_calendar(calendar_id)
    event = cal.get_event(event_id)
    if summary: event.summary = summary
    if start: event.start = start
    if end: event.end = end
    if location: event.location = location
    if description: event.description = description
    if attendees: event.attendees = attendees
    cal.update_event(event)
    return 'OK!'


def get_calendar(calendar_id):
    return GoogleCalendar(calendar_id, credentials_path="client_secret_573107433733-cr8pq51ig2f9n3i6aueevvj0tp9kskbb.apps.googleusercontent.com.json")
