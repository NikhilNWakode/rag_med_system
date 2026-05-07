"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { SourceCard } from "@/components/source-card";
import { MarkdownAnswer } from "@/components/markdown-answer";
import { searchQuery, type Source } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Source[]>([]);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setAnswer(null);
    setSources([]);

    try {
      const res = await searchQuery(
        query,
        5,
        yearFrom ? parseInt(yearFrom) : undefined,
        yearTo ? parseInt(yearTo) : undefined
      );
      setAnswer(res.answer);
      setSources(res.sources);
      toast.success(`Found ${res.sources.length} source${res.sources.length !== 1 ? "s" : ""}`);
    } catch {
      toast.error("Search failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Search Medical Literature</h1>

      <Card className="p-6 mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your medical research question..."
              disabled={loading}
              className="text-base"
            />
          </div>
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="text-xs text-muted-foreground mb-1 block">
                Year from
              </label>
              <Input
                type="number"
                value={yearFrom}
                onChange={(e) => setYearFrom(e.target.value)}
                placeholder="e.g. 2020"
                disabled={loading}
              />
            </div>
            <div className="flex-1 w-full">
              <label className="text-xs text-muted-foreground mb-1 block">
                Year to
              </label>
              <Input
                type="number"
                value={yearTo}
                onChange={(e) => setYearTo(e.target.value)}
                placeholder="e.g. 2024"
                disabled={loading}
              />
            </div>
            <Button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 w-full sm:w-auto"
            >
              {loading ? "Searching..." : "Search"}
            </Button>
          </div>
        </form>
      </Card>

      {loading && (
        <Card className="p-6 mb-6 space-y-3">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-[95%]" />
          <Skeleton className="h-4 w-[85%]" />
          <Skeleton className="h-4 w-[90%]" />
          <Skeleton className="h-4 w-[60%]" />
        </Card>
      )}

      {answer && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="font-semibold mb-3">Answer</h2>
            <div className="text-sm">
              <MarkdownAnswer content={answer} />
            </div>
          </Card>

          {sources.length > 0 && (
            <div>
              <h2 className="font-semibold mb-3">
                Sources ({sources.length})
              </h2>
              <div className="grid gap-2">
                {sources.map((source, i) => (
                  <SourceCard key={i} source={source} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
