import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


HTTP_TIMEOUT = (5, 20)


def create_weather_session():
    session = requests.Session()
    session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET",),
            )
        ),
    )
    return session


weather_session = create_weather_session()


def fetch_weather_data(app_id, lat, lon, session=weather_session):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    response = session.get(
        url,
        params={
            "lat": lat,
            "lon": lon,
            "appid": app_id,
            "units": "metric",
            "lang": "de",
        },
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
