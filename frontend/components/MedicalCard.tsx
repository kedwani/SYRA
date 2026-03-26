'use client';

import { useState } from 'react';

interface MedicalCardProps {
  title: string;
  items: {
    id: number;
    name: string;
    subtitle?: string;
    badge?: string;
    badgeColor?: string;
  }[];
  onAdd?: () => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  emptyMessage?: string;
}

export default function MedicalCard({
  title,
  items,
  onAdd,
  onEdit,
  onDelete,
  emptyMessage = 'No items added yet.',
}: MedicalCardProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (id: number) => {
    if (!onDelete) return;
    setDeletingId(id);
    try {
      await onDelete(id);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        {onAdd && (
          <button
            onClick={onAdd}
            className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
          >
            + Add
          </button>
        )}
      </div>
      <div className="divide-y divide-gray-100">
        {items.length === 0 ? (
          <p className="px-4 py-4 text-sm text-gray-500">{emptyMessage}</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="px-4 py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{item.name}</p>
                {item.subtitle && (
                  <p className="text-xs text-gray-500">{item.subtitle}</p>
                )}
              </div>
              <div className="flex items-center gap-2">
                {item.badge && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      item.badgeColor === 'red'
                        ? 'bg-red-100 text-red-700'
                        : item.badgeColor === 'yellow'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                {onEdit && (
                  <button
                    onClick={() => onEdit(item.id)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Edit
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={() => handleDelete(item.id)}
                    disabled={deletingId === item.id}
                    className="text-xs text-red-600 hover:text-red-800 disabled:opacity-50"
                  >
                    {deletingId === item.id ? '...' : 'Delete'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
