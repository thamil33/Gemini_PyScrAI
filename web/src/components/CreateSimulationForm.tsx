// Create simulation form

import { useState, useEffect } from 'react';
import { useSimulationStore } from '../stores/simulationStore';
import { api } from '../services/api';

interface ScenarioOption {
  name: string;
  display_name: string;
  description: string;
}

export function CreateSimulationForm() {
  const [name, setName] = useState('');
  const [scenario, setScenario] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState(false);
  const { createSimulation, isFetching } = useSimulationStore();

  useEffect(() => {
    async function fetchScenarios() {
      setLoadingScenarios(true);
      try {
        const response = await api.get<ScenarioOption[]>('/scenarios');
        setScenarios(response.data);
        // Set default scenario to the first one if available
        if (response.data.length > 0 && !scenario) {
          setScenario(response.data[0].name);
        }
      } catch (error) {
        console.error('Failed to fetch scenarios:', error);
        // Fallback to a default if API fails
        setScenarios([{ name: 'simple_town', display_name: 'Simple Town', description: 'A basic town scenario' }]);
        setScenario('simple_town');
      } finally {
        setLoadingScenarios(false);
      }
    }
    
    if (showForm) {
      fetchScenarios();
    }
  }, [showForm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !scenario) return;
    
    await createSimulation(name, scenario);
    setName('');
    setScenario(scenarios.length > 0 ? scenarios[0].name : '');
    setShowForm(false);
  };

  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
      >
        + New Simulation
      </button>
    );
  }

  const selectedScenario = scenarios.find(s => s.name === scenario);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Create New Simulation
      </h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="My Simulation"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Scenario
          </label>
          {loadingScenarios ? (
            <div className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400">
              Loading scenarios...
            </div>
          ) : (
            <>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                required
              >
                {scenarios.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.display_name}
                  </option>
                ))}
              </select>
              {selectedScenario && selectedScenario.description && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {selectedScenario.description}
                </p>
              )}
            </>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={isFetching || loadingScenarios}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md font-medium transition-colors"
          >
            {isFetching ? 'Creating...' : 'Create'}
          </button>
          <button
            type="button"
            onClick={() => setShowForm(false)}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-md font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
