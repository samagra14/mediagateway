import { useState, useEffect } from 'react';
import { api, VideoGenerationRequest, VideoGenerationResponse, ProviderInfo } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function Playground() {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [duration, setDuration] = useState(5);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [seed, setSeed] = useState('');
  const [generating, setGenerating] = useState(false);
  const [currentGeneration, setCurrentGeneration] = useState<VideoGenerationResponse | null>(null);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [error, setError] = useState('');
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  useEffect(() => {
    // Estimate cost when parameters change
    if (selectedModel && duration) {
      estimateCost();
    }
  }, [selectedModel, duration, aspectRatio]);

  const estimateCost = async () => {
    if (!selectedModel) return;

    try {
      const response = await fetch('/v1/usage/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          prompt: 'dummy',
          duration,
          aspect_ratio: aspectRatio,
        }),
      });

      const data = await response.json();
      setEstimatedCost(data.estimated_cost);
    } catch (err) {
      console.error('Failed to estimate cost:', err);
    }
  };

  const loadProviders = async () => {
    try {
      const data = await api.listProviders();
      const activeProviders = data.filter(p => p.has_key && p.key_status === 'active');
      setProviders(activeProviders);

      if (activeProviders.length > 0 && activeProviders[0].models.length > 0) {
        setSelectedModel(activeProviders[0].models[0]);
      }
    } catch (err: any) {
      console.error('Failed to load providers:', err);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    if (!selectedModel) {
      setError('No active providers. Please add API keys in Settings.');
      return;
    }

    setError('');
    setGenerating(true);
    setCurrentGeneration(null);

    try {
      const request: VideoGenerationRequest = {
        model: selectedModel,
        prompt: prompt.trim(),
        duration,
        aspect_ratio: aspectRatio,
        seed: seed ? parseInt(seed) : undefined,
      };

      const response = await api.createVideoGeneration(request);
      setCurrentGeneration(response);

      // Poll for status
      pollGenerationStatus(response.id);
    } catch (err: any) {
      setError(err.message || 'Failed to generate video');
      setGenerating(false);
    }
  };

  const pollGenerationStatus = async (generationId: string) => {
    const maxAttempts = 120; // 10 minutes
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await api.getVideoGeneration(generationId);
        setCurrentGeneration(status);

        if (status.status === 'completed') {
          setGenerating(false);
          return;
        } else if (status.status === 'failed') {
          setError(status.error || 'Generation failed');
          setGenerating(false);
          return;
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000);
        } else {
          setError('Generation timeout');
          setGenerating(false);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to check status');
        setGenerating(false);
      }
    };

    poll();
  };

  const availableModels = providers.flatMap(p =>
    p.models.map(m => ({ provider: p.display_name, model: m }))
  );

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Video Generation Playground</h1>
        <p className="text-muted-foreground">
          Create AI-generated videos from text prompts
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Generate Video</CardTitle>
          <CardDescription>
            Enter a prompt and configure parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Prompt</label>
            <Textarea
              placeholder="A serene sunset over mountains with birds flying..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              disabled={generating}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={generating || availableModels.length === 0}
              >
                {availableModels.length === 0 ? (
                  <option>No active providers</option>
                ) : (
                  availableModels.map(({ provider, model }) => (
                    <option key={model} value={model}>
                      {provider} - {model}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Aspect Ratio</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                disabled={generating}
              >
                <option value="16:9">16:9 (Landscape)</option>
                <option value="9:16">9:16 (Portrait)</option>
                <option value="1:1">1:1 (Square)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
              <Input
                type="number"
                min="1"
                max="10"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value) || 5)}
                disabled={generating}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Seed (optional)</label>
              <Input
                type="number"
                placeholder="Random"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                disabled={generating}
              />
            </div>
          </div>

          {estimatedCost !== null && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Estimated Cost:</span>
                <span className="text-lg font-bold text-green-600">
                  ${estimatedCost.toFixed(4)}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Based on {duration}s video at {aspectRatio} resolution
              </p>
            </div>
          )}

          {error && (
            <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
              {error}
            </div>
          )}

          <Button
            className="w-full"
            size="lg"
            onClick={handleGenerate}
            disabled={generating || availableModels.length === 0}
          >
            {generating ? 'Generating...' : 'Generate Video'}
          </Button>
        </CardContent>
      </Card>

      {currentGeneration && (
        <Card>
          <CardHeader>
            <CardTitle>Generation Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Status:</span>
                <span className={`text-sm px-2 py-1 rounded ${
                  currentGeneration.status === 'completed' ? 'bg-green-100 text-green-800' :
                  currentGeneration.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {currentGeneration.status}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Model:</span>
                <span className="text-sm text-muted-foreground">{currentGeneration.model}</span>
              </div>

              {currentGeneration.status === 'completed' && currentGeneration.video?.url && (
                <div className="mt-4">
                  <video
                    controls
                    className="w-full rounded-lg"
                    src={currentGeneration.video.url}
                  >
                    Your browser does not support the video tag.
                  </video>
                  <Button
                    className="w-full mt-3"
                    variant="outline"
                    onClick={() => window.open(currentGeneration.video?.url)}
                  >
                    Download Video
                  </Button>
                </div>
              )}

              {currentGeneration.usage && (
                <div className="pt-3 border-t space-y-2">
                  {currentGeneration.usage.cost && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Cost:</span>
                      <span className="text-sm text-muted-foreground">
                        ${currentGeneration.usage.cost.toFixed(2)}
                      </span>
                    </div>
                  )}
                  {currentGeneration.usage.time_seconds && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Generation Time:</span>
                      <span className="text-sm text-muted-foreground">
                        {currentGeneration.usage.time_seconds.toFixed(1)}s
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
