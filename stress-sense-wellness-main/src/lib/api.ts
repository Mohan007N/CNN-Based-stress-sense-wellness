/**
 * API utility for StressSense backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  department?: string;
  position?: string;
}

export interface AuthResponse {
  success: boolean;
  message?: string;
  access_token?: string;
  refresh_token?: string;
  user?: {
    id: number;
    full_name: string;
    email: string;
    role: string;
    department?: string;
    position?: string;
    created_at: string;
    last_login?: string;
  };
  error?: string;
}

/**
 * Login user
 */
export async function loginUser(data: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();
  return result;
}

/**
 * Register new user
 */
export async function registerUser(data: RegisterRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();
  return result;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(token: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const result = await response.json();
  return result;
}

/**
 * Logout user (client-side token removal)
 */
export function logoutUser(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

/**
 * Get stored access token
 */
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

/**
 * Store authentication data
 */
export function storeAuthData(accessToken: string, refreshToken: string, user: any): void {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
