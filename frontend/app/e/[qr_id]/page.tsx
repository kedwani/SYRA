'use client';

import { useEffect, useState } from 'react';
import { getEmergencyData, getEmergencyCritical, getEmergencyExtended } from '@/lib/api';
import { EmergencyData, EmergencyCriticalData, EmergencyExtendedData } from '@/types';

type ViewMode = 'basic' | 'critical' | 'extended';

export default function EmergencyPage({ params }: { params: Promise<{ qr_id: string }> }) {
  const [qrId, setQrId] = useState<string>('');
  const [mode, setMode] = useState<ViewMode>('basic');
  const [basicData, setBasicData] = useState<EmergencyData | null>(null);
  const [criticalData, setCriticalData] = useState<EmergencyCriticalData | null>(null);
  const [extendedData, setExtendedData] = useState<EmergencyExtendedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    params.then((p) => setQrId(p.qr_id));
  }, [params]);

  useEffect(() => {
    if (!qrId) return;

    async function fetchData() {
      try {
        const basic = await getEmergencyData(qrId);
        setBasicData(basic);
      } catch {
        setError('Could not load emergency information. The QR code may be invalid or expired.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [qrId]);

  const loadCritical = async () => {
    setLoading(true);
    try {
      const data = await getEmergencyCritical(qrId);
      setCriticalData(data);
      setMode('critical');
    } catch {
      setError('Could not load critical data.');
    } finally {
      setLoading(false);
    }
  };

  const loadExtended = async () => {
    setLoading(true);
    try {
      const data = await getEmergencyExtended(qrId);
      setExtendedData(data);
      setMode('extended');
    } catch {
      setError('Could not load extended data.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">&#9764;</div>
          <p className="text-gray-500 text-lg">Loading emergency data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">&#9888;</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Error</h1>
          <p className="text-lg text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  // Extended view
  if (mode === 'extended' && extendedData) {
    return (
      <div className="min-h-screen bg-white">
        <div className="bg-red-600 text-white px-4 py-6 text-center">
          <h1 className="text-2xl font-bold">SYRA Emergency Card</h1>
          <p className="text-sm mt-1 opacity-80">Extended Medical Information</p>
        </div>

        <div className="max-w-2xl mx-auto px-4 py-6">
          {/* Patient Info */}
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">{extendedData.profile.full_name}</h2>
            {extendedData.profile.date_of_birth && (
              <p className="text-sm text-gray-500">
                DOB: {new Date(extendedData.profile.date_of_birth).toLocaleDateString()}
              </p>
            )}
            <div className="mt-3 inline-block bg-red-100 text-red-800 px-6 py-3 rounded-lg">
              <span className="text-5xl font-black">{extendedData.profile.blood_type || '???'}</span>
              <p className="text-xs font-semibold mt-1">BLOOD TYPE</p>
            </div>
          </div>

          {/* Emergency Note */}
          {extendedData.emergency_note && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <p className="text-sm font-semibold text-yellow-800">Note</p>
              <p className="text-yellow-900">{extendedData.emergency_note}</p>
            </div>
          )}

          {/* Allergies */}
          <Section title="ALLERGIES" color="red">
            {extendedData.allergies.length === 0 ? (
              <p className="text-gray-500 text-sm">No known allergies</p>
            ) : (
              extendedData.allergies.map((a, i) => (
                <ItemRow key={i} name={a.name} badge={a.severity} color="red" />
              ))
            )}
          </Section>

          {/* Medications */}
          <Section title="MEDICATIONS" color="blue">
            {extendedData.medications.length === 0 ? (
              <p className="text-gray-500 text-sm">No medications listed</p>
            ) : (
              extendedData.medications.map((m, i) => (
                <ItemRow key={i} name={m.name} detail={`${m.dosage} - ${m.frequency}`} />
              ))
            )}
          </Section>

          {/* Conditions */}
          <Section title="CONDITIONS" color="orange">
            {extendedData.conditions.length === 0 ? (
              <p className="text-gray-500 text-sm">No conditions listed</p>
            ) : (
              extendedData.conditions.map((c, i) => (
                <ItemRow key={i} name={c.name} badge={c.severity} color={c.severity === 'life_threatening' || c.severity === 'severe' ? 'red' : 'yellow'} />
              ))
            )}
          </Section>

          {/* Emergency Contacts */}
          <Section title="EMERGENCY CONTACTS" color="green">
            {extendedData.emergency_contacts.length === 0 ? (
              <p className="text-gray-500 text-sm">No emergency contacts</p>
            ) : (
              extendedData.emergency_contacts.map((c, i) => (
                <div key={i} className="py-2 border-b border-gray-100 last:border-0">
                  <p className="font-semibold text-lg">{c.name}</p>
                  <p className="text-sm text-gray-600">{c.relationship}</p>
                  <a href={`tel:${c.phone}`} className="text-lg font-bold text-blue-600 block mt-1">
                    {c.phone}
                  </a>
                  {c.email && (
                    <a href={`mailto:${c.email}`} className="text-sm text-blue-600">
                      {c.email}
                    </a>
                  )}
                </div>
              ))
            )}
          </Section>

          {extendedData.last_updated && (
            <p className="text-xs text-gray-400 mt-6">
              Last updated: {new Date(extendedData.last_updated).toLocaleString()}
            </p>
          )}

          <button
            onClick={() => setMode('basic')}
            className="mt-4 text-sm text-gray-500 underline"
          >
            Back to basic view
          </button>
        </div>
      </div>
    );
  }

  // Critical view
  if (mode === 'critical' && criticalData) {
    return (
      <div className="min-h-screen bg-white">
        <div className="bg-red-600 text-white px-4 py-6 text-center">
          <h1 className="text-2xl font-bold">SYRA Emergency Card</h1>
          <p className="text-sm mt-1 opacity-80">Critical Information</p>
        </div>

        <div className="max-w-2xl mx-auto px-4 py-6">
          {/* Blood Type - Large */}
          <div className="text-center my-6">
            <div className="inline-block bg-red-100 text-red-800 px-8 py-4 rounded-lg">
              <span className="text-6xl font-black">{criticalData.blood_type || '???'}</span>
              <p className="text-sm font-semibold mt-1">BLOOD TYPE</p>
            </div>
          </div>

          {/* Emergency Note */}
          {criticalData.emergency_note && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <p className="text-yellow-900">{criticalData.emergency_note}</p>
            </div>
          )}

          {/* Critical Allergies */}
          <div className="mb-6">
            <h2 className="text-lg font-black text-red-700 mb-2 uppercase">Allergies</h2>
            {criticalData.allergies.length === 0 ? (
              <p className="text-gray-500">No severe allergies on record</p>
            ) : (
              <div className="space-y-2">
                {criticalData.allergies.map((a, i) => (
                  <div key={i} className="bg-red-50 border border-red-200 rounded px-4 py-3">
                    <span className="text-xl font-bold text-red-800">{a.name}</span>
                    <span className="ml-3 text-sm text-red-600 font-semibold uppercase">{a.severity.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Critical Conditions */}
          <div className="mb-6">
            <h2 className="text-lg font-black text-orange-700 mb-2 uppercase">Critical Conditions</h2>
            {criticalData.critical_conditions.length === 0 ? (
              <p className="text-gray-500">No critical conditions on record</p>
            ) : (
              <div className="space-y-2">
                {criticalData.critical_conditions.map((c, i) => (
                  <div key={i} className="bg-orange-50 border border-orange-200 rounded px-4 py-3">
                    <span className="text-xl font-bold text-orange-800">{c.name}</span>
                    <span className="ml-3 text-sm text-orange-600 font-semibold uppercase">{c.severity.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={loadExtended}
              className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium"
            >
              Load Extended Info
            </button>
            <button
              onClick={() => setMode('basic')}
              className="text-sm text-gray-500 underline"
            >
              Basic View
            </button>
          </div>

          {criticalData.last_updated && (
            <p className="text-xs text-gray-400 mt-4">
              Last updated: {new Date(criticalData.last_updated).toLocaleString()}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Basic view (default)
  return (
    <div className="min-h-screen bg-white">
      <div className="bg-red-600 text-white px-4 py-6 text-center">
        <h1 className="text-2xl font-bold">SYRA Emergency Card</h1>
        <p className="text-sm mt-1 opacity-80">Medical Emergency Information</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Name */}
        <h2 className="text-3xl font-bold text-gray-900 mb-2">{basicData?.name}</h2>

        {/* Blood Type - Large */}
        <div className="text-center my-6">
          <div className="inline-block bg-red-100 text-red-800 px-8 py-4 rounded-lg">
            <span className="text-7xl font-black">{basicData?.blood_type || '???'}</span>
            <p className="text-sm font-semibold mt-1">BLOOD TYPE</p>
          </div>
        </div>

        {/* Emergency Note */}
        {basicData?.emergency_note && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-900 text-lg">{basicData.emergency_note}</p>
          </div>
        )}

        <div className="flex gap-3 mt-8">
          <button
            onClick={loadCritical}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg text-sm font-bold uppercase"
          >
            Load Critical Data
          </button>
          <button
            onClick={loadExtended}
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-6 py-3 rounded-lg text-sm font-medium"
          >
            Full Medical Info
          </button>
        </div>
      </div>
    </div>
  );
}

function Section({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  const colors: Record<string, string> = {
    red: 'text-red-700 border-red-200',
    blue: 'text-blue-700 border-blue-200',
    orange: 'text-orange-700 border-orange-200',
    green: 'text-green-700 border-green-200',
  };
  return (
    <div className="mb-6">
      <h2 className={`text-lg font-black uppercase mb-2 ${colors[color]?.split(' ')[0] || 'text-gray-700'}`}>
        {title}
      </h2>
      <div className={`border rounded-lg p-4 ${colors[color]?.split(' ')[1] || 'border-gray-200'} border`}>
        {children}
      </div>
    </div>
  );
}

function ItemRow({ name, detail, badge, color }: { name: string; detail?: string; badge?: string; color?: string }) {
  const badgeColors: Record<string, string> = {
    red: 'bg-red-100 text-red-700',
    yellow: 'bg-yellow-100 text-yellow-700',
  };
  return (
    <div className="py-2 border-b border-gray-100 last:border-0 flex items-center justify-between">
      <div>
        <span className="font-semibold text-lg">{name}</span>
        {detail && <span className="text-sm text-gray-500 ml-2">{detail}</span>}
      </div>
      {badge && (
        <span className={`text-xs px-2 py-1 rounded-full font-semibold uppercase ${badgeColors[color || 'red'] || 'bg-gray-100 text-gray-700'}`}>
          {badge.replace('_', ' ')}
        </span>
      )}
    </div>
  );
}
