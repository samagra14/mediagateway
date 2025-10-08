/**
 * API client for MediaRouter backend
 */

const API_BASE_URL = '/v1';

export interface VideoGenerationRequest {
  model: string;
  prompt: string;
  provider?: string;
  duration?: number;
  aspect_ratio?: string;
  seed?: number;
  fps?: number;
}

export interface VideoGenerationResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  provider: string;
  status: string;
  prompt?: string;
  video?: {
    url?: string;
    duration?: number;
    width?: number;
    height?: number;
  };
  usage?: {
    cost?: number;
    time_seconds?: number;
  };
  error?: string;
  completed_at?: string;
}

export interface APIKeyRequest {
  provider: string;
  api_key: string;
}

export interface APIKeyResponse {
  id: number;
  provider: string;
  status: string;
  last_validated?: string;
  created_at: string;
  key_preview?: string;
}

export interface ProviderInfo {
  name: string;
  display_name: string;
  models: string[];
  features: any;
  has_key: boolean;
  key_status?: string;
}

export interface UsageStatsResponse {
  total_generations: number;
  total_cost: number;
  total_success: number;
  total_failure: number;
  success_rate: number;
  by_provider: any[];
  by_model: any[];
  recent_generations: VideoGenerationResponse[];
}

class API {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Video Generation
  async createVideoGeneration(request: VideoGenerationRequest): Promise<VideoGenerationResponse> {
    return this.request<VideoGenerationResponse>('/video/generations', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getVideoGeneration(generationId: string): Promise<VideoGenerationResponse> {
    return this.request<VideoGenerationResponse>(`/video/generations/${generationId}`);
  }

  async listVideoGenerations(params: {
    skip?: number;
    limit?: number;
    provider?: string;
    status?: string;
  } = {}): Promise<VideoGenerationResponse[]> {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params.provider) queryParams.append('provider', params.provider);
    if (params.status) queryParams.append('status', params.status);

    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request<VideoGenerationResponse[]>(`/video/generations${query}`);
  }

  async deleteVideoGeneration(generationId: string): Promise<void> {
    await this.request(`/video/generations/${generationId}`, {
      method: 'DELETE',
    });
  }

  // API Keys
  async addAPIKey(request: APIKeyRequest): Promise<APIKeyResponse> {
    return this.request<APIKeyResponse>('/keys', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async listAPIKeys(): Promise<APIKeyResponse[]> {
    return this.request<APIKeyResponse[]>('/keys');
  }

  async deleteAPIKey(keyId: number): Promise<void> {
    await this.request(`/keys/${keyId}`, {
      method: 'DELETE',
    });
  }

  async validateAPIKey(keyId: number): Promise<{ valid: boolean; status: string; error?: string }> {
    return this.request(`/keys/${keyId}/validate`, {
      method: 'POST',
    });
  }

  // Providers
  async listProviders(): Promise<ProviderInfo[]> {
    return this.request<ProviderInfo[]>('/providers');
  }

  // Usage Stats
  async getUsageStats(): Promise<UsageStatsResponse> {
    return this.request<UsageStatsResponse>('/usage/stats');
  }
}

export const api = new API();
