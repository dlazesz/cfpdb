#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys
import shutil
from pathlib import Path
from datetime import date

from yamale import make_schema, make_data, validate, YamaleError
from dulwich import porcelain

def load_and_validate(schema_fname, fname, strict=True):
    config_schema = make_schema(schema_fname)
    with open(fname, encoding='UTF-8') as data_fh:
        data_content = data_fh.read()
    data = make_data(content=data_content)
    try:
        validate(config_schema, data, strict)
    except YamaleError as e:
        for result in e.results:
            print('Error validating data {0} with {1}:'.format(result.data, result.schema), file=sys.stderr)
            for error in result.errors:
                print('', error, sep='\t', file=sys.stderr)
        exit(1)
    return data[0][0]

def run_update(work_dir, repo_url, username, token):
    # Compute absolute path for working dir for later use
    abs_work_dir = Path(work_dir).absolute()

    # Clean work_dir
    shutil.rmtree(abs_work_dir, ignore_errors=True)

    # Clone master: depth=1 and no-single-branch together as parameter to reduce bandwidth usage...
    repo = porcelain.clone(repo_url, abs_work_dir, depth=1, branch='conferences')

    # Go into the git working dir and also add it to modulepath!
    os.chdir(abs_work_dir)
    sys.path.append(str(abs_work_dir))

    # Create HTML from YAML file
    from generate_calendar import main as gen_html
    gen_html()

    # Checkout (remote) gh-pages branch
    porcelain.pull(repo, repo_url, refspecs='refs/heads/gh-pages')
    porcelain.update_head(repo, 'gh-pages')
    # These are unnecessary because we explicitly stage files
    # porcelain.reset(repo, 'hard')
    # os.remove('conferences.yaml')

    # Overwrite old HTML file
    os.rename('cfps.html', 'index.html')
    os.rename('cfps.ics', 'conferences.ics')

    # add result
    porcelain.add(repo, ['index.html', 'conferences.ics'])

    # The ics file generation is not reproducible so it does not count in the diff!
    if len(porcelain.status(repo, untracked_files='no')[0]['modify']) > 1:
        # commit result
        author = 'CFP Updater Bot <this.bot.h@s.no.email>'
        porcelain.commit(repo, f'Update on {date.today().isoformat()}', author=author, committer=author)
        # push result
        porcelain.push(repo, repo_url, 'gh-pages', username=username, password=token)
        print('Pushed!')
    else:
        print('Nothing to commit')


if __name__ == '__main__':
    repo_config = load_and_validate(Path(__file__).parent / 'repo_config_schema.yaml',
                                    Path(__file__).parent / 'repo_config.yaml')
    run_update(repo_config['work_dir'], repo_config['repo_url'], repo_config['username'], repo_config['token'])
