import React, { useState, useEffect } from 'react';
import { useSimulationStore } from '../stores/simulationStore';

interface ActorManagerProps {
  simulationId?: string;
}

interface Actor {
  id: string;
  name: string;
  type: string;
  active: boolean;
  last_updated: string | null;
  attributes: Record<string, any>;
  location?: Record<string, any>;
  metadata: Record<string, any>;
  created_at?: string;
}

interface ActorFormData {
  name: string;
  type: string;
  attributes: Record<string, any>;
  location?: Record<string, any>;
  metadata: Record<string, any>;
}

export function ActorManager({ simulationId }: ActorManagerProps = {}) {
  const { activeSimulation, createActor, updateActor, deleteActor, selectSimulation } = useSimulationStore();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingActor, setEditingActor] = useState<Actor | null>(null);
  const [formData, setFormData] = useState<ActorFormData>({
    name: '',
    type: 'npc',
    attributes: {},
    metadata: {}
  });

  // Get actors from the active simulation
  const actors: Actor[] = activeSimulation?.actors.map(actor => ({
    ...actor,
    attributes: {},
    metadata: {},
    active: true,
    last_updated: null,
    location: actor.location || undefined
  })) || [];

  // Reload simulation when simulationId changes
  useEffect(() => {
    if (simulationId && (!activeSimulation || activeSimulation.id !== simulationId)) {
      selectSimulation(simulationId);
    }
  }, [simulationId, activeSimulation, selectSimulation]);

  const handleCreateActor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createActor(formData);
      setShowCreateForm(false);
      setFormData({ name: '', type: 'npc', attributes: {}, metadata: {} });
    } catch (error) {
      console.error('Failed to create actor:', error);
    }
  };

  const handleUpdateActor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingActor) return;

    try {
      await updateActor(editingActor.id, formData);
      setEditingActor(null);
      setFormData({ name: '', type: 'npc', attributes: {}, metadata: {} });
      // Refresh simulation to get updated actors list
      if (simulationId) {
        await selectSimulation(simulationId);
      }
    } catch (error) {
      console.error('Failed to update actor:', error);
    }
  };

  const handleDeleteActor = async (actorId: string) => {
    if (!confirm('Are you sure you want to delete this actor?')) return;

    try {
      await deleteActor(actorId);
      // Refresh simulation to get updated actors list
      if (simulationId) {
        await selectSimulation(simulationId);
      }
    } catch (error) {
      console.error('Failed to delete actor:', error);
    }
  };

  const startEdit = (actor: Actor) => {
    setEditingActor(actor);
    setFormData({
      name: actor.name,
      type: actor.type,
      attributes: actor.attributes || {},
      location: actor.location,
      metadata: actor.metadata || {}
    });
  };

  const cancelEdit = () => {
    setEditingActor(null);
    setFormData({ name: '', type: 'npc', attributes: {}, metadata: {} });
  };

  if (!simulationId) {
    return null;
  }

  // Show loading state while simulation is being fetched
  if (!activeSimulation) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Actor Management
        </h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
        >
          + New Actor
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <form onSubmit={handleCreateActor} className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">Create New Actor</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="player">Player</option>
                <option value="npc">NPC</option>
                <option value="organization">Organization</option>
                <option value="entity">Entity</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors"
            >
              Create
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Edit Form */}
      {editingActor && (
        <form onSubmit={handleUpdateActor} className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">
            Edit Actor: {editingActor.name}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="player">Player</option>
                <option value="npc">NPC</option>
                <option value="organization">Organization</option>
                <option value="entity">Entity</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors"
            >
              Update
            </button>
            <button
              type="button"
              onClick={cancelEdit}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Actors List */}
      <div className="space-y-3">
        {actors.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 text-center py-4">
            No actors found. Create your first actor to get started.
          </p>
        ) : (
          actors.map((actor) => (
            <div
              key={actor.id}
              className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {actor.name}
                  </h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    actor.active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                  }`}>
                    {actor.active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 rounded-full">
                    {actor.type.toUpperCase()}
                  </span>
                </div>
                
                {/* Location */}
                {actor.location && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    📍 <span className="font-medium">Location:</span> {actor.location.name || JSON.stringify(actor.location)}
                  </div>
                )}
                
                {/* Traits */}
                {actor.attributes?.traits && Object.keys(actor.attributes.traits).length > 0 && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    ✨ <span className="font-medium">Traits:</span>{' '}
                    {Object.entries(actor.attributes.traits as Record<string, unknown>)
                      .map(([key, value]) => `${key}: ${value}`)
                      .join(', ')}
                  </div>
                )}
                
                {/* Skills */}
                {actor.attributes?.skills && Array.isArray(actor.attributes.skills) && actor.attributes.skills.length > 0 && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    🎯 <span className="font-medium">Skills:</span> {(actor.attributes.skills as string[]).join(', ')}
                  </div>
                )}
                
                {/* Role from metadata */}
                {actor.metadata?.role && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    👤 <span className="font-medium">Role:</span> {actor.metadata.role as string}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(actor)}
                  className="px-3 py-1 text-sm bg-yellow-600 hover:bg-yellow-700 text-white rounded-md transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteActor(actor.id)}
                  className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
