# CFPDB -- A _Call for Papers_ Database for collaborative use
A Call for Papers database which sorts confs and highlights due dates according to the current date, intended for collaborative use

The calendar is located at: https://dlazesz.github.io/cfpdb/

The _iCalendar_ format is located at: https://raw.githubusercontent.com/dlazesz/cfpdb/gh-pages/conferences.ics


## Usage

1) Edit [conferences.yaml in the conferences branch of this repository](https://github.com/dlazesz/cfpdb/blob/conferences/conferences.yaml)
2) Wait till 01:00 CET for the calendar to refresh
3) View the calendar at: https://dlazesz.github.io/cfpdb/

## Setup

There are multiple ways to setup your own instance:

- Run the program in cron: HOME=$HOME $HOME/cfpbd/run_update_in_venv.py >> $HOME/cfpbd/update.log 2>&1
- Run the program in virtualenv: run_update_in_venv.py
- Run the program manually and push the changes: update_cfpdb_on_github.py
- Run the program manually to see the changes locally: generate_html.py
- Run the program on Heroku: clock.py

1. Setup key-based access to github. Copy private key to private_key file
2. Set the proper github repository name in: update_cfpdb_on_github.py
3. Setup scheduled task eg. in cron

## Install to Heroku

  - Register
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
- _conferences_: stores _conferences.yaml_ that stores the conference data. Meant to be edited by the collaborators
- _gh-pages_: stores the rendered html file for the calendar to be shown as https://USERNAME.github.io/REPONAME

When the updater process runs, it fetches `conferences.yaml` from the _conferences_ branch in this repository and pushes the rendered html to _gh-pages_ branch

## New features

- iCalendar file (.ics) generation which can be subscribed to

## History
Code written between Nov 2008 and Nov 2010 by Bálint Sass

Full rewrite in 2019 Jan by Balázs Indig

## Acknowledgement

The Author would like to express his sincere gratitude for Bálint Sass for open sourcing the original program and enabling others to use and develop it further and keep this nice idea rocking!

## License

This program is licensed under the LGPL 3.0 license.
