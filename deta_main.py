from pathlib import Path

from update_cfpdb_on_github import load_and_validate, run_update

from deta import app

# define a function to run on a schedule
# the function must take an event as an argument
@app.lib.cron()
def cron_job(event):
    repo_config = load_and_validate(Path(__file__).parent / 'repo_config_schema.yaml',
                                    Path(__file__).parent / 'repo_config.yaml')
    run_update(repo_config['work_dir'], repo_config['repo_url'], repo_config['username'], repo_config['token'])
