import React, { useState } from 'react';
import { Layout, Typography, Row, Col } from 'antd';
import { FileUpload } from './components/FileUpload';
import { ConstituentTable } from './components/ConstituentTable';
import { PriceChart } from './components/PriceChart';
import { TopHoldingsChart } from './components/TopHoldingsChart';
import { ETF } from './api/client';

import 'antd/dist/reset.css'; // Add Ant Design reset styles if 5.x

const { Header, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [activeETF, setActiveETF] = useState<ETF | null>(null);

  const handleUploadSuccess = (etf: ETF) => {
    setActiveETF(etf);
  };

  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          ETF Price Monitor
        </Title>
      </Header>
      <Content style={{ padding: '0 50px', marginTop: '20px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Row gutter={16}>
            <Col span={24}>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </Col>
          </Row>

          {activeETF && (
            <>
              <Row gutter={16}>
                <Col span={24}>
                  <Title level={4}>Current Viewing: {activeETF.name}</Title>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <ConstituentTable etfId={activeETF.id} />
                </Col>
                <Col xs={24} lg={12}>
                  <TopHoldingsChart etfId={activeETF.id} />
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={24}>
                  <PriceChart etfId={activeETF.id} />
                </Col>
              </Row>
            </>
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default App;
