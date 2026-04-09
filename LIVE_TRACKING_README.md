# Live Delivery Tracking System

## Overview
The live delivery tracking system allows customers to track delivery persons in real-time during the delivery process. Delivery persons can share their location, and customers can see:

- **Live location** of the delivery person on a map
- **Real-time ETA** (Estimated Time of Arrival)
- **Distance remaining** to delivery location
- **Route visualization** from current location to destination

## Features

### For Delivery Persons
- **Location Sharing Controls**: Start/stop sharing location with customers
- **Automatic Location Updates**: GPS coordinates updated every 30 seconds when active
- **Manual Location Updates**: Update location on-demand
- **Privacy Control**: Complete control over when location is shared

### For Customers
- **Live Map Tracking**: See delivery person's current location in real-time
- **ETA Calculation**: Dynamic ETA based on current location and distance
- **Route Visualization**: Visual route from delivery person to destination
- **Status Updates**: Real-time status of location sharing

## Technical Implementation

### Database Changes
New columns added to `user` table:
- `current_lat`: Current latitude (FLOAT)
- `current_lng`: Current longitude (FLOAT)
- `location_updated_at`: Timestamp of last location update (DATETIME)
- `is_sharing_location`: Whether location sharing is active (BOOLEAN)

### API Endpoints

#### `/api/update-location` (POST)
Updates delivery person's current location.
```json
{
  "lat": 28.7041,
  "lng": 77.1025
}
```

#### `/api/stop-location-sharing` (POST)
Stops location sharing for the current user.

#### `/api/get-delivery-location/<order_id>` (GET)
Gets current location of delivery person for a specific order.
```json
{
  "success": true,
  "location": {
    "lat": 28.7041,
    "lng": 77.1025,
    "updated_at": "2024-01-15T10:30:00Z",
    "delivery_person": "John Doe"
  }
}
```

#### `/api/calculate-eta/<order_id>` (GET)
Calculates ETA from delivery person's current location to customer.
```json
{
  "success": true,
  "eta_minutes": 15,
  "distance_km": 5.2,
  "current_location": {"lat": 28.7041, "lng": 77.1025},
  "destination": {"lat": 28.6139, "lng": 77.2090}
}
```

## Setup Instructions

### 1. Database Migration
Run the migration script to add new columns:
```bash
python migrate_location_tracking.py
```

### 2. Environment Variables
Ensure your `.env` file has:
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 3. Browser Permissions
The system requires:
- **Geolocation API** access for delivery persons
- **Google Maps JavaScript API** for map display

## User Workflow

### Delivery Person Workflow
1. **Login** to delivery dashboard
2. **Start Location Sharing** when beginning deliveries
3. **System automatically updates** location every 30 seconds
4. **Stop sharing** when deliveries are complete

### Customer Workflow
1. **Place order** and select delivery location
2. **Track order** using the tracking page
3. **View live location** of delivery person on map
4. **See real-time ETA** and distance updates

## Security & Privacy

- **User Consent**: Location sharing requires explicit user action
- **Data Protection**: Location data is only accessible to authorized users
- **Time Limits**: Location data expires after 10 minutes of inactivity
- **Role-Based Access**: Only delivery persons can update locations, only customers/shopkeepers can view

## Technical Details

### Location Update Frequency
- **Automatic**: Every 30 seconds when sharing is active
- **Manual**: On-demand via "Update Location" button
- **Background**: Uses `navigator.geolocation.watchPosition()` for continuous tracking

### ETA Calculation
- **Algorithm**: Haversine distance formula
- **Speed Assumption**: 30 km/h average city speed
- **Buffer**: +5 minutes added for traffic/loading time
- **Real-time**: Recalculated every 60 seconds

### Map Features
- **Markers**: Different icons for pickup, delivery, and delivery person
- **Route**: Dynamic polyline showing path to destination
- **Bounds**: Auto-fit to show all relevant locations
- **Real-time Updates**: Markers and routes update automatically

## Browser Compatibility

### Supported Browsers
- Chrome 50+
- Firefox 50+
- Safari 10+
- Edge 79+

### Required Permissions
- `geolocation` API access
- HTTPS (required for geolocation in modern browsers)

## Troubleshooting

### Common Issues

#### "Geolocation not supported"
- Ensure browser supports Geolocation API
- Check if using HTTPS (required for geolocation)

#### "Location sharing not working"
- Check browser location permissions
- Verify GPS is enabled on device
- Try refreshing the page

#### "Map not loading"
- Verify Google Maps API key is set
- Check API key restrictions (referrer/domain)
- Ensure internet connectivity

#### "ETA not updating"
- Check if delivery person has location sharing active
- Verify order has valid delivery coordinates
- Check browser console for JavaScript errors

### Debug Mode
Enable debug logging by setting:
```javascript
console.log('Location update:', position.coords);
```

## Future Enhancements

### Potential Improvements
- **Google Directions API**: More accurate routing and ETA
- **WebSocket**: Real-time updates without polling
- **Push Notifications**: ETA alerts and status updates
- **Route Optimization**: Multiple delivery points
- **Traffic Data**: Real-time traffic integration
- **Offline Support**: Cached location data

### Performance Optimizations
- **Location Batching**: Send multiple updates in single request
- **Distance Filtering**: Only update when location changes significantly
- **Background Sync**: Update when app is in background
- **Battery Optimization**: Reduce update frequency when stationary

## API Reference

### Error Codes
- `400`: Invalid coordinates or missing data
- `403`: Unauthorized access
- `404`: Location data not available
- `500`: Server error

### Rate Limits
- Location updates: 2 per minute per user
- API calls: 60 per minute per IP
- Map loads: 1000 per day per API key

## Support

For technical support or feature requests, please check:
1. Browser console for JavaScript errors
2. Flask application logs
3. Google Maps API console for quota issues
4. Database migration status