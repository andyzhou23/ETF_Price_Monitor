import React, { useEffect, useState } from 'react';
import { Card } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Brush
} from 'recharts';
import { apiClient, PriceHistory } from '../api/client';

interface PriceChartProps {
  etfId: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ etfId }) => {
  const [data, setData] = useState<PriceHistory[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<PriceHistory[]>(`/etfs/${etfId}/price-history`);
        const formatted = response.data.map(d => ({
          ...d,
          price: Number(d.price.toFixed(2))
        }));
        setData(formatted);
      } catch (error) {
        console.error('Error fetching price history:', error);
      } finally {
        setLoading(false);
      }
    };
    if (etfId) {
      fetchData();
    }
  }, [etfId]);

  return (
    <Card title="ETF Reconstructed Price History" style={{ marginBottom: 20 }} loading={loading}>
      <div style={{ width: '100%', height: 400 }}>
        {!loading && data.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#999' }}>
            No price history available
          </div>
        ) : (
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip formatter={(value: number) => [`$${value}`, 'Price']} />
            <Line type="monotone" dataKey="price" stroke="#1890ff" dot={false} strokeWidth={2} />
            {data.length > 0 && (
              <Brush
                dataKey="date"
                height={30}
                stroke="#1890ff"
                startIndex={Math.max(0, data.length - 30)}
                endIndex={data.length - 1}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
        )}
      </div>
    </Card>
  );
};
