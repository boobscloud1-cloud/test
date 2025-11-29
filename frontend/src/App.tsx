import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import WebApp from '@twa-dev/sdk';
import { getUser } from './requests/api';
import { Wheel } from './components/Wheel';
import { TaskList } from './components/TaskList';
import { WinModal } from './components/WinModal';
import { NoSpinsModal } from './components/NoSpinsModal';
import { BuySpins } from './components/BuySpins';
import { AdminDashboard } from './components/AdminDashboard';
import './App.css';

// Mock user for browser dev (since TWA SDK might not work outside TG)
const MOCK_USER_ID = 123456789;

function Game({ user, setUser }: { user: any, setUser: any }) {
  const [winModalOpen, setWinModalOpen] = useState(false);
  const [winPrize, setWinPrize] = useState<{value: number, type: string}>({ value: 0, type: '' });
  const [noSpinsModalOpen, setNoSpinsModalOpen] = useState(false);

  const handleSpinResult = (result: any) => {
    if (user) {
        setUser((prev: any) => ({ 
            ...prev, 
            spins: result.remaining_spins 
        }));
        getUser(user.telegram_id).then(setUser);
      
      if (WebApp.HapticFeedback) {
        WebApp.HapticFeedback.notificationOccurred('success');
      }

      setWinPrize({ value: result.prize_value, type: result.prize_type });
      setWinModalOpen(true);
    }
  };

  const handleSpinError = (error: any) => {
      console.error(error); 
      setNoSpinsModalOpen(true);
      if (WebApp.HapticFeedback) {
        WebApp.HapticFeedback.notificationOccurred('error');
      }
  };

  const scrollToElement = (id: string) => {
      const element = document.getElementById(id);
      if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
  };

  return (
    <div className="app-main">
      <div className="wheel-stack">
        <Wheel 
          telegramId={user.telegram_id} 
          onSpinEnd={handleSpinResult} 
          onError={handleSpinError}
        />

        <BuySpins 
          telegramId={user.telegram_id}
          points={user.points}
          onComplete={(res) => {
            setUser((prev: any) => ({
              ...prev,
              spins: res.remaining_spins,
              points: res.remaining_points
            }));
          }}
        />
      </div>

      <hr className="divider" />
      
      <TaskList telegramId={user.telegram_id} />

      <WinModal 
        isOpen={winModalOpen} 
        prize={winPrize} 
        onClose={() => setWinModalOpen(false)} 
      />

      <NoSpinsModal
        isOpen={noSpinsModalOpen}
        onClose={() => setNoSpinsModalOpen(false)}
        onGoToTasks={() => scrollToElement('task-wall-section')}
        onInviteFriends={() => scrollToElement('invite-friends-section')}
      />
    </div>
  );
}

function MainApp() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      let telegramId = MOCK_USER_ID;

      // Check if running in Telegram
      if (WebApp.initDataUnsafe?.user) {
        telegramId = WebApp.initDataUnsafe.user.id;
        WebApp.expand();
        WebApp.setHeaderColor('#0f172a');
      }

      // Register/Get User from Backend
      try {
        const userData = await getUser(telegramId);
        setUser(userData);
      } catch (e) {
        console.error("Auth error", e);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  if (loading) return <div className="loading-screen">Loading...</div>;
  if (!user) return <div className="error-screen">Failed to load user data.</div>;

  return (
    <div className="app-container">
      <header className="app-header">
        <h2 className="header-title">Wheel of Fortune</h2>
        <div className="stats-container">
            <div className="stat-card">
              <span className="stat-label">Spins</span>
              <span className="stat-value highlight">{user.spins}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Points</span>
              <span className="stat-value">{user.points}</span>
            </div>
        </div>
      </header>

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Game user={user} setUser={setUser} />} />
          <Route path="/admin" element={<AdminDashboard telegramId={user.telegram_id} />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default MainApp;
