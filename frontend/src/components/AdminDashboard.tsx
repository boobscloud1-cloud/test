import { useEffect, useState } from 'react';
import { getAdminStats, createAdminTask, addAdminSpins } from '../requests/api';

interface AdminStats {
    total_users: number;
    total_tasks_completed: number;
    total_spins_consumed: number;
    estimated_revenue: number;
}

export const AdminDashboard = ({ telegramId }: { telegramId: number }) => {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    // Forms
    const [userIdToCredit, setUserIdToCredit] = useState('');
    const [spinsToCredit, setSpinsToCredit] = useState(10);
    
    const [newTaskName, setNewTaskName] = useState('');
    const [newTaskCpaId, setNewTaskCpaId] = useState('');
    const [newTaskSpins, setNewTaskSpins] = useState(1);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getAdminStats(telegramId);
                setStats(data);
            } catch (e: any) {
                setError("Failed to load stats. Are you admin?");
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, [telegramId]);

    const handleAddSpins = async () => {
        if (!userIdToCredit) return;
        try {
            await addAdminSpins(telegramId, parseInt(userIdToCredit), spinsToCredit);
            alert("Spins added!");
        } catch (e) {
            alert("Failed to add spins");
        }
    };

    const handleCreateTask = async () => {
        try {
            await createAdminTask(telegramId, {
                name: newTaskName,
                cpa_network_id: newTaskCpaId,
                reward_spins: newTaskSpins,
                is_active: true
            });
            alert("Task created!");
        } catch (e) {
            alert("Error creating task");
        }
    };

    if (loading) return <div>Loading Admin Panel...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="admin-dashboard">
            <h2>Admin Dashboard</h2>
            
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Users</h3>
                    <p>{stats?.total_users}</p>
                </div>
                <div className="stat-card">
                    <h3>Tasks Done</h3>
                    <p>{stats?.total_tasks_completed}</p>
                </div>
                <div className="stat-card">
                    <h3>Spins Used</h3>
                    <p>{stats?.total_spins_consumed}</p>
                </div>
                <div className="stat-card">
                    <h3>Est. Revenue</h3>
                    <p>${stats?.estimated_revenue.toFixed(2)}</p>
                </div>
            </div>

            <hr />

            <div className="admin-section">
                <h3>Manage Users</h3>
                <input 
                    placeholder="User ID" 
                    value={userIdToCredit}
                    onChange={(e) => setUserIdToCredit(e.target.value)}
                />
                <input 
                    type="number" 
                    placeholder="Spins" 
                    value={spinsToCredit}
                    onChange={(e) => setSpinsToCredit(parseInt(e.target.value))}
                />
                <button onClick={handleAddSpins}>Add Spins</button>
            </div>

            <hr />

            <div className="admin-section">
                <h3>Create Task</h3>
                <input 
                    placeholder="Task Name" 
                    value={newTaskName}
                    onChange={(e) => setNewTaskName(e.target.value)}
                />
                <input 
                    placeholder="CPA/Network ID" 
                    value={newTaskCpaId}
                    onChange={(e) => setNewTaskCpaId(e.target.value)}
                />
                <input 
                    type="number"
                    placeholder="Reward Spins"
                    value={newTaskSpins}
                    onChange={(e) => setNewTaskSpins(parseInt(e.target.value))}
                />
                {/* Note: CPA Payout field could be added if supported by backend schema */}
                <button onClick={handleCreateTask}>Create Task</button>
            </div>
            
            <style>{`
                .admin-dashboard { padding: 20px; color: white; }
                .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
                .stat-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; }
                .admin-section { margin-bottom: 20px; }
                .admin-section input { display: block; margin: 10px 0; padding: 8px; width: 100%; color: black;}
                .admin-section button { background: #4caf50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            `}</style>
        </div>
    );
};
