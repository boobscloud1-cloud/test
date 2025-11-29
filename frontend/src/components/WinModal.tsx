import React from 'react';

interface WinModalProps {
  isOpen: boolean;
  prize: { value: number, type: string };
  onClose: () => void;
}

export const WinModal: React.FC<WinModalProps> = ({ isOpen, prize, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <span className="modal-icon">🎉</span>
        <h3 className="modal-title">YOU WON!</h3>
        <p className="modal-text">
          {prize.value} {prize.type}
        </p>
        <button className="btn-primary" onClick={onClose}>
            AWESOME!
        </button>
      </div>
    </div>
  );
};
