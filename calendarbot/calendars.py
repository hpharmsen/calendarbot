# https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import dateparser
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar


class Calendars:
    def __init__(self):
        self.calendars = {}
        client_secret = {
            "installed": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "project_id": "calendarbot-408822",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "redirect_uris": ["http://localhost"]
            }
        }
        client_secret_file = Path(__file__).parent / 'client_secret.json'
        with open(client_secret_file, 'w') as f:
            json.dump(client_secret, f)
        for i in range(1, 10):
            calendar_id = os.environ.get(f'GOOGLE_CALENDAR_{i}')
            if calendar_id:
                self.calendars[str(i)] = GoogleCalendar(calendar_id, credentials_path=str(client_secret_file))
        os.remove(client_secret_file)

    def __getitem__(self, item):
        return self.calendars[item]

    def get_event(self, time_min=None, time_max=None, query=None):
        result = []
        for cal in self.calendars.values():
            if time_min:
                time_min = datetime.fromisoformat(time_min)
            if time_max:
                time_max = datetime.fromisoformat(time_max)
            events = cal.get_events(time_min, time_max, query=query, order_by="startTime", single_events=True)
            result += [{'summary': event.summary, 'start': str(event.start), 'end': str(event.end),
                        'location': event.location, 'description': event.description, 'attendees': str(event.attendees)}
                       for event in events]
        return json.dumps(result)

    def get_all_events(self):
        # return test_data()
        def event_str(calendar_no, event):
            start = str(event.start).split("+")[0]
            if start.endswith(':00'):
                start = start[:-3]
            end = str(event.end).split("+")[0]
            if end.endswith(':00'):
                end = end[:-3]
            if end[:10] == start[:10]:
                end = end[11:]
            result = f'{calendar_no} {event.id} -> {start}'
            if end:
                result += ' - ' + end
            result += f' {event.summary}'
            if event.location:
                result += ' at ' + event.location.replace('\n', ' ').replace(', Netherlands', '')
            if event.description:
                result += ' (' + event.description[:100].replace('\n', ' ') + ')'
            attendees = [a for a in event.attendees if a.display_name and a.display_name != 'Hans-Peter Harmsen'] \
                if event.attendees else []
            if attendees:
                result += ' with ' + ','.join([str(attendee.display_name) for attendee in attendees])
            return result

        time_max = datetime.now() + timedelta(days=180)
        result = ''
        for number, cal in self.calendars.items():
            events = cal.get_events(time_max=time_max, order_by="startTime", single_events=True)
            result += '\n'.join([event_str(number, event) for event in events])

        return result

    def create_event(self, event: dict):
        start_date = dateparser.parse(event['start'])
        end_date = dateparser.parse(event['end']) if event['end'] else start_date + timedelta(hours=1)
        cal = self.calendars[str(event.get('calendar_no', 1))]
        cal_event = Event(event['summary'], start_date, end_date, location=event['location'],
                          description=event['description'])
        res = cal.add_event(cal_event)
        return res

    def update_event(self, event: dict):
        cal = self.calendars[str(event.get('calendar_no', 1))]
        cal_event = cal.get_event(event['event_id'])
        if event.get('summary'):
            cal_event.summary = event['summary']
        if event.get('start'):
            cal_event.start = dateparser.parse(event['start'])
        if event.get('end'):
            cal_event.end = dateparser.parse(event['end'])
        if event.get('location'):
            cal_event.location = event['location']
        if event.get('description'):
            cal_event.description = event['description']
        res = cal.update_event(cal_event)
        return res

    def delete_event(self, event: dict):
        cal = self.calendars[str(event.get('calendar_no', 1))]
        cal_event = cal.get_event(event['event_id'])
        res = cal.delete_event(cal_event)
        return res


