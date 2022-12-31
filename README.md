# CFPDB -- A _Call for Papers_ Database for collaborative use
CFPDB is a Call for Papers database which sorts conferences and highlights due dates according to the current date, intended for collaborative use.

The calendar is located at: https://dlazesz.github.io/cfpdb/

The _iCalendar_ format is located at: https://raw.githubusercontent.com/dlazesz/cfpdb/gh-pages/conferences.ics


## Usage

1) Edit [conferences.yaml in the _conferences_ branch of this repository](https://github.com/dlazesz/cfpdb/blob/conferences/conferences.yaml)
2) The calendar will be refreshed at 01:00 CET
3) Check the calendar at: https://dlazesz.github.io/cfpdb/ or subscribe to the following iCalendar file: https://raw.githubusercontent.com/dlazesz/cfpdb/gh-pages/conferences.ics

### Using the _iCalendar_ file with [Google Calendar](https://calendar.google.com)

1) Go to https://calendar.google.com
2) In the left menu select the three vertical dots on the left of _Add a friend's calendar_
3) Select _Add by URL_
4) Insert the URL of the provided ics file (see above) and click _Add calendar_ 

### Using the _iCalendar_ file with _Android_

1) Install [ICSX5](https://icsx5.bitfire.at/) from [Play store](https://play.google.com/store/apps/details?id=at.bitfire.icsdroid&hl=en_US), [Aurora store](https://f-droid.org/en/packages/com.aurora.store/) or [F-droid](https://f-droid.org/en/packages/at.bitfire.icsdroid/)
2) Add the URL of the provided ics file (see above)
3) Set name and color
4) Set update frequency if needed 

## Setup

1. [Setup the Personal Access Token-based access to Github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) enabling ```repo``` scopes (shortcut: https://github.com/settings/tokens/new watch out for expiration time!)
2. Set [the proper github repository name (the HTTP variant of the remote url)](https://help.github.com/articles/which-remote-url-should-i-use/), github username and the newly created token in `repo_config.yaml` ([see example](repo_config_example.yaml))
3. Setup a scheduled task to run the update:

    - Create a virtualenv and install the dependencies: `virtualenv venv && ./venv/bin/pip install -r requirements.txt`
    - Type `crontab -e` to create a scheduled task.
    - Type the following to run at 1:00 AM every day (see [crontab.guru](https://crontab.guru) for examples): `0 1 * * * HOME=$HOME $HOME/cfpdb/venv/bin/python $HOME/cfpdb/update_cfpdb_on_github.py >> $HOME/cfpdb/update.log 2>&1`
    - (Optional) Run the program manually and push the changes: [`update_cfpdb_on_github.py`](update_cfpdb_on_github.py)
    - (Optional) Run the program manually to see the changes locally: [`generate_calendar.py`](generate_calendar.py)
    - (Optional) Run the program on Heroku: [`clock.py`](clock.py)
    - (Optional) Run the program on [Deta Cloud](https://www.deta.sh/): [`deta_main.py`](deta_main.py)

## Install to Heroku

__WARNING: Heroku free tier is discontinued.__

  - Sign up
  - Download and install Heroku CLI
  - Login to Heroku from the CLI
  - Create an app
  - Clone the repository
  - Add Heroku as remote origin
  - Setup the program (see step 1 and 2)
  - Push the repository to Heroku
  - Start the scheduled task: `heroku ps:scale clock=1`
  - Enjoy!

## Architecture

There are three independent (orphan) branches in this repository:

- _master_: contains the program and the setup instructions
- _conferences_: contains _conferences.yaml_ which stores the conference data (it is meant to be edited by the collaborators)
- _gh-pages_: stores the rendered html file for the calendar to be shown as https://USERNAME.github.io/REPONAME

The updater process fetches `conferences.yaml` from the _conferences_ branch in this repository and pushes the rendered html to the _gh-pages_ branch.

## New features

- iCalendar file (.ics) generation which can be subscribed to (see description)

## History
Code written between Nov 2008 and Nov 2010 by Bálint Sass

Full revision in Jan 2019 by Balázs Indig

## Acknowledgement

I would like to express my gratitude to Bálint Sass for open sourcing the original program and enabling others to use and develop it.

## License

This program is licensed under the LGPL 3.0 license.
