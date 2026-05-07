"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ingestPapers } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [ingestQuery, setIngestQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  async function handleIngest(e: React.FormEvent) {
    e.preventDefault();
    if (!ingestQuery.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await ingestPapers(ingestQuery, 10);
      setResult(
        `Ingested ${res.documents_ingested} papers (${res.chunks_created} chunks)`
      );
      toast.success(`Ingested ${res.documents_ingested} papers successfully`);
    } catch {
      setResult("Failed to ingest papers. Is the backend running?");
      toast.error("Ingestion failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto px-4 py-16 max-w-4xl">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl font-bold tracking-tight">
          <span className="text-primary">Medi</span>Search AI
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          AI-powered medical research assistant. Search PubMed literature with
          natural language and get cited, evidence-based answers.
        </p>
        <div className="flex items-center justify-center gap-2 flex-wrap">
          <Badge variant="secondary">Hybrid Retrieval</Badge>
          <Badge variant="secondary">Cross-Encoder Reranking</Badge>
          <Badge variant="secondary">Llama 3</Badge>
          <Badge variant="secondary">PubMed</Badge>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 mb-12">
        <Card
          className="p-6 cursor-pointer hover:border-primary transition-colors"
          onClick={() => router.push("/chat")}
        >
          <h2 className="text-lg font-semibold mb-2">Chat</h2>
          <p className="text-sm text-muted-foreground">
            Have a conversation with AI about medical research. Ask follow-up
            questions and explore topics in depth.
          </p>
        </Card>
        <Card
          className="p-6 cursor-pointer hover:border-primary transition-colors"
          onClick={() => router.push("/search")}
        >
          <h2 className="text-lg font-semibold mb-2">Search</h2>
          <p className="text-sm text-muted-foreground">
            One-shot search with year filtering. Get a direct answer with
            citations from indexed papers.
          </p>
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Ingest Papers from PubMed
        </h2>
        <p className="text-sm text-muted-foreground mb-4">
          Before searching, load papers into the knowledge base. Enter a medical
          topic to fetch and index relevant research.
        </p>
        <form onSubmit={handleIngest} className="flex gap-2">
          <Input
            value={ingestQuery}
            onChange={(e) => setIngestQuery(e.target.value)}
            placeholder='e.g. "type 2 diabetes treatment 2024"'
            disabled={loading}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !ingestQuery.trim()}>
            {loading ? "Ingesting..." : "Ingest"}
          </Button>
        </form>
        {result && (
          <p className="text-sm mt-3 text-muted-foreground">{result}</p>
        )}
      </Card>
    </div>
  );
}
