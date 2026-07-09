export default function ProcessingView({ loadingText, progress }) {
  return (
    <div className="processing-box">
      <div className="loader-circle"></div>
      <h3>{loadingText}</h3>
      <div className="progress-bar-container">
        <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
      </div>
      <p>{progress}% hoàn thành</p>
    </div>
  );
}
