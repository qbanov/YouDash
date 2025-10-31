import React from 'react';

function LoadingScreen({ isVisible }) {
  if (!isVisible) return null;

  return (
    <div id="loadingScreen" className={isVisible ? '' : 'fade-out'}>
      <p>Ładowanie...</p>
    </div>
  );
}

export default LoadingScreen;
