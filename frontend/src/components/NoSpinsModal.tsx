import React from 'react';

interface NoSpinsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGoToTasks: () => void;
  onInviteFriends: () => void;
}

export const NoSpinsModal: React.FC<NoSpinsModalProps> = ({ 
    isOpen, 
    onClose, 
    onGoToTasks, 
    onInviteFriends 
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <span className="modal-icon">😢</span>
        <h3 className="modal-title" style={{ 
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            color: 'transparent'
        }}>
            Out of Spins!
        </h3>
        <p className="modal-text">
          You have no spins left. Complete tasks or invite friends to keep playing!
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <button 
                className="btn-primary" 
                onClick={() => { onClose(); onGoToTasks(); }}
                style={{ fontSize: '1rem', padding: '10px' }}
            >
                📋 Complete Tasks
            </button>
            
            <button 
                className="btn-primary" 
                onClick={() => { onClose(); onInviteFriends(); }}
                style={{ 
                    fontSize: '1rem', 
                    padding: '10px', 
                    background: 'var(--bg-secondary)', 
                    border: '1px solid rgba(255,255,255,0.1)' 
                }}
            >
                👥 Invite Friends
            </button>
        </div>
      </div>
    </div>
  );
};