def test_data():
    return """1 604h3u3pihubi7qd7g7rlhpk6f_20231224T153000Z -> 2023-12-24 16:30 - 17:20 DMO-HPH-MLL
1 1ph3k4t63ocnnku8q1mq78u355 -> 2023-12-30 - 2023-12-31 A10 afgesloten
1 604h3u3pihubi7qd7g7rlhpk6f_20231231T153000Z -> 2023-12-31 16:30 - 17:20 DMO-HPH-MLL
1 237s9ngtki8ai1d88piva6j7cm -> 2024-01-03 - 2024-01-04 Renco golf
1 0ls5l361p8v0usb5j4lse5bhq9_20240104T064500Z -> 2024-01-04 07:45 - 10:45 Business Open
1 4eie2u6u0obtuerrp6690dvot5 -> 2024-01-06 19:30 - 22:15 Quick Nieuwjaarsreceptie en pubquiz
1 6430ekjivo3e4cdak8rkqe48n7_20240107 -> 2024-01-07 - 2024-01-08 Martijn jarig
1 604h3u3pihubi7qd7g7rlhpk6f_20240107T153000Z -> 2024-01-07 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240108T183000Z -> 2024-01-08 19:30 - 21:00 Spaans Sesiones de Conversacion
1 6scic0e035l4kprtgedded1lqm -> 2024-01-11 16:00 - 20:00 BO reunie at Tribes Amsterdam Amstel Station, 
1 _c8qm2e9i6gom4 -> 2024-01-11 16:00 - 20:00 Event op 7 jarig Jubileum De Amsterdamse
1 9ndlki7adtat74je9ug6mjk5o0 -> 2024-01-12 - 2024-01-15 Gent
1 604h3u3pihubi7qd7g7rlhpk6f_20240114T153000Z -> 2024-01-14 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240115T190000Z -> 2024-01-15 20:00 - 21:30 Spaans Les 
1 0ls5l361p8v0usb5j4lse5bhq9_20240118T064500Z -> 2024-01-18 07:45 - 10:45 Business Open
1 03oq9ruk7nr11v1qnda11v79ag_20240120T100000Z -> 2024-01-20 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240121T153000Z -> 2024-01-21 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240122T183000Z -> 2024-01-22 19:30 - 21:00 Spaans Sesiones de Conversacion
1 5ae3k36cp1pvvgohn85mjdekk5 -> 2024-01-24 15:30 - 19:30 Marktlink Meet the Manager event at Inn Style, Maarssen
1 03oq9ruk7nr11v1qnda11v79ag_20240127T100000Z -> 2024-01-27 11:00 - 12:30 Softbaltraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240128T153000Z -> 2024-01-28 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240129T190000Z -> 2024-01-29 20:00 - 21:30 Spaans Les 
1 k5e2urvp3p38fc3ld3hd23glr0 -> 2024-02-01 - 2024-02-02 Marktlink AI event (Noor belt me, €1500)
1 0ls5l361p8v0usb5j4lse5bhq9_20240201T064500Z -> 2024-02-01 07:45 - 10:45 Business Open
1 2jvkvg4eprn01hurmsmer1jrqc_20240202 -> 2024-02-02 - 2024-02-03 Jarig
1 03oq9ruk7nr11v1qnda11v79ag_20240203T100000Z -> 2024-02-03 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240204T153000Z -> 2024-02-04 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240205T183000Z -> 2024-02-05 19:30 - 21:00 Spaans Sesiones de Conversacion
1 03oq9ruk7nr11v1qnda11v79ag_20240210T100000Z -> 2024-02-10 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 59mm6m4kgp1tlhbbr3dcthge96_20240211 -> 2024-02-11 - 2024-02-12 Joost Comperen jarig
1 604h3u3pihubi7qd7g7rlhpk6f_20240211T153000Z -> 2024-02-11 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240212T190000Z -> 2024-02-12 20:00 - 21:30 Spaans Les 
1 0ls5l361p8v0usb5j4lse5bhq9_20240215T064500Z -> 2024-02-15 07:45 - 10:45 Business Open
1 03oq9ruk7nr11v1qnda11v79ag_20240217T100000Z -> 2024-02-17 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240218T153000Z -> 2024-02-18 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240219T183000Z -> 2024-02-19 19:30 - 21:00 Spaans Sesiones de Conversacion
1 03oq9ruk7nr11v1qnda11v79ag_20240224T100000Z -> 2024-02-24 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240225T153000Z -> 2024-02-25 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240226T190000Z -> 2024-02-26 20:00 - 21:30 Spaans Les 
1 0ls5l361p8v0usb5j4lse5bhq9_20240229T064500Z -> 2024-02-29 07:45 - 10:45 Business Open
1 03oq9ruk7nr11v1qnda11v79ag_20240302T100000Z -> 2024-03-02 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 02lg5vh5anhq9b4vd47qj9pf2v -> 2024-03-03 - 2024-03-04 Marije en JW 12,5jr
1 604h3u3pihubi7qd7g7rlhpk6f_20240303T153000Z -> 2024-03-03 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240304T183000Z -> 2024-03-04 19:30 - 21:00 Spaans Sesiones de Conversacion
1 0pke4gk0g0as3akt8173608r2i_20240308 -> 2024-03-08 - 2024-03-09 Linda van Zomeren jarig
1 03oq9ruk7nr11v1qnda11v79ag_20240309T100000Z -> 2024-03-09 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240310T153000Z -> 2024-03-10 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240311T190000Z -> 2024-03-11 20:00 - 21:30 Spaans Les 
1 06g15l4ptsbm5g6jeb304p7vak_20240312 -> 2024-03-12 - 2024-03-13 Paulien jarig
1 45rnvbkkqba8bu8svebtb61dll_20240314 -> 2024-03-14 - 2024-03-15 Hans Drenth jarig
1 0ls5l361p8v0usb5j4lse5bhq9_20240314T064500Z -> 2024-03-14 07:45 - 10:45 Business Open
1 646bjmaishvajlttmfie49h73c -> 2024-03-15 14:30 - 21:00 Halfjaarlijks Funders event Rotterdam Factoring 
1 03oq9ruk7nr11v1qnda11v79ag_20240316T100000Z -> 2024-03-16 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240317T153000Z -> 2024-03-17 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240318T183000Z -> 2024-03-18 19:30 - 21:00 Spaans Sesiones de Conversacion
1 49qg2jio12lngdqfh7pmtqjoav -> 2024-03-22 - 2024-03-23 ALV Quick
1 03oq9ruk7nr11v1qnda11v79ag_20240323T100000Z -> 2024-03-23 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 604h3u3pihubi7qd7g7rlhpk6f_20240324T153000Z -> 2024-03-24 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240325T190000Z -> 2024-03-25 20:00 - 21:30 Spaans Les 
1 0ls5l361p8v0usb5j4lse5bhq9_20240328T064500Z -> 2024-03-28 07:45 - 10:45 Business Open
1 03oq9ruk7nr11v1qnda11v79ag_20240330T100000Z -> 2024-03-30 11:00 - 12:30 Softbalttraining at Calandhal, Amsterdam
1 3mt833ivkggtvmfi1j452o02st -> 2024-06-07 - 2024-06-10 MLB weekend Londen
1 604h3u3pihubi7qd7g7rlhpk6f_20240609T143000Z -> 2024-06-09 16:30 - 17:20 DMO-HPH-MLL
1 cc35n86t9or6dnqudcb1rt2f0c_20240610T173000Z -> 2024-06-10 19:30 - 21:00 Spaans Sesiones de Conversacion
1 604h3u3pihubi7qd7g7rlhpk6f_20240616T143000Z -> 2024-06-16 16:30 - 17:20 DMO-HPH-MLL
1 tqojl68e3a8751svqoomtiqpb2_20240617T180000Z -> 2024-06-17 20:00 - 21:30 Spaans Les 
1 0ls5l361p8v0usb5j4lse5bhq9_20240620T054500Z -> 2024-06-20 07:45 - 10:45 Business Open2 
2 88lu657r29ouutcvnr1qjvp724 -> 2023-12-25 16:00 - 22:00 Kerst bij Annelies
2 b49mv0reuh2qro9aifbi5phn54 -> 2023-12-26 16:00 - 23:00 Kerst in Breda
2 jvipg03266dtkpbmf9n4uc3tio -> 2023-12-29 17:30 - 22:30 Marcel en Lenny bij ons at Windjammerdijk 14
2 7ig5c5lo5bbbqph1g9poo7h1kr_20240617 -> 2024-06-17 - 2024-06-18 Lenny jarig ('68)"""