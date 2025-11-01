🌤️ Dallas Weather Dashboard
<p align="center">
  <img src="https://raw.githubusercontent.com/Nivas1105/cloud_devops_project/main/web-app/Arcitecture_Diagram_Web_App.png" alt="Architecture Diagram" width="700"/>
</p>

The Dallas Weather Dashboard is a secure, cloud-powered web application that visualizes real-time weather and forecast data for Dallas, Texas.
It integrates AWS Cognito for user authentication, Flask as the backend authentication proxy, API Gateway + AWS Lambda for weather data APIs, and a modern HTML dashboard for visualization.

🧭 Architecture Overview

User Interface (Frontend)

Hosted locally via http://localhost:8080/index.html

Displays live Dallas weather, hourly forecasts, and interactive temperature/humidity charts (using Plotly.js).

Automatically redirects to login if the user is not authenticated.

Authentication Layer (Flask + Cognito)

Flask app (http://localhost:5050) handles OAuth 2.0 flow with Amazon Cognito.

Users log in via Cognito’s Hosted UI.

Flask securely stores Cognito tokens in session and redirects users back to the dashboard.

Logout clears both local session and Cognito session.

Data Access Layer (API Gateway + Lambda)

The frontend fetches weather data from a protected AWS API Gateway endpoint.

API Gateway verifies user tokens using Cognito Authorizer.

Valid requests invoke a Lambda function that fetches weather data (e.g., from WeatherAPI).

Cognito Integration Flow

User clicks “Login with Cognito” → redirected to Cognito Hosted UI

After authentication, Cognito redirects to Flask /callback

Flask exchanges code for tokens → stores session → redirects to dashboard

Frontend requests data → validated by API Gateway → served by Lambda
