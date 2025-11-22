const mongoose = require("mongoose");

const cropSchema = new mongoose.Schema({
  name: String,
  soil: String,
  rainfall: String,
  temperature: String
});

module.exports = mongoose.model("Crop", cropSchema);
