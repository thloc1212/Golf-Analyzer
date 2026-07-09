const express = require('express');
const cors = require('cors');
const analyzeRoutes = require('./routes/analyzeRoutes');

const app = express();
const PORT = 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Root route for checking server status
app.get('/', (req, res) => {
  res.send('Golf Analyzer Backend is running! Use POST /analyze to upload videos.');
});

// Use routes
app.use(analyzeRoutes);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
