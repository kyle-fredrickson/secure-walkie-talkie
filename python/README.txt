This program is run through main.py.

To run it navigate to the python folder, then run
    python3 main.py -d --login Alice --text -l, to listen as Alice for text without logging in.
    -d specifies no login, --login Alice specifies login as Alice, --text specifies that we're listening for text, and -l that we're listening.

To send Alice a message now that she's listening from the python folder, run
    python3 main.py -d --login Bob --text -t "message" Alice
    -t <message or file> <Recipient>
