const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const analyzeController = require('../controllers/analyzeController');

router.post('/analyze', upload.single('file'), analyzeController.analyzeVideo);

module.exports = router;