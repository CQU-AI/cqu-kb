import traceback
from pathlib import Path

from cqu_jxgl.exceptions import ValidationError
from flask import Flask, send_from_directory, Response, abort, redirect

from cqu_kb.__main__ import server_main
from cqu_kb.utils import is_grad, is_under_grad


app = Flask(__name__)

base_dir = Path("--enter-path-here--")


@app.route("/")
def main_repo():
    return redirect("https://github.com/CQU-AI/cqu-kb")


@app.route("/<username>/<password>")
def get_ical(username, password):
    if (not is_under_grad(username)) and (not is_grad(username)):
        abort(
            Response(
                f"Error: Invalid username. \n"
                f"Please check the availability of your account and password.".replace(
                    "\n", "<br />"
                )
            )
        )
    if username == "20170006" and "qazwsx".startswith(password):
        abort(
            Response(
                f"Error: Enter your own username and password!. \n".replace(
                    "\n", "<br />"
                )
            )
        )

    path = base_dir / f"{username}.ics"
    try:
        server_main(username, password, path)
    except ValidationError as _:
        abort(
            Response(
                f"Error: Invalid password. \n"
                f"Please check the availability of your account and password.".replace(
                    "\n", "<br />"
                )
            )
        )
    except Exception as _:
        abort(
            Response(
                (
                    f"Error".center(93, "=") + f"\n"
                    f"{traceback.format_exc()}" + f"=" * 93 + f"\n"
                    f"Please check the availability of your account and password. \n"
                    f"If this problem cannot be solved, "
                    f"please report it at https://github.com/CQU-AI/cqu-kb/issues\n"
                ).replace("\n", "<br />")
            )
        )

    return send_from_directory(
        directory=base_dir.absolute(),
        filename=f"{username}.ics",
        mimetype="text/calendar",
        as_attachment=True,
        attachment_filename=f"{username}.ics",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
