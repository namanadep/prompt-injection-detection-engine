/**
 * Analytics dashboard component with charts.
 */
import React, { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AnalyticsData, apiClient } from '../services/api';
import { TrendingUp, Activity, Target } from 'lucide-react';

export const AnalyticsDashboard: React.FC = () => {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        try {
            setLoading(true);
            const data = await apiClient.getAnalytics();
            setAnalytics(data);
            setError(null);
        } catch (err) {
            setError('Failed to load analytics data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64 border-2 border-yellow-400/30 bg-black/60">
                <div className="text-yellow-400 font-mono text-sm neon-glow">LOADING ANALYTICS...</div>
            </div>
        );
    }

    if (error || !analytics) {
        return (
            <div className="flex items-center justify-center h-64 border-2 border-red-400/30 bg-black/60" style={{ borderColor: 'rgba(255, 0, 0, 0.3)' }}>
                <div className="text-red-400 font-mono text-sm neon-glow" style={{ color: '#FF0000' }}>
                    ERROR: {error || 'NO ANALYTICS DATA AVAILABLE'}
                </div>
            </div>
        );
    }

    const COLORS = ['#FFD700', '#FF0000', '#00FF41', '#00FFFF', '#FF00FF'];

    // Prepare data for charts
    const methodData = Object.entries(analytics.method_effectiveness).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
    }));

    const topPatternsData = analytics.top_patterns.slice(0, 10);

    return (
        <div className="space-y-8">
            {/* Method Effectiveness */}
            <div className="border-2 border-yellow-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(255, 215, 0, 0.3)' }}>
                <div className="border-b-2 border-yellow-400/30 px-4 py-3 flex items-center space-x-2" style={{ borderColor: 'rgba(255, 215, 0, 0.3)' }}>
                    <Target className="text-yellow-400" size={20} />
                    <h3 className="text-sm font-mono uppercase tracking-wider text-yellow-400 neon-glow">METHOD EFFECTIVENESS</h3>
                </div>
                <div className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={methodData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {methodData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip 
                                contentStyle={{ 
                                    backgroundColor: '#000000', 
                                    border: '2px solid #FFD700',
                                    color: '#FFD700',
                                    fontFamily: 'monospace'
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Top Patterns */}
            <div className="border-2 border-cyan-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(0, 255, 255, 0.3)' }}>
                <div className="border-b-2 border-cyan-400/30 px-4 py-3 flex items-center space-x-2" style={{ borderColor: 'rgba(0, 255, 255, 0.3)' }}>
                    <Activity className="text-cyan-400" size={20} style={{ color: '#00FFFF' }} />
                    <h3 className="text-sm font-mono uppercase tracking-wider text-cyan-400 neon-glow" style={{ color: '#00FFFF' }}>TOP DETECTION PATTERNS</h3>
                </div>
                <div className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={topPatternsData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#00FFFF" opacity={0.2} />
                            <XAxis 
                                dataKey="name" 
                                angle={-45} 
                                textAnchor="end" 
                                height={100}
                                tick={{ fill: '#00FFFF', fontFamily: 'monospace', fontSize: 10 }}
                            />
                            <YAxis tick={{ fill: '#00FFFF', fontFamily: 'monospace', fontSize: 10 }} />
                            <Tooltip 
                                contentStyle={{ 
                                    backgroundColor: '#000000', 
                                    border: '2px solid #00FFFF',
                                    color: '#00FFFF',
                                    fontFamily: 'monospace'
                                }}
                            />
                            <Bar dataKey="count" fill="#00FFFF" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Confidence Distribution */}
            <div className="border-2 border-green-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(0, 255, 65, 0.3)' }}>
                <div className="border-b-2 border-green-400/30 px-4 py-3 flex items-center space-x-2" style={{ borderColor: 'rgba(0, 255, 65, 0.3)' }}>
                    <TrendingUp className="text-green-400" size={20} style={{ color: '#00FF41' }} />
                    <h3 className="text-sm font-mono uppercase tracking-wider text-green-400 neon-glow" style={{ color: '#00FF41' }}>CONFIDENCE DISTRIBUTION</h3>
                </div>
                <div className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={analytics.confidence_distribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#00FF41" opacity={0.2} />
                            <XAxis 
                                dataKey="confidence" 
                                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                                tick={{ fill: '#00FF41', fontFamily: 'monospace', fontSize: 10 }}
                            />
                            <YAxis tick={{ fill: '#00FF41', fontFamily: 'monospace', fontSize: 10 }} />
                            <Tooltip 
                                contentStyle={{ 
                                    backgroundColor: '#000000', 
                                    border: '2px solid #00FF41',
                                    color: '#00FF41',
                                    fontFamily: 'monospace'
                                }}
                                labelFormatter={(value) => `CONFIDENCE: ${(Number(value) * 100).toFixed(0)}%`}
                            />
                            <Legend 
                                wrapperStyle={{ color: '#00FF41', fontFamily: 'monospace' }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="count" 
                                stroke="#00FF41" 
                                strokeWidth={2}
                                dot={{ fill: '#00FF41' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <button
                    onClick={loadAnalytics}
                    className="px-6 py-3 bg-yellow-400/20 border-2 border-yellow-400 text-yellow-400 font-mono text-sm hover:bg-yellow-400/30 transition-all neon-border glitch"
                    style={{ borderColor: '#FFD700', color: '#FFD700' }}
                >
                    REFRESH ANALYTICS
                </button>
            </div>
        </div>
    );
};

