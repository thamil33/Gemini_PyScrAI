// Action composer form for injecting intents

import { ChangeEvent, FormEvent, useState } from 'react';
import { useSimulationStore } from '../stores/simulationStore';

interface ComposerState {
  actorId: string;
  intent: string;
  description: string;
  metadataText: string;
}

const initialState: ComposerState = {
  actorId: '',
  intent: '',
  description: '',
  metadataText: '',
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

    let metadata: Record<string, unknown> | undefined;
    if (form.metadataText.trim()) {
      try {
        metadata = JSON.parse(form.metadataText.trim());
      } catch (error) {
        setLocalError('Metadata must be valid JSON');
        return;
      }
    }

    try {
      await submitAction(activeSimulation.id, {
        actorId: form.actorId.trim(),
        intent: form.intent.trim(),
        description: form.description.trim() || undefined,
        metadata,
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
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Action Composer</h3>
        {isActionSubmitting && (
          <span className="text-xs text-blue-500 animate-pulse">Submitting...</span>
        )}
      </div>

      {localError && (
        <div className="mb-4 rounded-md border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 px-3 py-2 text-sm text-red-700 dark:text-red-200">
          {localError}
        </div>
      )}

      {activeSimulation.actors.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-2">
            Quick-fill from known actors
          </p>
          <div className="flex flex-wrap gap-2">
            {activeSimulation.actors.map((actor) => (
              <button
                key={actor.id}
                type="button"
                onClick={() => handleActorSelect(actor.id)}
                className="rounded-full border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-900/40 px-3 py-1 text-xs text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
              >
                {actor.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Actor ID
            </label>
            <input
              type="text"
              value={form.actorId}
              onChange={handleChange('actorId')}
              placeholder="actor-npc"
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description (optional)
            </label>
            <input
              type="text"
              value={form.description}
              onChange={handleChange('description')}
              placeholder="Short summary for researchers"
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Intent
          </label>
          <textarea
            value={form.intent}
            onChange={handleChange('intent')}
            placeholder="Describe what the actor intends to do"
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Metadata JSON (optional)
          </label>
          <textarea
            value={form.metadataText}
            onChange={handleChange('metadataText')}
            placeholder='{"channel": "sdr"}'
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white font-mono text-sm"
            rows={3}
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Provide additional context for the engine (parsed as JSON).
          </p>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={resetForm}
            className="px-4 py-2 rounded-md bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white transition-colors"
            disabled={isActionSubmitting}
          >
            Clear
          </button>
          <button
            type="submit"
            className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium transition-colors"
            disabled={isActionSubmitting}
          >
            {isActionSubmitting ? 'Submitting...' : 'Submit Action'}
          </button>
        </div>
      </form>
    </div>
  );
}
