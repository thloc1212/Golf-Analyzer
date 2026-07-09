const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

exports.analyzeVideo = (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  console.log('File uploaded:', req.file.path);
  
  // Đường dẫn file output
  const outputFilename = 'processed-' + req.file.filename;
  const outputPath = path.join(os.tmpdir(), outputFilename);

  console.log('Starting AI processing...');

  // Gọi Python script để xử lý video
  const pythonProcess = spawn('python3', ['process_video.py', req.file.path, outputPath]);

  let pythonOutput = '';

  // Lắng nghe log từ Python (để debug)
  pythonProcess.stdout.on('data', (data) => {
    const str = data.toString();
    // console.log(`Python stdout: ${str}`);
    pythonOutput += str;
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });

  // Khi Python chạy xong
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    
    // Xóa file input sau khi xử lý xong
    fs.unlink(req.file.path, (err) => {
      if (err) console.error('Error deleting input file:', err);
    });

    if (code === 0) {
      // Parse JSON result from Python output
      let analysisResult = {};
      try {
        const match = pythonOutput.match(/__JSON_START__(.*)__JSON_END__/s);
        if (match && match[1]) {
          analysisResult = JSON.parse(match[1]);
          // console.log('Parsed Analysis Result:', analysisResult);
          // console.log('Metrics - Speed:', analysisResult.swing_speed, 'Angle:', analysisResult.arm_angle);
        }
      } catch (e) {
        console.error('Error parsing Python JSON output:', e);
      }

      // Trả về file đã xử lý
      const absoluteOutputPath = path.resolve(outputPath);
      
      // Set custom headers for analysis result
      res.set('Access-Control-Expose-Headers', 'X-Golf-Band, X-Golf-Probs, X-Swing-Start, X-Swing-End, X-Swing-Speed, X-Arm-Angle');
      res.set('X-Golf-Band', analysisResult.band || 'Unknown');
      res.set('X-Golf-Probs', analysisResult.probs || '');
      res.set('X-Swing-Start', analysisResult.swing_start || 0);
      res.set('X-Swing-End', analysisResult.swing_end || 0);
      res.set('X-Swing-Speed', analysisResult.swing_speed || 0);
      res.set('X-Arm-Angle', analysisResult.arm_angle || 0);

      res.sendFile(absoluteOutputPath, (err) => {
        // Xóa file output sau khi gửi xong
        fs.unlink(absoluteOutputPath, (unlinkErr) => {
          if (unlinkErr) console.error('Error deleting output file:', unlinkErr);
        });

        if (err) {
          console.error('Error sending file:', err);
          // res.status(500).json({ error: 'Error sending processed file' });
        }
      });
    } else {
      res.status(500).json({ error: 'Video processing failed' });
    }
  });
};
