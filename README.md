# Bike Angels Routing Algorithm

This repository contains a Python program using the Streamlit library for routing optimization of Bike Angels in NYC. It uses dynamic programming and the real-time data API of Bike Angels to suggest the optimal route based on points scored and maximum cycling time. 

STILL IN DEVELOPMENT

## Main Function

The primary calling function of the program is `main.py`, which integrates various modules to provide the functionality of the app. It fetches the real-time data of the Bike Angels stations in NYC and provides a user interface for inputting the start and end stations and the maximum cycling time. It then processes the data and calls the dynamic programming function to suggest the optimal route.

## Prerequisites

This program requires the following Python libraries:

- requests
- pandas
- streamlit
- json

Please ensure these are installed in your Python environment.

## Running the Program

You can run the program by calling Streamlit with the main file:

```
streamlit run main.py
```

The program will launch a new web page where you can interact with the program. 

## Using the App

Once the app is running:

1. Select your starting and ending stations from the dropdown menus.
2. Use the slider to set your maximum cycling time.
3. Click "Submit".

The app will then display the optimal route between the chosen stations within the selected cycling time, along with the expected cycling times, points to be earned, and a map showing the route.

## Notes

This program is set to filter out stations outside of a predefined boundary in NYC and those that are not currently accepting returns or rentals. If a station is not appearing, ensure it is within the active region and is currently operational. 

Also, ensure that your start station is a "take" or "neutral" status station, and your end station is a "give" or "neutral" status station. Stations with incompatible statuses will return an error.
