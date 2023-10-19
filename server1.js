const express = require('express');
const mysql = require('mysql2/promise');// Use mysql2 instead of mysql
const app = express();
const port = 3000;

const cors = require("cors");

const corsOptions = {   origin: "*",   methods:
"GET,HEAD,PUT,PATCH,POST,DELETE",   allowedHeaders:
    "Access-Control-Allow-Headers,Access-Control-Allow-Origin,Access-Control-Request-Method,Access-Control-Request-Headers,Origin,Cache-Control,Content-Type,X-Token,X-Refresh-Token",   credentials: true,   preflightContinue: false,  
optionsSuccessStatus: 204 };

app.use(cors());

app.use(express.static(__dirname));

// Create a connection pool
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '12345',   
    database: 'dsci560_lab5',
    waitForConnections: true,
    connectionLimit: 10, // Adjust the limit as needed
    queueLimit: 0,
});

// Create a promise pool from the connection pool
//const db = pool.promise();

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index1.html');
});

app.get('/fetch_data', (req, res) => {
    
    console.log('Inside fetch_data...')
    const sql = 'SELECT name, latitude, longitude FROM wells_data';
    
    // Use the pool to execute the query directly
    pool.query(sql)
        .then(([rows, fields]) => {
            res.json(rows);
        })
        .catch((err) => {
            console.error('Error querying the database:', err);
            res.status(500).json({ error: 'An error occurred while fetching data from the database.' });
        });
});


app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});