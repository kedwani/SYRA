import {
  AuthResponse,
  User,
  MedicalProfile,
  Allergy,
  Medication,
  Condition,
  EmergencyContact,
  EmergencyData,
  EmergencyCriticalData,
  EmergencyExtendedData,
  Bracelet,
  QRCodeData,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      data?.detail || data?.error || data?.non_field_errors?.[0] || `Request failed with status ${response.status}`,
      response.status,
      data
    );
  }

  return data as T;
}

// Auth
export async function login(email: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>('/api/v1/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function register(data: {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone: string;
  date_of_birth: string;
  blood_type: string;
  agreed_to_terms: boolean;
  privacy_consent: boolean;
}): Promise<AuthResponse> {
  return request<AuthResponse>('/api/v1/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function refreshToken(refresh: string): Promise<{ access: string }> {
  return request<{ access: string }>('/api/v1/auth/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  });
}

// Profile
export async function getMyProfile(): Promise<MedicalProfile> {
  return request<MedicalProfile>('/api/v1/profiles/me/');
}

export async function updateMyProfile(data: Partial<MedicalProfile>): Promise<MedicalProfile> {
  return request<MedicalProfile>('/api/v1/profiles/me/', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getQRCode(): Promise<QRCodeData> {
  return request<QRCodeData>('/api/v1/profiles/qr/');
}

export async function getPublicProfile(qrId: string): Promise<EmergencyData> {
  return request<EmergencyData>(`/api/v1/profiles/${qrId}/`);
}

// Medical - Allergies
export async function getAllergies(): Promise<Allergy[]> {
  return request<Allergy[]>('/api/v1/medical/allergies/');
}

export async function createAllergy(data: {
  name: string;
  severity: string;
  visibility: string;
  notes?: string;
}): Promise<Allergy> {
  return request<Allergy>('/api/v1/medical/allergies/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateAllergy(
  id: number,
  data: Partial<Allergy>
): Promise<Allergy> {
  return request<Allergy>(`/api/v1/medical/allergies/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteAllergy(id: number): Promise<void> {
  return request<void>(`/api/v1/medical/allergies/${id}/`, {
    method: 'DELETE',
  });
}

// Medical - Medications
export async function getMedications(): Promise<Medication[]> {
  return request<Medication[]>('/api/v1/medical/medications/');
}

export async function createMedication(data: {
  name: string;
  dosage: string;
  frequency: string;
  visibility: string;
  prescribed_by?: string;
  reason?: string;
}): Promise<Medication> {
  return request<Medication>('/api/v1/medical/medications/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateMedication(
  id: number,
  data: Partial<Medication>
): Promise<Medication> {
  return request<Medication>(`/api/v1/medical/medications/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteMedication(id: number): Promise<void> {
  return request<void>(`/api/v1/medical/medications/${id}/`, {
    method: 'DELETE',
  });
}

// Medical - Conditions
export async function getConditions(): Promise<Condition[]> {
  return request<Condition[]>('/api/v1/medical/conditions/');
}

export async function createCondition(data: {
  name: string;
  severity: string;
  visibility: string;
  diagnosed_date?: string;
  notes?: string;
}): Promise<Condition> {
  return request<Condition>('/api/v1/medical/conditions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCondition(
  id: number,
  data: Partial<Condition>
): Promise<Condition> {
  return request<Condition>(`/api/v1/medical/conditions/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteCondition(id: number): Promise<void> {
  return request<void>(`/api/v1/medical/conditions/${id}/`, {
    method: 'DELETE',
  });
}

// Medical - Emergency Contacts
export async function getEmergencyContacts(): Promise<EmergencyContact[]> {
  return request<EmergencyContact[]>('/api/v1/medical/emergency-contacts/');
}

export async function createEmergencyContact(data: {
  name: string;
  relationship: string;
  phone: string;
  email?: string;
  is_primary?: boolean;
}): Promise<EmergencyContact> {
  return request<EmergencyContact>('/api/v1/medical/emergency-contacts/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateEmergencyContact(
  id: number,
  data: Partial<EmergencyContact>
): Promise<EmergencyContact> {
  return request<EmergencyContact>(`/api/v1/medical/emergency-contacts/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteEmergencyContact(id: number): Promise<void> {
  return request<void>(`/api/v1/medical/emergency-contacts/${id}/`, {
    method: 'DELETE',
  });
}

// Emergency
export async function getEmergencyData(qrHash: string): Promise<EmergencyData> {
  return request<EmergencyData>(`/api/v1/e/${qrHash}/`);
}

export async function getEmergencyCritical(qrHash: string): Promise<EmergencyCriticalData> {
  return request<EmergencyCriticalData>(`/api/v1/e/${qrHash}/critical/`);
}

export async function getEmergencyExtended(qrHash: string): Promise<EmergencyExtendedData> {
  return request<EmergencyExtendedData>(`/api/v1/e/${qrHash}/extended/`);
}

// Bracelets
export async function getMyBracelets(): Promise<Bracelet[]> {
  return request<Bracelet[]>('/api/v1/bracelets/');
}

export async function claimBracelet(data: {
  serial_number: string;
  claim_pin: string;
}): Promise<{ message: string; bracelet: Bracelet }> {
  return request<{ message: string; bracelet: Bracelet }>('/api/v1/bracelets/claim/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
