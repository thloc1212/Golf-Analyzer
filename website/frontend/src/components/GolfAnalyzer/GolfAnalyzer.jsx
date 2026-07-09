import { useGolfAnalysis } from '../../hooks/useGolfAnalysis';
import UploadBox from './UploadBox';
import ProcessingView from './ProcessingView';
import ResultView from './ResultView';
import './GolfAnalyzer.css';

export default function GolfAnalyzer() {
  const {
    status,
    videoSrc,
    loadingText,
    progress,
    analysisResult,
    processVideo,
    resetAnalysis
  } = useGolfAnalysis();

  return (
    <div className="analyzer-container">
      {status === 'idle' && (
        <UploadBox onFileSelect={processVideo} />
      )}

      {status === 'processing' && (
        <ProcessingView loadingText={loadingText} progress={progress} />
      )}

      {status === 'done' && (
        <ResultView 
          videoSrc={videoSrc} 
          analysisResult={analysisResult} 
          onReset={resetAnalysis} 
        />
      )}
    </div>
  );
}
