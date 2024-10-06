import requests


def get_coordinates(address, api_key):
    """
    Get latitude and longitude of a given address using Google Maps Geocoding API.

    Parameters:
    - address (str): The address to geocode.
    - api_key (str): Your Google Maps Geocoding API key.

    Returns:
    - tuple: (latitude, longitude) if the address is found.
    - None: If the address is not found or an error occurs.
    """
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    # Prepare the parameters for the request
    params = {
        'address': address,
        'key': api_key
    }

    try:
        # Send the GET request to the Google Maps Geocoding API
        response = requests.get(geocode_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Check if the geocoding was successful
        if data['status'] == 'OK':
            # Extract latitude and longitude
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return latitude, longitude
        else:
            print(f"Geocoding API error: {data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle any requests exceptions (e.g., network errors)
        print(f"HTTP request failed: {e}")
        return None



