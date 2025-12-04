require("dotenv").config();
const express = require("express");
const cors = require("cors");
const axios = require("axios");
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

// ------------------- FLASK API BASE URL -------------------
cconst FLASK_API_URL = process.env.FLASK_API_URL || "http://127.0.0.1:8000";


// ====================================================================
//                 🌱 FERTILITY PREDICTION (ML MODEL)
// ====================================================================
app.post("/api/crops/fertility", async (req, res) => {
  try {
    const response = await axios.post(
      `${FLASK_API_URL}/predict/fertility`,
      req.body
    );
    res.json(response.data);
  } catch (error) {
    console.error("Error calling Flask fertility API:", error.message);
    res.status(500).json({ error: "Failed to get fertility prediction" });
  }
});


// ====================================================================
//          💧 IRRIGATION (MOISTURE) PREDICTION — NEW IMPROVED
// ====================================================================
app.post("/api/crops/moisture", async (req, res) => {
  try {
    console.log("Backend received irrigation request:", req.body);

    const response = await axios.post(
      `${FLASK_API_URL}/predict/irrigation`,   // <-- NEW ENDPOINT
      req.body,
      {
        headers: { "Content-Type": "application/json" },
        timeout: 10000, // 10 seconds
      }
    );

    console.log("Flask returned:", response.data);
    res.json(response.data);

  } catch (error) {
    console.error("Error calling Flask irrigation API:", error.message);

    if (error.response) {
      // Flask returned an error response
      console.error("Flask error:", error.response.data);
      return res.status(error.response.status).json(error.response.data);
    }

    if (error.code === "ECONNREFUSED") {
      return res.status(503).json({
        error: "Cannot connect to ML service. Make sure Flask is running on port 8000",
      });
    }

    res.status(500).json({
      error: "Failed to get irrigation prediction",
      details: error.message,
    });
  }
});


// ====================================================================
//                             ❤️ HEALTH CHECK
// ====================================================================
app.get("/api/health", async (req, res) => {
  try {
    const flaskResponse = await axios.get(`${FLASK_API_URL}/health`, {
      timeout: 3000,
    });

    res.json({
      backend: "healthy",
      flask: flaskResponse.data,
    });

  } catch (error) {
    res.json({
      backend: "healthy",
      flask: "unavailable",
      error: error.message,
    });
  }
});


// ====================================================================
//                           🚀 SERVER START
// ====================================================================
const PORT = process.env.PORT || 5000;
app.listen(PORT, () =>
  console.log(`🚀 Server running on port ${PORT}`)
);
