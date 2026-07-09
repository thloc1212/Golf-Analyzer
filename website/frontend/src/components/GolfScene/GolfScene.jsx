import './GolfScene.css';

export default function GolfScene() {
  return (
    <div className="golf-scene-container">
      {/* Đồi cỏ */}
      <div className="hill hill-1"></div>
      <div className="hill hill-2"></div>
      <div className="hill hill-3"></div>

      {/* Cờ và Lỗ */}
      <div className="flag-group">
        <div className="pole"></div>
        <div className="flag"></div>
        <div className="hole"></div>
      </div>

      {/* Bóng Golf */}
      <div className="golf-ball">
        <div className="shadow"></div>
      </div>

      {/* Mây trang trí */}
      <div className="cloud cloud-1"></div>
      <div className="cloud cloud-2"></div>
    </div>
  );
}
