import { useState, useEffect } from 'react';
import { api, APIKeyResponse, ProviderInfo } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Settings() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKeyResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddKey, setShowAddKey] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [newApiKey, setNewApiKey] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [providersData, keysData] = await Promise.all([
        api.listProviders(),
        api.listAPIKeys(),
      ]);
      setProviders(providersData);
      setApiKeys(keysData);
    } catch (err: any) {
      setError('Failed to load data');
    }
  };

  const handleAddKey = async () => {
    if (!selectedProvider || !newApiKey.trim()) {
      setError('Please select a provider and enter an API key');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.addAPIKey({
        provider: selectedProvider,
        api_key: newApiKey.trim(),
      });

      setSuccess('API key added successfully!');
      setNewApiKey('');
      setShowAddKey(false);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to add API key');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to delete this API key?')) {
      return;
    }

    try {
      await api.deleteAPIKey(keyId);
      setSuccess('API key deleted successfully!');
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to delete API key');
    }
  };

  const handleValidateKey = async (keyId: number) => {
    setLoading(true);
    setError('');

    try {
      const result = await api.validateAPIKey(keyId);
      if (result.valid) {
        setSuccess('API key is valid!');
      } else {
        setError('API key is invalid');
      }
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to validate API key');
    } finally {
      setLoading(false);
    }
  };

  const providersWithoutKeys = providers.filter(p => !p.has_key);

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your API keys and view usage statistics
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-md">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-800 rounded-md">
          {success}
        </div>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
          <CardDescription>
            Add and manage your provider API keys
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {apiKeys.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No API keys configured. Add your first key to get started.
              </div>
            ) : (
              <div className="space-y-3">
                {apiKeys.map((key) => (
                  <div
                    key={key.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-medium capitalize">{key.provider}</span>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            key.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {key.status}
                        </span>
                      </div>
                      {key.key_preview && (
                        <div className="text-sm text-muted-foreground mt-1">
                          {key.key_preview}
                        </div>
                      )}
                      {key.last_validated && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Last validated: {new Date(key.last_validated).toLocaleString()}
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleValidateKey(key.id)}
                        disabled={loading}
                      >
                        Test
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteKey(key.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!showAddKey && providersWithoutKeys.length > 0 && (
              <Button
                className="w-full"
                variant="outline"
                onClick={() => setShowAddKey(true)}
              >
                Add API Key
              </Button>
            )}

            {showAddKey && (
              <div className="border rounded-lg p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Provider</label>
                  <select
                    className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                  >
                    <option value="">Select a provider</option>
                    {providersWithoutKeys.map((provider) => (
                      <option key={provider.name} value={provider.name}>
                        {provider.display_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">API Key</label>
                  <Input
                    type="password"
                    placeholder="Enter your API key"
                    value={newApiKey}
                    onChange={(e) => setNewApiKey(e.target.value)}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    className="flex-1"
                    onClick={handleAddKey}
                    disabled={loading}
                  >
                    {loading ? 'Validating...' : 'Add Key'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowAddKey(false);
                      setNewApiKey('');
                      setSelectedProvider('');
                      setError('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available Providers</CardTitle>
          <CardDescription>
            Supported video generation providers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {providers.map((provider) => (
              <div
                key={provider.name}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div>
                  <div className="font-medium">{provider.display_name}</div>
                  <div className="text-sm text-muted-foreground">
                    Models: {provider.models.join(', ')}
                  </div>
                </div>
                {provider.has_key ? (
                  <span className="text-sm px-2 py-1 rounded bg-green-100 text-green-800">
                    Configured
                  </span>
                ) : (
                  <span className="text-sm px-2 py-1 rounded bg-gray-100 text-gray-800">
                    Not configured
                  </span>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
