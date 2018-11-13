#!/bin/bash

if [[ -z "$API_KEY" || -z "$DOMAIN" || -z "$EMAIL" ]]
then
    echo "incomplete configuration, nothing sent" >&2
    exit 1
fi

ITEMS=$(cat)
SUBJECT=$(date +'%A Standup (%F)')

if [[ -n "$ITEMS" ]]
then
    NL=$'\n\n'
    curl -s --user "api:${API_KEY}" \
        "https://api.mailgun.net/v3/${DOMAIN}/messages" \
        -F from="Tasks <tasks@${DOMAIN}>" \
        -F to="$EMAIL" \
        -F subject="$SUBJECT" \
        -F text="Here is your daily standup!${NL}${ITEMS}"
        > /dev/null
fi
