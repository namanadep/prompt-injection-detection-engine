/**
 * API client for communicating with the backend.
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DetectionResult {
  is_threat: boolean;
  confidence: number;
  threat_level: string;
  explanation: string;
  rule_result: {
    detected: boolean;
    confidence: number;
    matched_patterns: Array<{
      pattern_id: string;
      pattern_name: string;
      severity: string;
      confidence: number;
    }>;
    matched_keywords: string[];
  };
  ml_result: {
    detected: boolean;
    confidence: number;
    model_version: string;
    prediction_label?: string;
  };
  vector_result: {
    detected: boolean;
    confidence: number;
    similar_attacks: Array<{
      attack_id: string;
      text: string;
      category: string;
      severity: string;
      similarity_score: number;
    }>;
  };
  timestamp: string;
  processing_time_ms?: number;
}

export interface DetectionStats {
  total_requests: number;
  threats_detected: number;
  threat_percentage: number;
  avg_confidence: number;
  detection_by_method: Record<string, number>;
  threat_levels: Record<string, number>;
}

export interface AnalyticsData {
  threats_over_time: Array<{
    timestamp: string;
    is_threat: boolean;
    confidence: number;
  }>;
  top_patterns: Array<{
    name: string;
    count: number;
  }>;
  confidence_distribution: Array<{
    confidence: number;
    count: number;
  }>;
  method_effectiveness: Record<string, number>;
}

export interface HealthResponse {
  status: string;
  version: string;
  models_loaded: boolean;
  chroma_connected: boolean;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async detectInjection(text: string): Promise<DetectionResult> {
    const response = await this.client.post<DetectionResult>('/api/v1/detect', {
      text,
    });
    return response.data;
  }

  async detectBatch(texts: string[]): Promise<DetectionResult[]> {
    const response = await this.client.post<DetectionResult[]>('/api/v1/detect/batch', {
      texts,
    });
    return response.data;
  }

  async getStats(): Promise<DetectionStats> {
    const response = await this.client.get<DetectionStats>('/api/v1/stats');
    return response.data;
  }

  async getAnalytics(): Promise<AnalyticsData> {
    const response = await this.client.get<AnalyticsData>('/api/v1/analytics');
    return response.data;
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/api/v1/health');
    return response.data;
  }
}

export const apiClient = new APIClient();

