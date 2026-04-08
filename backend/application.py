"""
Elastic Beanstalk entry point for the Smart Campus Lost & Found backend.

Elastic Beanstalk's Python platform looks for an object named `application`
inside a module named `application.py` at the root of the deployment bundle.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

application = create_app(os.environ.get("FLASK_ENV", "production"))


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
