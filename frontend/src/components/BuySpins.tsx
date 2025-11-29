import React, { useMemo, useState } from 'react';
import WebApp from '@twa-dev/sdk';
import { buySpins } from '../requests/api';

type PurchaseResult = {
  spins_purchased: number;
  remaining_spins: number;
  remaining_points: number;
};

interface BuySpinsProps {
  telegramId: number;
  points: number;
  onComplete: (res: PurchaseResult) => void;
}

const COST_PER_SPIN = 1000;

export const BuySpins: React.FC<BuySpinsProps> = ({ telegramId, points, onComplete }) => {
  const [qty, setQty] = useState<number>(1);
  const [expanded, setExpanded] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const totalCost = useMemo(() => qty * COST_PER_SPIN, [qty]);
  const canAfford = points >= totalCost;

  const dec = () => setQty((q) => Math.max(1, q - 1));
  const inc = () => setQty((q) => Math.min(20, q + 1));

  const handleBuy = async () => {
    if (!canAfford || loading) return;
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const res: PurchaseResult = await buySpins(telegramId, qty);
      onComplete(res);

      if (WebApp.HapticFeedback) {
        WebApp.HapticFeedback.notificationOccurred('success');
      }
      setMessage(`Purchased ${res.spins_purchased} ${res.spins_purchased > 1 ? 'spins' : 'spin'}.`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Purchase failed';
      setError(detail);
      if (WebApp.HapticFeedback) {
        WebApp.HapticFeedback.notificationOccurred('error');
      }
    } finally {
      setLoading(false);
    }
  };

  const remaining = Math.max(0, Math.floor(points - totalCost));

  // Collapsed state: a single Buy Spins button
  if (!expanded) {
    return (
      <section className="buy-panel buy-collapsed" role="region" aria-label="Buy Spins">
        <button
          className="btn-primary btn-buy-mini"
          onClick={() => setExpanded(true)}
          aria-expanded="false"
          aria-controls="buy-spins-card"
        >
          <span className="btn-main">Buy Spins</span>
          <span className="cost-badge" aria-hidden="true">1000 pts/spin</span>
        </button>
      </section>
    );
  }

  // Expanded modal with controls (qty only via +/-), replicating Out of Spins modal style
  return (
    <div
      className="modal-overlay"
      onClick={() => {
        if (!loading) {
          setExpanded(false);
          setError(null);
          setMessage(null);
        }
      }}
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="buy-close"
          aria-label="Close buy spins panel"
          onClick={() => {
            setExpanded(false);
            setError(null);
            setMessage(null);
          }}
          disabled={loading}
        >
          &times;
        </button>

        <h3
          id="buy-spins-title"
          className="buy-title"
          style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            color: 'transparent'
          }}
        >
          Buy Spins
        </h3>
        <p className="buy-subtitle">1000 pts per spin</p>

        <div className="buy-balance" aria-live="polite">
          Available: <span className="bal-value">{Math.floor(points).toLocaleString()} pts</span>
        </div>

        <label className="qty-label">Quantity</label>
        <div className="qty-control">
          <button
            type="button"
            className="btn-qty"
            onClick={dec}
            aria-label="Decrease quantity"
            disabled={loading}
          >
            &minus;
          </button>

          {/* Display-only current quantity (no typing) */}
          <div className="qty-display" role="status" aria-live="polite" aria-atomic="true">
            {qty}
          </div>

          <button
            type="button"
            className="btn-qty"
            onClick={inc}
            aria-label="Increase quantity"
            disabled={loading}
          >
            +
          </button>
        </div>

        <div id="cost-desc" className="buy-cost">
          <span>Total:</span> <strong>{totalCost.toLocaleString()} pts</strong>
        </div>
        <div className="buy-remaining">After purchase: {remaining.toLocaleString()} pts</div>

        {error && <div role="alert" className="buy-error">⚠ {error}</div>}
        {message && <div aria-live="polite" className="buy-success">✓ {message}</div>}

        <button
          className="btn-primary"
          onClick={handleBuy}
          disabled={!canAfford || loading}
          aria-disabled={!canAfford || loading}
        >
          {loading ? 'Processing...' : `Buy ${qty} ${qty > 1 ? 'Spins' : 'Spin'}`}
        </button>
      </div>
    </div>
  );
};

export default BuySpins;
