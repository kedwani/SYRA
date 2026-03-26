// SYRA Frontend TypeScript Types

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  date_of_birth: string | null;
  blood_type: string;
  avatar: string;
  is_medical_personnel: boolean;
  medical_license_number: string;
  hospital_name: string;
  hospital_verified: boolean;
  subscription_type: string;
  agreed_to_terms: boolean;
  privacy_consent: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface MedicalProfile {
  id: string;
  user: User;
  qr_token: string;
  qr_token_hash: string;
  qr_url: string;
  default_visibility: string;
  is_active: boolean;
  emergency_note: string;
  created_at: string;
  updated_at: string;
  last_accessed_at: string | null;
}

export interface Allergy {
  id: number;
  name: string;
  severity: string;
  visibility: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface Medication {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  visibility: string;
  prescribed_by: string;
  reason: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Condition {
  id: number;
  name: string;
  severity: string;
  visibility: string;
  diagnosed_date: string | null;
  notes: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContact {
  id: number;
  name: string;
  relationship: string;
  phone: string;
  email: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmergencyData {
  name: string;
  blood_type: string;
  emergency_note: string;
}

export interface EmergencyCriticalData {
  blood_type: string;
  allergies: { name: string; severity: string }[];
  critical_conditions: { name: string; severity: string }[];
  emergency_note: string;
  last_updated: string | null;
}

export interface EmergencyExtendedData {
  profile: {
    full_name: string;
    date_of_birth: string | null;
    blood_type: string;
  };
  allergies: { name: string; severity: string; visibility: string }[];
  medications: { name: string; dosage: string; frequency: string; visibility: string }[];
  conditions: { name: string; severity: string; visibility: string }[];
  emergency_contacts: { name: string; relationship: string; phone: string; email: string }[];
  emergency_note: string;
  last_updated: string | null;
}

export interface Bracelet {
  id: number;
  serial_number: string;
  qr_token: string;
  status: string;
  profile: string;
  ordered_at: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
  claimed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface QRCodeData {
  qr_token_hash: string;
  qr_url: string;
  qr_image: string;
}
