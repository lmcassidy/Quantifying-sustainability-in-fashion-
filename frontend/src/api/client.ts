import type {
  ProductInput,
  ScoreResponse,
  ProductSummary,
  MaterialReference,
  OriginReference,
  CareReference,
  CertificationReference,
  PricePredictionInput,
  PricePredictionResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    // Handle FastAPI validation errors (detail can be array or string)
    let message = `HTTP ${response.status}`;
    if (typeof error.detail === 'string') {
      message = error.detail;
    } else if (Array.isArray(error.detail) && error.detail.length > 0) {
      message = error.detail.map((e: { msg?: string }) => e.msg || 'Validation error').join(', ');
    }
    throw new Error(message);
  }

  return response.json();
}

// Scoring API
export async function scoreProduct(product: ProductInput): Promise<ScoreResponse> {
  return fetchJson<ScoreResponse>(`${API_BASE}/score`, {
    method: 'POST',
    body: JSON.stringify(product),
  });
}

// Products API
export async function getProducts(limit = 20, offset = 0): Promise<ProductSummary[]> {
  return fetchJson<ProductSummary[]>(
    `${API_BASE}/products?limit=${limit}&offset=${offset}`
  );
}

export async function getProduct(id: number): Promise<ProductSummary> {
  return fetchJson<ProductSummary>(`${API_BASE}/products/${id}`);
}

export async function getCategories(): Promise<string[]> {
  return fetchJson<string[]>(`${API_BASE}/categories`);
}

export async function getRandomProduct(): Promise<ScoreResponse> {
  return fetchJson<ScoreResponse>(`${API_BASE}/products/random`);
}

// Reference Data API
export async function getMaterials(): Promise<MaterialReference[]> {
  return fetchJson<MaterialReference[]>(`${API_BASE}/reference/materials`);
}

export async function getOrigins(): Promise<OriginReference[]> {
  return fetchJson<OriginReference[]>(`${API_BASE}/reference/origins`);
}

export async function getCareInstructions(): Promise<CareReference[]> {
  return fetchJson<CareReference[]>(`${API_BASE}/reference/care`);
}

export async function getCertifications(): Promise<CertificationReference[]> {
  return fetchJson<CertificationReference[]>(`${API_BASE}/reference/certifications`);
}

// Price Prediction API
export async function predictPrice(
  input: PricePredictionInput
): Promise<PricePredictionResponse> {
  return fetchJson<PricePredictionResponse>(`${API_BASE}/predict-price`, {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

// Health Check
export async function checkHealth(): Promise<{ status: string }> {
  const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';
  return fetchJson<{ status: string }>(`${baseUrl}/health`);
}
