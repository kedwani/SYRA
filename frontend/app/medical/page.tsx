'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import {
  getAllergies, createAllergy, deleteAllergy,
  getMedications, createMedication, deleteMedication,
  getConditions, createCondition, deleteCondition,
  getEmergencyContacts, createEmergencyContact, deleteEmergencyContact,
} from '@/lib/api';
import { Allergy, Medication, Condition, EmergencyContact } from '@/types';
import MedicalCard from '@/components/MedicalCard';
import FormInput from '@/components/FormInput';
import FormSelect from '@/components/FormSelect';

const SEVERITY_OPTIONS = [
  { value: 'mild', label: 'Mild' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'severe', label: 'Severe' },
  { value: 'life_threatening', label: 'Life Threatening' },
];

const VISIBILITY_OPTIONS = [
  { value: 'public', label: 'Public' },
  { value: 'medical', label: 'Medical Only' },
  { value: 'private', label: 'Private' },
];

const FREQUENCY_OPTIONS = [
  { value: 'once', label: 'Once daily' },
  { value: 'twice', label: 'Twice daily' },
  { value: 'three_times', label: 'Three times daily' },
  { value: 'daily', label: 'Once daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'as_needed', label: 'As needed' },
];

const RELATIONSHIP_OPTIONS = [
  { value: 'spouse', label: 'Spouse' },
  { value: 'parent', label: 'Parent' },
  { value: 'child', label: 'Child' },
  { value: 'sibling', label: 'Sibling' },
  { value: 'friend', label: 'Friend' },
  { value: 'other', label: 'Other' },
];

function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'life_threatening': return 'red';
    case 'severe': return 'red';
    case 'moderate': return 'yellow';
    default: return 'gray';
  }
}

type FormType = 'allergy' | 'medication' | 'condition' | 'contact' | null;

