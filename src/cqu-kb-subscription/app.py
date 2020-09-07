from pathlib import Path

from cqu_kb.__main__ import server_main
from flask import Flask, send_from_directory

app = Flask(__name__)

base_dir = Path("--enter-path-here--")


@app.route('/<username>/<password>')
def get_ical(username, password):
    path = base_dir / f'{username}.ics'
    server_main(username, password, path)

    return send_from_directory(
        directory=base_dir.absolute(),
        filename=f'{username}.ics',
        mimetype='text/calendar',
        as_attachment=True,
        attachment_filename=f'{username}.ics'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
