================================================================================
Smart Campus Lost & Found System
Author: Vikas Reddy Amanagantti (x25178849)
National College of Ireland -- Cloud Platform Programming -- Semester 2, 2026
================================================================================

PROJECT OVERVIEW
----------------
A cloud-native web application for managing lost and found items on a university
campus. The system enables users to report lost/found items, automatically
matches them using text similarity and image recognition, manages claims through
a verification workflow, and sends notifications when matches are detected.

CLOUD SERVICES USED (6)
------------------------
1. Amazon DynamoDB    -- NoSQL database for items, claims, users, matches
2. Amazon S3          -- Object storage for item images
3. Amazon Rekognition -- Image-based item matching and label detection
4. Amazon SNS         -- Push notifications for matches and claim updates
5. Amazon CloudWatch  -- Application monitoring, metrics, and logging
6. AWS Lambda         -- Asynchronous image processing and match detection

All services run in MOCK MODE by default (USE_AWS=False), so the application
works locally without AWS credentials.

DIRECTORY STRUCTURE
-------------------
Vikas/
  backend/         -- Flask REST API (Python)
  frontend/        -- React single-page application
  campusfinder/    -- Custom Python OOP library (pip installable)
  report/          -- IEEE LaTeX report and architecture diagram generator
  .github/         -- GitHub Actions CI/CD workflow

PREREQUISITES
-------------
- Python 3.9 or later
- Node.js 18 or later
- pip (Python package manager)
- npm (Node.js package manager)

BACKEND SETUP
-------------
1. Navigate to the backend directory:
       cd Vikas/backend

2. Create and activate a virtual environment (recommended):
       python -m venv venv
       source venv/bin/activate        # macOS/Linux
       venv\Scripts\activate           # Windows

3. Install Python dependencies:
       pip install -r requirements.txt

4. Install the custom library:
       pip install -e ../campusfinder

5. Start the Flask development server on port 5001:
       python app.py

   The API will be available at http://localhost:5001

FRONTEND SETUP
--------------
1. Navigate to the frontend directory:
       cd Vikas/frontend

2. Install Node.js dependencies:
       npm install

3. Start the development server on port 3001:
       npm start

   The app will be available at http://localhost:3001

RUNNING TESTS
-------------
Backend tests (from Vikas/backend):
    pytest tests/ -v

Library tests (from Vikas/campusfinder):
    pytest tests/ -v

CUSTOM LIBRARY -- campusfinder
------------------------------
Install in editable mode:
    cd Vikas/campusfinder
    pip install -e .

Classes provided:
    - ItemMatcher          : text similarity, fuzzy matching, category/colour matching
    - LocationTracker      : campus zone management, proximity calculation
    - ClaimProcessor       : claim verification workflow, priority scoring
    - NotificationManager  : notification rules engine, batching, urgency levels
    - Analytics            : recovery rates, hotspot analysis, trend detection

GENERATING THE ARCHITECTURE DIAGRAM
------------------------------------
    cd Vikas/report
    python architecture.py
    # Output: architecture.png

COMPILING THE IEEE REPORT
-------------------------
    cd Vikas/report
    pdflatex main.tex
    pdflatex main.tex   # run twice for references

API ENDPOINTS
-------------
Health check:
    GET  /
    GET  /api/health

Items (full CRUD):
    GET    /api/items              -- List all items (filter: ?type=lost&category=electronics)
    GET    /api/items/<id>         -- Get item by ID
    POST   /api/items             -- Create item
    PUT    /api/items/<id>         -- Update item
    DELETE /api/items/<id>         -- Delete item
    GET    /api/items/stats        -- Item statistics

Claims (full CRUD):
    GET    /api/claims             -- List all claims
    GET    /api/claims/<id>        -- Get claim by ID
    POST   /api/claims            -- Create claim
    PUT    /api/claims/<id>        -- Update claim
    DELETE /api/claims/<id>        -- Delete claim

Users (full CRUD):
    GET    /api/users              -- List all users
    GET    /api/users/<id>         -- Get user by ID
    POST   /api/users             -- Create user
    PUT    /api/users/<id>         -- Update user
    DELETE /api/users/<id>         -- Delete user

Matches (full CRUD):
    GET    /api/matches            -- List all matches
    GET    /api/matches/<id>       -- Get match by ID
    POST   /api/matches           -- Create match
    PUT    /api/matches/<id>       -- Update match
    DELETE /api/matches/<id>       -- Delete match

AWS Service endpoints:
    GET    /api/aws/status         -- All service statuses
    POST   /api/aws/upload-image   -- Upload image to S3
    POST   /api/aws/analyse-image  -- Run Rekognition analysis
    POST   /api/aws/trigger-match  -- Invoke Lambda match detection
    GET    /api/aws/notifications  -- View sent notifications
    GET    /api/aws/metrics        -- View CloudWatch metrics
    GET    /api/aws/logs           -- View CloudWatch logs

ENVIRONMENT VARIABLES
---------------------
FLASK_ENV          -- development | testing | production (default: development)
USE_AWS            -- True | False (default: False)
AWS_REGION         -- AWS region (default: eu-west-1)
S3_BUCKET          -- S3 bucket name
SNS_TOPIC_ARN      -- SNS topic ARN
LAMBDA_FUNCTION_NAME -- Lambda function name
SECRET_KEY         -- Flask secret key

CI/CD
-----
The GitHub Actions workflow (.github/workflows/deploy.yml) runs on every push
to main and on pull requests. It executes three jobs sequentially:
1. Test the campusfinder library
2. Test the Flask backend
3. Build the React frontend
================================================================================
