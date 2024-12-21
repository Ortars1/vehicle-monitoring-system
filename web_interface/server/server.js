const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());

// Serving static files
app.use(express.static(path.join(__dirname, '../build')));

const pool = new Pool({
  host: process.env.DATABASE_HOST || 'database-service',
  database: process.env.DATABASE_NAME || 'vehicle_monitoring',
  user: process.env.DATABASE_USER || 'postgres',
  password: process.env.DATABASE_PASSWORD || 'your_password',
  port: process.env.DATABASE_PORT || 5432,
});

app.get('/api/vehicles', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT DISTINCT vehicle_id, 
             latitude, longitude, timestamp, speed, fuel_level
      FROM vehicle_data
      WHERE timestamp = (
          SELECT MAX(timestamp)
          FROM vehicle_data v2
          WHERE v2.vehicle_id = vehicle_data.vehicle_id
      )
    `);
    res.json({ vehicles: result.rows });
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Catch all routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../build', 'index.html'));
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
