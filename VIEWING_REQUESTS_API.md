# Viewing Requests API Documentation

This document describes the API endpoints for managing car viewing requests in your CRM system.

## Base URL
```
/api/viewings/
```

## Authentication
All endpoints require authentication. Include your JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List All Viewing Requests
**GET** `/api/viewings/`

Returns a paginated list of all viewing requests with summary information.

**Query Parameters:**
- `page`: Page number for pagination
- `car`: Filter by car ID
- `client_name`: Filter by client name (partial match)
- `broker`: Filter by broker ID
- `start_date`: Filter by start date (ISO format: YYYY-MM-DDTHH:MM:SS)
- `end_date`: Filter by end date (ISO format: YYYY-MM-DDTHH:MM:SS)
- `status`: Filter by status (`scheduled`, `overdue`, `pending`)

**Example Request:**
```bash
GET /api/viewings/?status=scheduled&page=1
```

**Response (Summary Format):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/viewings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "reference_number": "ABC123DEF456",
      "car_make_model": "BMW X5 (2023)",
      "car_price": "75000.00",
      "car_image": "/media/cars/abc123/bmw_x5.jpg",
      "client_name": "John Doe",
      "client_email": "john@example.com",
      "client_phone": "+1234567890",
      "preferred_datetime": "2024-01-15T14:00:00Z",
      "broker_name": "Jane Smith",
      "created_at": "2024-01-10T10:30:00Z",
      "days_ago": 5
    }
  ]
}
```

### 2. Get Single Viewing Request Details
**GET** `/api/viewings/{id}/`

Returns full details of a specific viewing request.

**Response (Full Detail Format):**
```json
{
  "id": 1,
  "reference_number": "ABC123DEF456",
  "car": {
    "id": 5,
    "reference_number": "CAR789XYZ012",
    "make": "BMW",
    "model": "X5",
    "year": 2023,
    "description": "Luxury SUV with premium features",
    "price": "75000.00",
    "image": "/media/cars/car789/bmw_x5.jpg",
    "is_sold": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "car_details": {
    "id": 5,
    "reference_number": "CAR789XYZ012",
    "make": "BMW",
    "model": "X5",
    "year": 2023,
    "description": "Luxury SUV with premium features",
    "price": "75000.00",
    "image": "/media/cars/car789/bmw_x5.jpg",
    "is_sold": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_phone": "+1234567890",
  "preferred_datetime": "2024-01-15T14:00:00Z",
  "notes": "Client prefers afternoon viewing",
  "broker": {
    "id": 3,
    "reference_number": "BRO456GHI789",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1987654321"
  },
  "broker_details": {
    "id": 3,
    "reference_number": "BRO456GHI789",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1987654321"
  },
  "status_info": {
    "status": "scheduled",
    "is_overdue": false,
    "days_until_viewing": 5
  },
  "created_at": "2024-01-10T10:30:00Z",
  "updated_at": "2024-01-10T10:30:00Z"
}
```

### 3. Recent Viewing Requests
**GET** `/api/viewings/recent/`

Returns viewing requests from the last 30 days.

**Query Parameters:**
- `page`: Page number for pagination

**Example Request:**
```bash
GET /api/viewings/recent/?page=1
```

### 4. Upcoming Viewings
**GET** `/api/viewings/upcoming/`

Returns scheduled viewings that haven't happened yet, ordered by date.

**Query Parameters:**
- `page`: Page number for pagination

**Example Request:**
```bash
GET /api/viewings/upcoming/?page=1
```

### 5. Overdue Viewings
**GET** `/api/viewings/overdue/`

Returns viewing requests where the preferred datetime has passed.

**Query Parameters:**
- `page`: Page number for pagination

**Example Request:**
```bash
GET /api/viewings/overdue/?page=1
```

### 6. Viewings by Car
**GET** `/api/viewings/by_car/?car_id={car_id}`

Returns all viewing requests for a specific car.

**Required Parameters:**
- `car_id`: ID of the car

**Example Request:**
```bash
GET /api/viewings/by_car/?car_id=5
```

### 7. Viewings by Broker
**GET** `/api/viewings/by_broker/?broker_id={broker_id}`

Returns all viewing requests assigned to a specific broker.

**Required Parameters:**
- `broker_id`: ID of the broker

**Example Request:**
```bash
GET /api/viewings/by_broker/?broker_id=3
```

### 8. Create New Viewing Request
**POST** `/api/viewings/`

Creates a new viewing request.

**Request Body:**
```json
{
  "car_id": 5,
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_phone": "+1234567890",
  "preferred_datetime": "2024-01-15T14:00:00Z",
  "notes": "Client prefers afternoon viewing",
  "broker_id": 3
}
```

**Response:**
```json
{
  "id": 1,
  "reference_number": "ABC123DEF456",
  "car": { ... },
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_phone": "+1234567890",
  "preferred_datetime": "2024-01-15T14:00:00Z",
  "notes": "Client prefers afternoon viewing",
  "broker": { ... },
  "created_at": "2024-01-10T10:30:00Z",
  "updated_at": "2024-01-10T10:30:00Z"
}
```

### 9. Update Viewing Request
**PUT** `/api/viewings/{id}/`

Updates an existing viewing request.

**Request Body:** Same as POST

### 10. Delete Viewing Request
**DELETE** `/api/viewings/{id}/`

Deletes a viewing request.

### 11. Mark as Interested
**POST** `/api/viewings/{id}/mark_interested/`

Marks a viewing as interested (placeholder for future SoldCar creation).

**Response:**
```json
{
  "status": "interested"
}
```

### 12. Mark as Not Interested
**POST** `/api/viewings/{id}/mark_not_interested/`

Marks a viewing as not interested.

**Response:**
```json
{
  "status": "not_interested"
}
```

## Frontend Integration Examples

### React/JavaScript Example
```javascript
// Fetch all viewing requests
const fetchViewingRequests = async () => {
  try {
    const response = await fetch('/api/viewings/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching viewing requests:', error);
  }
};

// Fetch viewing requests with filters
const fetchFilteredViewings = async (filters) => {
  const params = new URLSearchParams(filters);
  try {
    const response = await fetch(`/api/viewings/?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching filtered viewings:', error);
  }
};

// Fetch upcoming viewings
const fetchUpcomingViewings = async () => {
  try {
    const response = await fetch('/api/viewings/upcoming/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching upcoming viewings:', error);
  }
};
```

### Python Example
```python
import requests

# Fetch all viewing requests
def get_viewing_requests(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('http://localhost:8000/api/viewings/', headers=headers)
    return response.json()

# Fetch filtered viewing requests
def get_filtered_viewings(token, filters):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(
        'http://localhost:8000/api/viewings/',
        headers=headers,
        params=filters
    )
    return response.json()
```

## Status Information

The `status_info` field provides useful information about each viewing request:

- **status**: `scheduled`, `expired`, or `pending`
- **is_overdue**: Boolean indicating if the preferred datetime has passed
- **days_until_viewing**: Number of days until the scheduled viewing (null if no datetime set)

## Pagination

All list endpoints support pagination with the following response format:
- `count`: Total number of items
- `next`: URL for next page (null if no next page)
- `previous`: URL for previous page (null if no previous page)
- `results`: Array of items for current page

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing required parameters)
- `401`: Unauthorized (invalid or missing token)
- `404`: Not Found (viewing request doesn't exist)
- `500`: Internal Server Error

Error responses include a descriptive message:
```json
{
  "error": "car_id parameter is required"
}
```
