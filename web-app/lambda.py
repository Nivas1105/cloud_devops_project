import os
import json
import urllib3
http = urllib3.PoolManager()

def lambda_handler(event, context):
    CORS_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,GET' 
    }

    request_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if request_method == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': '' 
        }

    print("Handling GET request...")
    try:
        API_KEY = os.environ.get('WEATHER_API_KEY')
        if not API_KEY:
            raise ValueError("API key is not configured in environment variables.")
        url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q=Dallas&days=3"
        response = http.request('GET', url)
        weather_data = json.loads(response.data.decode('utf-8'))

        if response.status != 200:
            print(f"Error from WeatherAPI: Status {response.status}")
            raise Exception("Failed to fetch data from WeatherAPI.")

        print("Successfully fetched weather data.")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(weather_data)
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'An internal server error occurred.'})
        }