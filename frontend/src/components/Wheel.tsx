import React, { useState, useRef } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { spinWheel } from '../requests/api';

interface WheelProps {
  telegramId: number;
  onSpinEnd: (result: any) => void;
  onError: (error: any) => void;
}

export const Wheel: React.FC<WheelProps> = ({ telegramId, onSpinEnd, onError }) => {
  const [isSpinning, setIsSpinning] = useState(false);
  const controls = useAnimation();
  const characterControls = useAnimation();
  const currentRotation = useRef(0); // Store total rotation to prevent snapping back

  // Wedge labels to match backend prize mapping (0..7 wedges, 45° each)
  // Backend PRIZES base angles: 0,45,90,135,180,225,270,315
  const wedges = [
    { label: '1 Spin' },    // 0°
    { label: '100 pts' },   // 45°
    { label: '500 pts' },   // 90°
    { label: '5 Spins' },   // 135°
    { label: 'iPhone' },    // 180°
    { label: '50 pts' },    // 225°
    { label: '2 Spins' },   // 270°
    { label: '1000 pts' },  // 315°
  ];

  // Map backend prize to its base wedge angle for consistent visual alignment
  const prizeAngleMap = (type: string, value: string): number => {
    if (type === 'spins' && value === '1') return 0;
    if (type === 'points' && value === '100') return 45;
    if (type === 'points' && value === '500') return 90;
    if (type === 'spins' && value === '5') return 135;
    if (type === 'item' && value === 'iphone') return 180;
    if (type === 'points' && value === '50') return 225;
    if (type === 'spins' && value === '2') return 270;
    if (type === 'points' && value === '1000') return 315;
    return 0;
  };

  const handleSpin = async () => {
    if (isSpinning) return;
    setIsSpinning(true);

    try {
      // Character Push Animation
      await characterControls.start({
        x: [0, -20, 0], // Move left (push) and back
        rotate: [0, -15, 0], // Lean forward
        transition: { duration: 0.5, ease: 'easeInOut' },
      });

      const result = await spinWheel(telegramId);

      // Calculate new rotation using backend-provided angle to ensure exact match.
      // CSS 0deg points to the right (3 o'clock). Pointer is at top (12 o'clock).
      // We want the prize angle to end up at 0deg (top): (result.angle + currentRotation + delta) % 360 === 0
      const fullSpins = 360 * 5;
      const theta = ((result.angle % 360) + 360) % 360;
      const currentMod = ((currentRotation.current % 360) + 360) % 360;
      const delta = (360 - theta - currentMod + 360) % 360;

      const newTotalRotation = currentRotation.current + fullSpins + delta;

      await controls.start({
        rotate: newTotalRotation,
        transition: { duration: 5, ease: 'circOut' },
      });

      currentRotation.current = newTotalRotation; // Update ref

      onSpinEnd(result);
    } catch (e) {
      console.error(e);
      // Pass error to parent to handle with modal
      onError(e);
    } finally {
      setIsSpinning(false);
    }
  };

  return (
    <div className="wheel-container">
      {/* Pointer */}
      <div className="wheel-pointer" />

      {/* Character (Wizard/Businessman) */}
      <motion.div
        animate={characterControls}
        style={{
          position: 'absolute',
          right: -60, // Position to the right of the wheel
          bottom: 20,
          fontSize: '80px',
          zIndex: 10,
          cursor: 'pointer',
          filter: 'drop-shadow(0 4px 4px rgba(0,0,0,0.4))',
        }}
        onClick={handleSpin} // Allow clicking character to spin too!
        whileHover={{ scale: 1.1 }}
      >
        🧙‍♂️
      </motion.div>

      {/* Wheel Disc */}
      <motion.div
        className="wheel-disc"
        animate={controls}
        initial={{ rotate: 0 }}
        // Add a slight idle wobble when not spinning
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {wedges.map((w, i) => {
          const angle = i * 45 + 22.5; // center of each 45° wedge
          return (
            <div
              key={i}
              className="wedge-label"
              style={{
                transform: `translate(-50%, -50%) rotate(${angle}deg) translate(0, -115px) rotate(${-angle}deg)`,
              }}
            >
              {w.label}
            </div>
          );
        })}
        <div className="wheel-overlay" />
        <div className="wheel-hub" />
      </motion.div>

      <div className="spin-btn-container">
        <button className="btn-primary" onClick={handleSpin} disabled={isSpinning}>
          {isSpinning ? 'SPINNING...' : 'SPIN THE WHEEL'}
        </button>
      </div>
    </div>
  );
};
