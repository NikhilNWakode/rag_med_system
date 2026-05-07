"use client";

import { Badge } from "@/components/ui/badge";
import type { Source } from "@/lib/api";

export function SourceCard({ source }: { source: Source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg border p-3 hover:bg-muted/50 transition-colors"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-snug line-clamp-2">
            [{source.source_number}] {source.title}
          </p>
          <p className="text-xs text-muted-foreground mt-1 truncate">
            {source.authors}
          </p>
        </div>
        <Badge variant="secondary" className="shrink-0 text-xs">
          {source.year}
        </Badge>
      </div>
      <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
        <span className="truncate">{source.journal}</span>
        {source.pmid && (
          <>
            <span>·</span>
            <span>PMID: {source.pmid}</span>
          </>
        )}
      </div>
    </a>
  );
}
