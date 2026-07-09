import { useState } from 'react';
import { analyzeVideo } from '../services/api';

export const useGolfAnalysis = () => {
  const [status, setStatus] = useState('idle'); // idle | processing | done
  const [videoSrc, setVideoSrc] = useState(null);
  const [loadingText, setLoadingText] = useState('Đang khởi động AI...');
  const [progress, setProgress] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);

  const processVideo = async (file) => {
    if (!file) return;

    setStatus('processing');
    setProgress(0);
    setLoadingText('Đang tải video lên...');
    setAnalysisResult(null);

    try {
      // Simulate progress
      let progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + 5;
        });
      }, 200);

      const { result, videoUrl } = await analyzeVideo(file);

      clearInterval(progressInterval);
      setProgress(100);
      setAnalysisResult(result);
      setVideoSrc(videoUrl);
      setStatus('done');
    } catch (error) {
      console.error('Error:', error);
      alert('Có lỗi xảy ra khi xử lý video!');
      setStatus('idle');
    }
  };

  const resetAnalysis = () => {
    setStatus('idle');
    setVideoSrc(null);
    setAnalysisResult(null);
    setProgress(0);
  };

  return {
    status,
    videoSrc,
    loadingText,
    progress,
    analysisResult,
    processVideo,
    resetAnalysis
  };
};
