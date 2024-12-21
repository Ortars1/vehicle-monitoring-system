import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [vehicles, setVehicles] = useState([]);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await axios.get('/api/vehicles');
        setVehicles(response.data.vehicles);
      } catch (error) {
        console.error('Error fetching vehicles:', error);
      }
    };

    fetchVehicles();
    const interval = setInterval(fetchVehicles, 5000); //Обновление каждые 5 сек
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Vehicle Monitoring System</h1>
      <div>
        {vehicles.map((vehicle) => (
          <div key={vehicle.vehicle_id} style={{ margin: '10px', padding: '10px', border: '1px solid #ccc' }}>
            <p>Vehicle ID: {vehicle.vehicle_id}</p>
            <p>Location: {vehicle.latitude}, {vehicle.longitude}</p>
            <p>Speed: {vehicle.speed} km/h</p>
            <p>Fuel Level: {vehicle.fuel_level}%</p>
            <p>Last Updated: {new Date(vehicle.timestamp).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
