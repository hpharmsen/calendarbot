#!/usr/bin/python
try:
    import unzip_requirements
except ImportError:
    pass
except FileNotFoundError:
    pass

import sys, os
import httplib2  # easy_install httplib2
from apiclient.discovery import build  # easy_install google-api-python-client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

# from oauth2client.tools import run
from oauth2client import tools

# ADD NEW SERVICES HERE
scopeUrls = {
    "calendar": "https://www.googleapis.com/auth/calendar",
    "spreadsheets": "https://spreadsheets.google.com/feeds",
    "analytics": "https://www.googleapis.com/auth/analytics.readonly",
}

scriptdir = os.path.abspath(os.path.split(sys.argv[0])[0])


def initialize_service(service):

    # 1. We first try to retrieve stored credentials.
    #    If none are found then run the Auth Flow.

    # Retrieve existing credendials
    storage = Storage(
        os.path.join(scriptdir, os.path.join("google", service + ".dat"))
    )  # Token will be stored in this file
    credentials = storage.get()

    # If existing credentials are invalid and Run Auth flow
    # the run method will store any new credentials
    if credentials is None or credentials.invalid:
        # The Flow object to be used if we need to authenticate
        scope = scopeUrls.get(service)
        if not scope:
            print("Service % is not yet known. Please add it")
            sys.exit(1)
        # client_secrets.json contains OAuth 2.0 Client details for authentication and authorization.
        FLOW = flow_from_clientsecrets(
            os.path.join(scriptdir, "client_secrets.json"),
            scope=scope,
            message="client_secrets.json is missing",
        )
        # credentials = run(FLOW, storage) #run Auth Flow and store credentials
        credentials = tools.run_flow(
            FLOW, storage
        )  # run Auth Flow and store credentials

    # 2. authorize the http object
    http = credentials.authorize(httplib2.Http())

    # 3. Build the calendar Service Object with the authorized http object
    if service == "spreadsheets":
        return build("drive", "v2", http=http)
    else:
        return build(service, "v3", http=http)


if __name__ == "__main__":
    service = initialize_service("calendar")
