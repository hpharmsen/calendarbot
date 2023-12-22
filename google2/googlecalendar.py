try:
    import unzip_requirements
except ImportError:
    pass
except FileNotFoundError:
    pass

import datetime
import os
from pathlib import Path

import pytz
#from . import googleauth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def parse_date(fullstring):
    if fullstring.count("T"):
        # 31T14:00:00+01:00
        datestring, timestring = fullstring.split("T")
    elif fullstring.count(" "):
        datestring, timestring = fullstring.split()
    else:
        datestring = fullstring
        timestring = ""

    y, m, d = datestring.split()[0].split("-")

    if timestring:
        H, M = timestring.split(":", 1)
        if M.count(":"):
            M = M.split(":")[0]
        return datetime.datetime(
            year=int(y), month=int(m), day=int(d), hour=int(H), minute=int(M)
        )
    return datetime.datetime(year=int(y), month=int(m), day=int(d))


class GoogleCalendar:
    def __init__(self):
        # Get an analytics service object.
        #self.service = googleauth.initialize_service("calendar")
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        script_dir = Path(__file__).parent
        creds = Credentials.from_authorized_user_file(script_dir / 'token.json', SCOPES)
        self.service = build('calendar', 'v3', credentials=creds)
        self._calendarId = None

    def setCalendar(self, calendarId):
        self._calendarId = calendarId

    def listCalendars(self):
        page_token = None
        calendars = []
        while True:
            calendar_list = (
                self.service.calendarList().list(pageToken=page_token).execute()
            )
            calendars += [
                {"id": c["id"], "name": c["summary"]} for c in calendar_list["items"]
            ]
            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break
        return calendars

    def getCalendarByName(self, name):
        for c in self.listCalendars():
            if c["name"] == name:
                return c["id"]
        return None

    def setCalendarByName(self, name):
        self.setCalendar(self.getCalendarByName(name))

    def listEvents(
        self, q="", calendarId=None, maxResults=250, timeMin=None, timeMax=None
    ):
        if not calendarId:
            calendarId = self._calendarId
        events = []
        page_token = ""
        while True:
            if page_token:
                event_list = (
                    self.service.events()
                    .list(
                        q=q,
                        calendarId=calendarId,
                        timeMin=timeMin,
                        timeMax=timeMax,
                        singleEvents="True",
                        orderBy="startTime",
                        maxResults=maxResults,
                        pageToken=page_token,
                    )
                    .execute()
                )
            else:
                event_list = (
                    self.service.events()
                    .list(
                        q=q,
                        calendarId=calendarId,
                        timeMin=timeMin,
                        timeMax=timeMax,
                        singleEvents="True",
                        orderBy="startTime",
                        maxResults=maxResults,
                    )
                    .execute()
                )
            events += event_list["items"]
            if len(events) >= maxResults:
                break
            page_token = event_list.get("nextPageToken")
            # print page_token
            if not page_token:
                break
        return [simplifyEvent(c) for c in events]

    def findEvent(self, summary, startdate, calendarId=None):
        events = self.listEvents(summary, calendarId)
        for event in events:
            if (
                dateStr(event["start"]) == startdate.split("T")[0]
            ):  # Hier wordt het wel erg hackerig.
                return event
        return False

    def findEventsOnDay(self, day, calendarId=None):
        timeMin = day.astimezone().isoformat()
        timeMax = timeMin.replace("T00:00:00", "T23:59:59")
        events = self.listEvents("", calendarId, timeMin=timeMin, timeMax=timeMax)
        # events = [event for event in events if dateStr(event['start'])==day.strftime('%Y-%m-%d')]
        return events

    def _createEventData(
        self, summary, description="", start_time=None, end_time=None, location=""
    ):
        fullday = 0
        if start_time:
            start_time = parse_date(start_time)
            if start_time.hour == 0 and start_time.minute == 0:
                fullday = 1
        else:
            # Use current time for the start_time
            start_time = datetime.datetime.now()
        if end_time:
            end_time = parse_date(end_time)
        else:
            if fullday:
                end_time = start_time + datetime.timedelta(days=1)
            else:
                end_time = start_time + datetime.timedelta(hours=1)

        eventdata = {
            "summary": summary,
            "description": description,
            "location": location,
        }
        if fullday:
            eventdata["start"] = {"date": dateStr(start_time)}
            eventdata["end"] = {"date": dateStr(end_time)}
        else:
            eventdata["start"] = {"dateTime": timeStr(start_time)}
            eventdata["end"] = {"dateTime": timeStr(end_time)}

        return eventdata

    def insertEvent(
        self, summary, description="", start_time=None, end_time=None, location=""
    ):
        # Onderstaande check is om te zorgen dat events niet dubbel in de agenda komen
        eventdata = self._createEventData(
            summary, description, start_time, end_time, location
        )
        # try:
        #     d = eventdata["start"]["date"]
        # except:
        #     d = eventdata["start"]["dateTime"]
        #if self.findEvent(summary, d):
        #    print(start_time, summary, "Already existent")
        #    return

        event = (
            self.service.events()
            .insert(calendarId=self._calendarId, body=eventdata)
            .execute()
        )
        return simplifyEvent(event)

    def updateEvent(
        self,
        eventId,
        summary,
        description="",
        start_time=None,
        end_time=None,
        location="",
    ):
        eventdata = self._createEventData(
            summary, description, start_time, end_time, location
        )
        event = (
            self.service.events()
            .update(calendarId=self._calendarId, eventId=eventId, body=eventdata)
            .execute()
        )
        return simplifyEvent(event)

    def deleteEvent(self, id):
        try:
            self.service.events().delete(
                calendarId=self._calendarId, eventId=id
            ).execute()
        except:
            try:  # Probeer nog een keer
                self.service.events().delete(
                    calendarId=self._calendarId, eventId=id
                ).execute()
            except:
                print("could not delete event", id)
                pass  # Ok, dan niet. Is waarschijnlijk al verwijderd


def simplifyEvent(event):
    if event["start"].get("dateTime"):
        return {
            "id": event["id"],
            "start": parse_date(event["start"]["dateTime"]),
            "end": parse_date(event["end"]["dateTime"]),
            "summary": event["summary"],
            "fullday": 0,
        }
    else:
        return {
            "id": event["id"],
            "start": parse_date(event["start"]["date"]),
            "end": parse_date(event["end"]["date"]),
            "summary": event["summary"],
            "fullday": 1,
        }


def timeStr(dt):
    return (
        pytz.timezone("Europe/Amsterdam").localize(dt).strftime("%Y-%m-%dT%H:%M:%S%z")
    )


def dateStr(dt):
    return dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    # test code
    cal = GoogleCalendar()
    print('CALENDARS', cal.listCalendars())
    hp = cal.getCalendarByName("HP")
    cal.setCalendar(hp)
    print('EVENTS')
    print(cal.listEvents(hp, 10))
    print( 'INSERT ')
    print(cal.insertEvent("testevent"))
