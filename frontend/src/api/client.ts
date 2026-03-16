import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export interface Constituent {
  name: string;
  weight: number;
  latest_price: number;
}

export interface PriceHistory {
  date: string;
  price: number;
}

export interface TopHolding {
  name: string;
  weight: number;
  latest_price: number;
  holding_value: number;
}

export interface ETF {
  id: number;
  name: string;
  constituent_count: number;
}
