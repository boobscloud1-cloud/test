import React, { useEffect, useState } from 'react';
// @ts-ignore
import postscribe from 'postscribe';
import { getTasks, api } from '../requests/api';

interface Task {
  id: number;
  name: string;
  description: string;
  reward_spins: number;
}

export const TaskList: React.FC<{ telegramId: number }> = ({ telegramId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    getTasks().then(setTasks);
  }, []);

  const handleTaskClick = (task: Task) => {
    // Special handling for "Complete Survey" using Script Injection (Overlay)
    // Uses postscribe to handle 'document.write' used by CPAGrip
    if (task.name === "Complete Survey") {
        // If the locker script is already loaded, just trigger it again (do not touch the DOM container)
        try {
            // @ts-ignore
            if (window.call_locker) {
                console.log("Locker already loaded, calling...");
                // @ts-ignore
                window.call_locker();
                return;
            }
        } catch (err) {
            console.warn("Existing locker failed to open, re-injecting...", err);
        }

        const containerId = "cpagrip-script-container";
        
        // Ensure container exists (and clear only when re-injecting)
        let container = document.getElementById(containerId);
        if (!container) {
            container = document.createElement('div');
            container.id = containerId;
            // Append to body so it can overlay
            document.body.appendChild(container);
        } else {
            // Clear previous script content before re-injection
            container.innerHTML = '';
        }

        console.log("Injecting CPAGrip Script via Postscribe...");

        // Use postscribe to safely inject the script that uses document.write
        postscribe('#' + containerId, `<script src="https://trianglerockers.com/script_include.php?id=1857570&tracking_id=${telegramId}"></script>`, {
            done: () => {
                console.log("CPAGrip Script Loaded.");
                // Allow a brief moment for script execution/parsing then call the trigger
                setTimeout(() => {
                    // @ts-ignore
                    if (window.call_locker) {
                        console.log("Calling call_locker()...");
                        // @ts-ignore
                        window.call_locker();
                    } else {
                        console.warn("call_locker function not found after script load.");
                        // Fallback: Maybe the script didn't expose it yet or failed?
                        alert("Survey loaded. Click again if it doesn't appear.");
                    }
                }, 500);
            }
        });
        
        return;
    }

    // Fallback for Link Lockers (Legacy)
    const CPAGRIP_URL = "https://www.cpagrip.com/show.php?l=REPLACE_WITH_YOUR_LINK_ID";
    const finalLink = `${CPAGRIP_URL}&tracking_id=${telegramId}`;
    window.open(finalLink, '_blank');
  };
  
  const referralLink = `https://t.me/MyBot?start=${telegramId}`;

  return (
    <div>
      <h3 id="task-wall-section" className="section-title">
        <span>⚡</span> Task Wall (Get Spins)
      </h3>
      
      <ul className="task-list">
        {tasks.map(task => (
          <li key={task.id} className="task-item" onClick={() => handleTaskClick(task)}>
            <div className="task-info">
                <span className="task-name">{task.name}</span>
                <p className="task-desc">{task.description}</p>
            </div>
            <div className="task-action">
                <button className="btn-task">
                    +{task.reward_spins} Spins
                </button>
            </div>
          </li>
        ))}
      </ul>

      <div id="invite-friends-section" className="invite-section">
        <h4 className="invite-title">Invite Friends</h4>
        <p className="invite-text">Get 3 spins when they complete a task!</p>
        <div className="invite-input-group">
            <input 
                className="invite-input"
                type="text" 
                readOnly 
                value={referralLink} 
            />
            <button 
                className="btn-copy"
                onClick={() => {
                    navigator.clipboard.writeText(referralLink);
                    alert("Link copied!");
                }}
            >
                Copy
            </button>
        </div>
      </div>

      <div className="debug-zone">
        <h4 className="debug-title">Developer Debug Zone</h4>
        <p style={{ fontSize: 12, margin: 0, marginBottom: 5 }}>Simulate completing a task (CPA Postback)</p>
        <button
            className="btn-debug"
            onClick={async () => {
                const randomTransId = "DEBUG_" + Math.floor(Math.random() * 10000);
                try {
                    await api.get(`/tasks/postback?click_id=${randomTransId}&sub_id=${telegramId}&payout=1.0&token=YOUR_CPA_SECRET_TOKEN`);
                    alert("Simulated Postback Sent! +3 Spins.");
                    window.location.reload(); // Refresh to see spins
                } catch(e) {
                    alert("Error sending postback");
                }
            }}
        >
            [DEV] Force Complete Task
        </button>
      </div>
    </div>
  );
};
