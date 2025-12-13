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
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-600 dark:text-gray-400">Loading analytics...</div>
            </div>
        );
    }

    if (error || !analytics) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-red-600">{error || 'No analytics data available'}</div>
            </div>
        );
    }

    const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];

    // Prepare data for charts
    const methodData = Object.entries(analytics.method_effectiveness).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
    }));

    const topPatternsData = analytics.top_patterns.slice(0, 10);

    return (
        <div className="space-y-8">
            {/* Method Effectiveness */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <Target className="text-blue-600" size={24} />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Detection Method Effectiveness</h3>
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
                        <Tooltip />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Top Patterns */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <Activity className="text-green-600" size={24} />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Top Detection Patterns</h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topPatternsData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Confidence Distribution */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <TrendingUp className="text-purple-600" size={24} />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Confidence Score Distribution</h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analytics.confidence_distribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="confidence" tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                        <YAxis />
                        <Tooltip labelFormatter={(value) => `Confidence: ${(Number(value) * 100).toFixed(0)}%`} />
                        <Legend />
                        <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <button
                    onClick={loadAnalytics}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                    Refresh Analytics
                </button>
            </div>
        </div>
    );
};

