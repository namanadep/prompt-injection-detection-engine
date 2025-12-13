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
            <div className="flex items-center justify-center h-64 clean-card">
                <div className="text-gray-600 font-medium">Loading analytics...</div>
            </div>
        );
    }

    if (error || !analytics) {
        return (
            <div className="flex items-center justify-center h-64 clean-card border-2 border-red-200 bg-red-50">
                <div className="text-red-600 font-medium">
                    Error: {error || 'No analytics data available'}
                </div>
            </div>
        );
    }

    const COLORS = ['#2D5016', '#87CEEB', '#FFD700', '#F97316', '#EF4444'];

    // Prepare data for charts
    const methodData = Object.entries(analytics.method_effectiveness).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
    }));

    const topPatternsData = analytics.top_patterns.slice(0, 10);

    return (
        <div className="space-y-8">
            {/* Method Effectiveness */}
            <div className="clean-card p-8">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#2D5016' }}>
                        <Target className="text-white" size={24} />
                    </div>
                    <h3 className="text-xl font-bold" style={{ color: '#2D5016' }}>Detection Method Effectiveness</h3>
                </div>
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
                                backgroundColor: 'white', 
                                border: '1px solid #E5E5E5',
                                borderRadius: '8px',
                                color: '#2D5016'
                            }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Top Patterns */}
            <div className="clean-card p-8">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#87CEEB' }}>
                        <Activity className="text-white" size={24} />
                    </div>
                    <h3 className="text-xl font-bold" style={{ color: '#2D5016' }}>Top Detection Patterns</h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topPatternsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                        <XAxis 
                            dataKey="name" 
                            angle={-45} 
                            textAnchor="end" 
                            height={100}
                            tick={{ fill: '#666666', fontSize: 12 }}
                        />
                        <YAxis tick={{ fill: '#666666', fontSize: 12 }} />
                        <Tooltip 
                            contentStyle={{ 
                                backgroundColor: 'white', 
                                border: '1px solid #E5E5E5',
                                borderRadius: '8px',
                                color: '#2D5016'
                            }}
                        />
                        <Bar dataKey="count" fill="#2D5016" radius={[8, 8, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Confidence Distribution */}
            <div className="clean-card p-8">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FFD700' }}>
                        <TrendingUp className="text-white" size={24} />
                    </div>
                    <h3 className="text-xl font-bold" style={{ color: '#2D5016' }}>Confidence Score Distribution</h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analytics.confidence_distribution}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                        <XAxis 
                            dataKey="confidence" 
                            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                            tick={{ fill: '#666666', fontSize: 12 }}
                        />
                        <YAxis tick={{ fill: '#666666', fontSize: 12 }} />
                        <Tooltip 
                            contentStyle={{ 
                                backgroundColor: 'white', 
                                border: '1px solid #E5E5E5',
                                borderRadius: '8px',
                                color: '#2D5016'
                            }}
                            labelFormatter={(value) => `Confidence: ${(Number(value) * 100).toFixed(0)}%`}
                        />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey="count" 
                            stroke="#2D5016" 
                            strokeWidth={3}
                            dot={{ fill: '#2D5016', r: 4 }}
                            activeDot={{ r: 6 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <button
                    onClick={loadAnalytics}
                    className="btn-secondary"
                >
                    Refresh Analytics
                </button>
            </div>
        </div>
    );
};

