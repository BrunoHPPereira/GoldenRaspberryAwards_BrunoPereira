# Golden Raspberry Awards API

This project provides a RESTful API to analyze the Golden Raspberry Awards (Razzies) data, specifically focusing on producers with the longest and shortest intervals between consecutive Worst Film awards.

## Requirements

- Python 3.8 or higher
- pip (Python package manager)


## Project Structure

```
backend/
├── app.py              # Main Flask application
├── tests.py            # Integration tests
├── requirements.txt    # Python dependencies
└── README.md           # Documentation

data/
└── movielist.csv       # Dataset of Razzie nominees and winners (must be inside data folder)
```

## Setup Instructions

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. The API will be available at `http://localhost:5000`

## API Endpoints

### GET /api/producers/awards-interval

Returns producers with the maximum and minimum intervals between consecutive Worst Film awards.

#### Example Response:

```json
{
  "min": [
    {
      "producer": "Producer Name",
      "interval": 1,
      "previousWin": 2018,
      "followingWin": 2019
    }
  ],
  "max": [
    {
      "producer": "Producer Name",
      "interval": 99,
      "previousWin": 1900,
      "followingWin": 1999
    }
  ]
}
```

## Running Tests

To run the integration tests:

```
python tests.py
```

## Implementation Details

- The application loads data from a CSV file into an in-memory SQLite database
- API endpoints are implemented following REST principles (Richardson Maturity Level 2)
- Integration tests verify that the API returns the correct data format and values