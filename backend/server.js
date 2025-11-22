require("dotenv").config();
const express = require("express");
const cors = require("cors");
const axios = require("axios"); // <-- to call Flask API
const connectDB = require("./config/db");
const authRoutes = require("./routes/authRoutes");
const cropRoutes = require("./routes/cropRoutes");

const app = express();
connectDB();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api/auth", authRoutes);
app.use("/api/crops", cropRoutes);

// ------------------- FLASK API INTEGRATION -------------------

// Base URL of your Flask API
const FLASK_API_URL = "http://127.0.0.1:8000";

// Route to call Fertility prediction
app.post("/api/crops/fertility", async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_API_URL}/predict/fertility`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error("Error calling Flask fertility API:", error.message);
    res.status(500).json({ error: "Failed to get fertility prediction" });
  }
});

// Route to call Moisture prediction
app.post("/api/crops/moisture", async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_API_URL}/predict/moisture`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error("Error calling Flask moisture API:", error.message);
    res.status(500).json({ error: "Failed to get moisture prediction" });
  }
}); 

// ------------------- SERVER -------------------
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
