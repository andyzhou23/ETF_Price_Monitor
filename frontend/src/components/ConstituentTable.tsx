import React, { useEffect, useState } from 'react';
import { Table, Card } from 'antd';
import { apiClient, Constituent } from '../api/client';

interface ConstituentTableProps {
  etfId: string;
}

export const ConstituentTable: React.FC<ConstituentTableProps> = ({ etfId }) => {
  const [data, setData] = useState<Constituent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<Constituent[]>(`/etfs/${etfId}/constituents`);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching constituents:', error);
      } finally {
        setLoading(false);
      }
    };
    if (etfId) {
      fetchData();
    }
  }, [etfId]);

  const columns = [
    {
      title: 'Constituent',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: Constituent, b: Constituent) => a.name.localeCompare(b.name),
    },
    {
      title: 'Weight',
      dataIndex: 'weight',
      key: 'weight',
      sorter: (a: Constituent, b: Constituent) => a.weight - b.weight,
      render: (val: number) => val.toFixed(4),
    },
    {
      title: 'Latest Close Price',
      dataIndex: 'latest_price',
      key: 'latest_price',
      sorter: (a: Constituent, b: Constituent) => a.latest_price - b.latest_price,
      render: (val: number) => `$${val.toFixed(2)}`,
    },
  ];

  return (
    <Card title="ETF Constituents" style={{ marginBottom: 20 }}>
      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="name" 
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};
