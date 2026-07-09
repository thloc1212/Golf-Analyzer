export const analyzeVideo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://127.0.0.1:5001/analyze', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  const band = response.headers.get('X-Golf-Band');
  const probs = response.headers.get('X-Golf-Probs');
  const swingSpeed = response.headers.get('X-Swing-Speed');
  const armAngle = response.headers.get('X-Arm-Angle');

  const blob = await response.blob();
  const videoUrl = URL.createObjectURL(blob);

  return {
    result: {
      band: band || 'Unknown',
      probs: probs,
      swingSpeed: parseFloat(swingSpeed || 0).toFixed(2),
      armAngle: parseFloat(armAngle || 0).toFixed(1)
    },
    videoUrl
  };
};
