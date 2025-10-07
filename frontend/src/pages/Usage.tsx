import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface UsageSummary {
  total_generations: number;
  total_cost: number;
  total_video_duration: number;
  total_processing_time: number;
  average_cost_per_generation: number;
}

interface DailyStats {
  date: string;
  count: number;
  cost: number;
  duration: number;
  success: number;
  failed: number;
}

interface ProviderStats {
  provider: string;
  count: number;
  cost: number;
  duration: number;
  avg_cost_per_second: number;
}

interface DetailedUsage {
  summary: UsageSummary;
  daily: DailyStats[];
  by_provider: ProviderStats[];
}

interface PricingInfo {
  provider: string;
  model: string;
  per_second: number;
  base_cost: number;
  currency: string;
  examples: {
    "5_seconds": number;
    "10_seconds": number;
    "20_seconds": number;
  };
}

export default function Usage() {
  const [usage, setUsage] = useState<DetailedUsage | null>(null);
  const [pricing, setPricing] = useState<PricingInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadData();
  }, [dateRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usageRes, pricingRes] = await Promise.all([
        fetch(`/v1/usage/detailed?start_date=${dateRange.start}&end_date=${dateRange.end}`),
        fetch('/v1/usage/pricing'),
      ]);

      const usageData = await usageRes.json();
      const pricingData = await pricingRes.json();

      setUsage(usageData);
      setPricing(pricingData.pricing || []);
    } catch (err) {
      console.error('Failed to load usage data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center py-12 text-muted-foreground">Loading usage data...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Usage & Cost Analytics</h1>
        <p className="text-muted-foreground">
          Track your video generation usage and costs
        </p>
      </div>

      {/* Date Range Selector */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Date Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Start Date</label>
              <input
                type="date"
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">End Date</label>
              <input
                type="date"
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              />
            </div>
            <Button onClick={loadData}>Update</Button>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {usage && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Cost</CardDescription>
                <CardTitle className="text-3xl text-green-600">
                  ${usage.summary.total_cost.toFixed(2)}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Avg: ${usage.summary.average_cost_per_generation.toFixed(4)}/video
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Generations</CardDescription>
                <CardTitle className="text-3xl">{usage.summary.total_generations}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Videos created in date range
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Video Duration</CardDescription>
                <CardTitle className="text-3xl">{usage.summary.total_video_duration.toFixed(1)}s</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Total output duration
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Processing Time</CardDescription>
                <CardTitle className="text-3xl">{(usage.summary.total_processing_time / 60).toFixed(1)}m</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Time spent generating
                </p>
              </CardContent>
            </Card>
          </div>

          {/* By Provider */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Cost by Provider</CardTitle>
              <CardDescription>Breakdown of spending per provider</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {usage.by_provider.map((provider) => (
                  <div key={provider.provider} className="border-b pb-4 last:border-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-semibold capitalize">{provider.provider}</h3>
                        <p className="text-sm text-muted-foreground">
                          {provider.count} videos • {provider.duration.toFixed(1)}s total duration
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">
                          ${provider.cost.toFixed(2)}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          ${provider.avg_cost_per_second.toFixed(4)}/sec
                        </p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{
                          width: `${(provider.cost / usage.summary.total_cost) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Daily Stats */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Daily Usage</CardTitle>
              <CardDescription>Day-by-day breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {usage.daily.slice(-7).reverse().map((day) => (
                  <div key={day.date} className="flex justify-between items-center py-2 border-b last:border-0">
                    <div className="flex-1">
                      <div className="font-medium">{day.date}</div>
                      <div className="text-sm text-muted-foreground">
                        {day.count} videos • {day.success} success • {day.failed} failed
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-green-600">${day.cost.toFixed(2)}</div>
                      <div className="text-xs text-muted-foreground">{day.duration.toFixed(1)}s</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Pricing Info */}
      <Card>
        <CardHeader>
          <CardTitle>Current Pricing</CardTitle>
          <CardDescription>Cost per second for each provider and model</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {pricing.map((price) => (
              <div key={`${price.provider}-${price.model}`} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold capitalize">
                      {price.provider} - {price.model}
                    </h3>
                    <p className="text-2xl font-bold text-green-600 mt-1">
                      ${price.per_second}/second
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center p-2 bg-gray-50 rounded">
                    <div className="text-muted-foreground">5 seconds</div>
                    <div className="font-semibold">${price.examples["5_seconds"]}</div>
                  </div>
                  <div className="text-center p-2 bg-gray-50 rounded">
                    <div className="text-muted-foreground">10 seconds</div>
                    <div className="font-semibold">${price.examples["10_seconds"]}</div>
                  </div>
                  <div className="text-center p-2 bg-gray-50 rounded">
                    <div className="text-muted-foreground">20 seconds</div>
                    <div className="font-semibold">${price.examples["20_seconds"]}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
