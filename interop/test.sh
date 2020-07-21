#!/bin/bash
MESSAGE="hello"

TALKER_CONFIG="../python/config/Bob.json"
LISTENER_CONFIG="../python/config/Alice.json"
RECIPIENT="Alice"

function test () {
    local talker=$1
    local listener=$2
    local talkerOut=$3
    local listenerOut=$4
    local message=$5

    touch $talkerOut
    touch $listenerOut

    local talkerVars="tvars.json"
    local listenerVars="lvars.json"
    echo "{}" > $talkerVars
    echo "{}" > $listenerVars

    # Talker sends message 1. Listener receives message 1.
    ./$talker $TALKER_CONFIG $RECIPIENT $message 1 $listenerOut $talkerOut $talkerVars
    ./$listener $LISTENER_CONFIG 1 $talkerOut $listenerOut $listenerVars

    # Listener sends message 2. Talker receives message 2.
    ./$listener $LISTENER_CONFIG 2 $talkerOut $listenerOut $listenerVars
    ./$talker $TALKER_CONFIG $RECIPIENT $message 2 $listenerOut $talkerOut $talkerVars

    # Talker sends message 3 and D. Listener receives message 3 and D.
    ./$talker $TALKER_CONFIG $RECIPIENT $message 3 $listenerOut $talkerOut $talkerVars
    local receivedMessage=$(./$listener $LISTENER_CONFIG 3 $talkerOut $listenerOut $listenerVars)

    #rm $talkerOut
    #rm $listenerOut
    #rm $talkerVars
    #rm $listenerVars

    if [ $message = $receivedMessage ]; then
        return 0
    else
        return 1
    fi
}

function main () {
    test $1 $2 $3 $4 $MESSAGE

    if [ $? -eq 0 ]; then
        echo "Test passed."
    else
        echo "Test failed."
    fi
}

[ "${BASH_SOURCE[0]}" == "${0}" ] && main "$@"