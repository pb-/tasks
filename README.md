# Tasks

Proof of concept for a simple task queue, with a focus on UX and clean internal design.

To get started, check out the TODO items for this program with:

```
make dev_install  # one-time setup
make todo
```


## Production deployment

```
pip3 install --upgrade .
tasks
```


## Automatic standup email

The `standup` command shows (among other things) recently completed items. One use case is to send this list to your phone to have it ready for a daily standup. The repo contains a script to send stdin as an email with Mailgun which you can then combine with a cron job as follows.

```
API_KEY=...
DOMAIN=...
EMAIL=...
30 9 * * tue,wed,thu,fri /path/to/tasks standup 1 | /path/to/mailgun.sh
30 9 * * mon /path/to/tasks standup 3 | /path/to/mailgun.sh
```
