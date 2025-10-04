// Compact action composer for workspace panel

import { ChangeEvent, FormEvent, useState } from 'react';
import { useSimulationStore } from '../stores/simulationStore';

interface ComposerState {
  actorId: string;
  intent: string;
  description: string;
}

const initialState: ComposerState = {
  actorId: '',
  intent: '',
  description: '',
};

export function ActionComposer() {
  const { activeSimulation, submitAction, isActionSubmitting } = useSimulationStore();
  const [form, setForm] = useState<ComposerState>(initialState);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = (field: keyof ComposerState) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm((prev) => ({ ...prev, [field]: event.target.value }));
      if (localError) {
        setLocalError(null);
      }
    };

  const resetForm = () => {
    setForm(initialState);
    setLocalError(null);
  };

  const handleActorSelect = (actorId: string) => {
    setForm((prev) => ({ ...prev, actorId }));
    setLocalError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!activeSimulation) {
      return;
    }

    if (!form.actorId.trim() || !form.intent.trim()) {
      setLocalError('Actor ID and intent are required');
      return;
    }

    try {
      await submitAction(activeSimulation.id, {
        actorId: form.actorId.trim(),
        intent: form.intent.trim(),
        description: form.description.trim() || undefined,
      });
      resetForm();
    } catch (error) {
      setLocalError((error as Error).message);
    }
  };

  if (!activeSimulation) {
    return null;
  }

  return (
    <div>
      {localError && (
        <div className="mb-3 rounded-md border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 px-3 py-2 text-sm text-red-700 dark:text-red-200">
          {localError}
        </div>
      )}

      {/* Quick Actor Selection */}
      {activeSimulation.actors.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick select:
          </p>
          <div className="flex flex-wrap gap-2">
            {activeSimulation.actors.map((actor) => (
              <button
                key={actor.id}
                type="button"
                onClick={() => handleActorSelect(actor.id)}
                className={`px-2 py-1 text-xs rounded-full transition-colors ${
                  form.actorId === actor.id
                    ? 'bg-blue-600 text-white'
                    : 'border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900/40 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                {actor.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <form className="space-y-3" onSubmit={handleSubmit}>
        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Actor ID *
          </label>
          <input
            type="text"
            value={form.actorId}
            onChange={handleChange('actorId')}
            placeholder="actor-id or select above"
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Intent *
          </label>
          <textarea
            value={form.intent}
            onChange={handleChange('intent')}
            placeholder="What should this actor do?"
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description (optional)
          </label>
          <input
            type="text"
            value={form.description}
            onChange={handleChange('description')}
            placeholder="Short summary for researchers"
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
          />
        </div>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={resetForm}
            className="px-3 py-2 text-sm rounded-md bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white transition-colors"
            disabled={isActionSubmitting}
          >
            Clear
          </button>
          <button
            type="submit"
            className="px-3 py-2 text-sm rounded-md bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium transition-colors"
            disabled={isActionSubmitting}
          >
            {isActionSubmitting ? 'Submitting...' : '📤 Submit Action'}
          </button>
        </div>
      </form>
    </div>
  );
}