export default function MedicalPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [allergies, setAllergies] = useState<Allergy[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [activeForm, setActiveForm] = useState<FormType>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Allergy form
  const [allergyName, setAllergyName] = useState('');
  const [allergySeverity, setAllergySeverity] = useState('moderate');
  const [allergyVisibility, setAllergyVisibility] = useState('public');

  // Medication form
  const [medName, setMedName] = useState('');
  const [medDosage, setMedDosage] = useState('');
  const [medFrequency, setMedFrequency] = useState('daily');
  const [medVisibility, setMedVisibility] = useState('public');

  // Condition form
  const [condName, setCondName] = useState('');
  const [condSeverity, setCondSeverity] = useState('moderate');
  const [condVisibility, setCondVisibility] = useState('public');

  // Contact form
  const [contactName, setContactName] = useState('');
  const [contactRelationship, setContactRelationship] = useState('other');
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactPrimary, setContactPrimary] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
      return;
    }
    loadAll();
  }, [router]);

  async function loadAll() {
    try {
      const [a, m, c, ec] = await Promise.all([
        getAllergies(),
        getMedications(),
        getConditions(),
        getEmergencyContacts(),
      ]);
      setAllergies(a);
      setMedications(m);
      setConditions(c);
      setContacts(ec);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setAllergyName('');
    setAllergySeverity('moderate');
    setAllergyVisibility('public');
    setMedName('');
    setMedDosage('');
    setMedFrequency('daily');
    setMedVisibility('public');
    setCondName('');
    setCondSeverity('moderate');
    setCondVisibility('public');
    setContactName('');
    setContactRelationship('other');
    setContactPhone('');
    setContactEmail('');
    setContactPrimary(false);
    setActiveForm(null);
    setError('');
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (activeForm === 'allergy') {
        await createAllergy({ name: allergyName, severity: allergySeverity, visibility: allergyVisibility });
        setAllergies(await getAllergies());
      } else if (activeForm === 'medication') {
        await createMedication({ name: medName, dosage: medDosage, frequency: medFrequency, visibility: medVisibility });
        setMedications(await getMedications());
      } else if (activeForm === 'condition') {
        await createCondition({ name: condName, severity: condSeverity, visibility: condVisibility });
        setConditions(await getConditions());
      } else if (activeForm === 'contact') {
        await createEmergencyContact({
          name: contactName,
          relationship: contactRelationship,
          phone: contactPhone,
          email: contactEmail,
          is_primary: contactPrimary,
        });
        setContacts(await getEmergencyContacts());
      }
      resetForm();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to save';
      setError(message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteAllergy(id: number) {
    await deleteAllergy(id);
    setAllergies(allergies.filter((a) => a.id !== id));
  }

  async function handleDeleteMedication(id: number) {
    await deleteMedication(id);
    setMedications(medications.filter((m) => m.id !== id));
  }

  async function handleDeleteCondition(id: number) {
    await deleteCondition(id);
    setConditions(conditions.filter((c) => c.id !== id));
  }

  async function handleDeleteContact(id: number) {
    await deleteEmergencyContact(id);
    setContacts(contacts.filter((c) => c.id !== id));
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Loading medical data...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Medical Information</h1>

      {error && activeForm && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-4 py-3 mb-4">
          {error}
        </div>
      )}

      {activeForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
          <h2 className="text-sm font-semibold mb-4">
            {activeForm === 'allergy' && 'Add Allergy'}
            {activeForm === 'medication' && 'Add Medication'}
            {activeForm === 'condition' && 'Add Condition'}
            {activeForm === 'contact' && 'Add Emergency Contact'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {activeForm === 'allergy' && (
              <>
                <FormInput label="Allergen" value={allergyName} onChange={setAllergyName} required id="all-name" placeholder="e.g. Peanuts" />
                <FormSelect label="Severity" value={allergySeverity} onChange={setAllergySeverity} options={SEVERITY_OPTIONS} id="all-severity" />
                <FormSelect label="Visibility" value={allergyVisibility} onChange={setAllergyVisibility} options={VISIBILITY_OPTIONS} id="all-vis" />
              </>
            )}
            {activeForm === 'medication' && (
              <>
                <FormInput label="Medication Name" value={medName} onChange={setMedName} required id="med-name" placeholder="e.g. Metformin" />
                <FormInput label="Dosage" value={medDosage} onChange={setMedDosage} required id="med-dosage" placeholder="e.g. 500mg" />
                <FormSelect label="Frequency" value={medFrequency} onChange={setMedFrequency} options={FREQUENCY_OPTIONS} id="med-freq" />
                <FormSelect label="Visibility" value={medVisibility} onChange={setMedVisibility} options={VISIBILITY_OPTIONS} id="med-vis" />
              </>
            )}
            {activeForm === 'condition' && (
              <>
                <FormInput label="Condition Name" value={condName} onChange={setCondName} required id="cond-name" placeholder="e.g. Diabetes Type 2" />
                <FormSelect label="Severity" value={condSeverity} onChange={setCondSeverity} options={SEVERITY_OPTIONS} id="cond-severity" />
                <FormSelect label="Visibility" value={condVisibility} onChange={setCondVisibility} options={VISIBILITY_OPTIONS} id="cond-vis" />
              </>
            )}
            {activeForm === 'contact' && (
              <>
                <FormInput label="Contact Name" value={contactName} onChange={setContactName} required id="ec-name" placeholder="e.g. Jane Doe" />
                <FormSelect label="Relationship" value={contactRelationship} onChange={setContactRelationship} options={RELATIONSHIP_OPTIONS} id="ec-rel" />
                <FormInput label="Phone" type="tel" value={contactPhone} onChange={setContactPhone} required id="ec-phone" placeholder="+1234567890" />
                <FormInput label="Email" type="email" value={contactEmail} onChange={setContactEmail} id="ec-email" placeholder="jane@example.com" />
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={contactPrimary} onChange={(e) => setContactPrimary(e.target.checked)} />
                  <span>Primary contact</span>
                </label>
              </>
            )}

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={saving}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        <MedicalCard
          title="Allergies"
          items={allergies.map((a) => ({
            id: a.id,
            name: a.name,
            subtitle: a.notes || '',
            badge: a.severity.replace('_', ' '),
            badgeColor: getSeverityColor(a.severity),
          }))}
          onAdd={() => setActiveForm('allergy')}
          onDelete={handleDeleteAllergy}
          emptyMessage="No allergies recorded."
        />

        <MedicalCard
          title="Medications"
          items={medications.map((m) => ({
            id: m.id,
            name: m.name,
            subtitle: `${m.dosage} - ${m.frequency.replace('_', ' ')}`,
            badge: m.is_active ? 'Active' : 'Inactive',
            badgeColor: m.is_active ? undefined : 'yellow',
          }))}
          onAdd={() => setActiveForm('medication')}
          onDelete={handleDeleteMedication}
          emptyMessage="No medications recorded."
        />

        <MedicalCard
          title="Conditions"
          items={conditions.map((c) => ({
            id: c.id,
            name: c.name,
            subtitle: c.notes || '',
            badge: c.severity.replace('_', ' '),
            badgeColor: getSeverityColor(c.severity),
          }))}
          onAdd={() => setActiveForm('condition')}
          onDelete={handleDeleteCondition}
          emptyMessage="No conditions recorded."
        />

        <MedicalCard
          title="Emergency Contacts"
          items={contacts.map((c) => ({
            id: c.id,
            name: c.name,
            subtitle: `${c.relationship} - ${c.phone}`,
            badge: c.is_primary ? 'Primary' : undefined,
          }))}
          onAdd={() => setActiveForm('contact')}
          onDelete={handleDeleteContact}
          emptyMessage="No emergency contacts added."
        />
      </div>
    </div>
  );
}
