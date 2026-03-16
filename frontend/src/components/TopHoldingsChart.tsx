import React, { useEffect, useState } from 'react';
import { Card } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { apiClient, TopHolding } from '../api/client';

interface TopHoldingsChartProps {
  etfId: string;
}

const COLORS = ['#1890ff', '#13c2c2', '#52c41a', '#fadb14', '#fa8c16'];

export const TopHoldingsChart: React.FC<TopHoldingsChartProps> = ({ etfId }) => {
  const [data, setData] = useState<TopHolding[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<TopHolding[]>(`/etfs/${etfId}/top-holdings`);
        const formatted = response.data.map(d => ({
          ...d,
          holding_value: Number(d.holding_value.toFixed(2))
        }));
        setData(formatted);
      } catch (error) {
        console.error('Error fetching top holdings:', error);
      } finally {
        setLoading(false);
      }
    };
    if (etfId) {
      fetchData();
    }
  }, [etfId]);

  return (
    <Card title="Top 5 Holdings by Value" style={{ marginBottom: 20 }} loading={loading}>
      <div style={{ width: '100%', height: 400 }}>
        {!loading && data.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#999' }}>
            No holdings data available
          </div>
        ) : (
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value: number) => [`$${value}`, 'Holding Value']} />
            <Bar dataKey="holding_value">
              {data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        )}
      </div>
    </Card>
  );
};
