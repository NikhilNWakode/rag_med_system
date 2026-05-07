"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { SourceCard } from "@/components/source-card";
import { MarkdownAnswer } from "@/components/markdown-answer";
import {
  chatQuery,
  getConversations,
  getConversationMessages,
  deleteConversation,
  getExportUrl,
  type Source,
  type Conversation,
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [activeSources, setActiveSources] = useState<Source[]>([]);
  const [showSources, setShowSources] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function loadConversations() {
    try {
      const convs = await getConversations();
      setConversations(convs);
    } catch {
      // silently fail on first load
    }
  }

  async function loadConversation(conv: Conversation) {
    try {
      const data = await getConversationMessages(conv.id);
      const msgs: Message[] = data.messages.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
        sources: m.sources || undefined,
      }));
      setMessages(msgs);
      setConversationId(conv.id);
      setShowHistory(false);
      const lastAssistant = [...msgs].reverse().find((m) => m.role === "assistant");
      if (lastAssistant?.sources) setActiveSources(lastAssistant.sources);
    } catch {
      toast.error("Failed to load conversation");
    }
  }

  async function handleDelete(convId: string) {
    try {
      await deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (conversationId === convId) handleNewChat();
      toast.success("Conversation deleted");
    } catch {
      toast.error("Failed to delete");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await chatQuery(userMsg, conversationId);
      setConversationId(res.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
      setActiveSources(res.sources);
      loadConversations();
    } catch {
      toast.error("Failed to get response. Is the backend running?");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't process your request. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleNewChat() {
    setMessages([]);
    setConversationId(undefined);
    setActiveSources([]);
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      {/* History sidebar — visible on xl+, togglable on smaller */}
      <div
        className={`w-64 border-r flex-col ${
          showHistory ? "flex fixed inset-y-14 left-0 z-40 bg-background" : "hidden xl:flex"
        }`}
      >
        <div className="px-3 py-3 border-b flex items-center justify-between">
          <h2 className="font-semibold text-sm">History</h2>
          <Button
            variant="ghost"
            size="sm"
            className="xl:hidden h-6 w-6 p-0"
            onClick={() => setShowHistory(false)}
          >
            &times;
          </Button>
        </div>
        <ScrollArea className="flex-1">
          {conversations.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8">
              No conversations yet
            </p>
          ) : (
            <div className="p-2 space-y-1">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`group flex items-center gap-1 rounded-md px-2 py-1.5 cursor-pointer hover:bg-muted text-sm ${
                    conversationId === conv.id ? "bg-muted" : ""
                  }`}
                >
                  <button
                    className="flex-1 text-left truncate"
                    onClick={() => loadConversation(conv)}
                  >
                    {conv.title}
                  </button>
                  <button
                    className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive text-xs shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(conv.id);
                    }}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="xl:hidden"
              onClick={() => setShowHistory(!showHistory)}
            >
              History
            </Button>
            <h1 className="font-semibold">Medical Research Chat</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="lg:hidden"
              onClick={() => setShowSources(!showSources)}
            >
              Sources {activeSources.length > 0 && `(${activeSources.length})`}
            </Button>
            {conversationId && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(getExportUrl(conversationId), "_blank")}
              >
                Export PDF
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={handleNewChat}>
              New Chat
            </Button>
          </div>
        </div>

        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-16 text-muted-foreground">
                <p className="text-lg font-medium mb-2">
                  Ask a medical research question
                </p>
                <p className="text-sm">
                  e.g. &quot;What are the risk factors for Alzheimer&apos;s
                  disease?&quot;
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="text-sm">
                      <MarkdownAnswer content={msg.content} />
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  )}
                  {msg.sources && msg.sources.length > 0 && (
                    <button
                      className="text-xs mt-2 underline opacity-70 hover:opacity-100"
                      onClick={() => {
                        setActiveSources(msg.sources!);
                        setShowSources(true);
                      }}
                    >
                      View {msg.sources.length} source
                      {msg.sources.length > 1 ? "s" : ""}
                    </button>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-3 w-[70%] space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-[90%]" />
                  <Skeleton className="h-4 w-[75%]" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t p-4">
          <form
            onSubmit={handleSubmit}
            className="max-w-3xl mx-auto flex gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a medical research question..."
              disabled={loading}
              className="flex-1"
            />
            <Button type="submit" disabled={loading || !input.trim()}>
              Send
            </Button>
          </form>
        </div>
      </div>

      {/* Sources panel */}
      <div
        className={`w-80 border-l flex-col ${
          showSources ? "flex fixed inset-y-14 right-0 z-40 bg-background" : "hidden lg:flex"
        }`}
      >
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h2 className="font-semibold text-sm">Sources</h2>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden h-6 w-6 p-0"
            onClick={() => setShowSources(false)}
          >
            &times;
          </Button>
        </div>
        <ScrollArea className="flex-1 p-3">
          {activeSources.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8">
              Sources will appear here after you ask a question
            </p>
          ) : (
            <div className="space-y-2">
              {activeSources.map((source, i) => (
                <SourceCard key={i} source={source} />
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
}
