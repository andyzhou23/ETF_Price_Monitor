import React, { useState } from 'react';
import { Upload, Button, message, Card } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { apiClient, ETF } from '../api/client';

interface FileUploadProps {
  onUploadSuccess: (etf: ETF) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [loading, setLoading] = useState(false);

  const customRequest = async (options: any) => {
    const { file, onSuccess, onError } = options;
    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await apiClient.post<ETF>('/etfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success(`${file.name} uploaded successfully.`);
      onSuccess(response.data);
      onUploadSuccess(response.data);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Upload failed.';
      message.error(errorMsg);
      onError(new Error(errorMsg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Upload ETF Definition" style={{ marginBottom: 20 }}>
      <Upload customRequest={customRequest} showUploadList={false} accept=".csv">
        <Button icon={<UploadOutlined />} loading={loading}>
          Click to Upload CSV
        </Button>
      </Upload>
      <p style={{ marginTop: 10, color: '#888' }}>
        Please upload a CSV file containing `name` and `weight` columns.
      </p>
    </Card>
  );
};
