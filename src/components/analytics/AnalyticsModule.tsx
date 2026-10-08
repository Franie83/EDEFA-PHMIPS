import React, { useState } from 'react';
import { api } from '../../services/api.ts';
import {
  LineChart,
  BrainCircuit,
  TrendingUp,
  AlertTriangle,
  Send,
  Sparkles,
  Bot,
  User,
  HelpCircle,
  Clock,
  ArrowRight
} from 'lucide-react';

export const AnalyticsModule: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'assistant'; text: string; records?: any[] }>>([
    {
      sender: 'assistant',
      text: 'Welcome to the EF-PHMIPS Decision Support Intelligence Engine. You may ask questions in natural language regarding ecological hazards, budget allocations, contractor performance, recurring hotspots, and prioritization algorithms across Nigeria.'
    }
  ]);

  const handleAskQuery = async (userPrompt?: string) => {
    const textToAsk = userPrompt || query;
    if (!textToAsk.trim()) return;

    const newMessages = [...messages, { sender: 'user' as const, text: textToAsk }];
    setMessages(newMessages);
    setQuery('');
    setLoading(true);

    try {
      const response = await api.askAiAssistant(textToAsk);
      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          text: response.answer,
          records: response.matched_records
        }
      ]);
    } catch (e: any) {
      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          text: `An error occurred while querying the decision engine: ${e.message || 'Service unavailable'}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="analytics-module" className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Analytics & AI Decision Support System</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Module 13
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Natural language queries powered by server-side Gemini intelligence, trend recognition, and predictive ecological modeling.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Quick Suggested Prompts & Analytics Insights */}
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center">
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-amber-500" />
              Executive Query Suggestions
            </h3>
            <div className="space-y-2 text-xs">
              {[
                'Which LGAs in Edo State face the most critical gully collapse risk?',
                'Summarize total capital required for unaddressed critical hazards across Edo State.',
                'What are our most severe recurring flood and erosion hotspots in Edo State?',
                'List all active projects in procurement and their approved contractors.',
                'Explain the multi-criteria risk scoring methodology used by EDEFA for priority ranking.'
              ].map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handleAskQuery(prompt)}
                  className="w-full text-left p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 text-slate-700 hover:text-emerald-950 transition-colors flex items-start justify-between group"
                >
                  <span className="leading-snug">{prompt}</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1 mt-0.5 text-slate-400 group-hover:text-emerald-700 shrink-0" />
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3 text-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Predictive Seasonality Alerts
            </h3>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 space-y-1">
              <strong className="block text-[11px]">Rainfall Onset Peak (Edo Central / Edo South)</strong>
              <p className="text-[11px] leading-relaxed">
                Anticipated heavy rainfall in Q2/Q3 increases headward migration speed in unconsolidated Benin formation sands by 3.4x. Urgent drainage interceptors required at Uwelu, Queen Ede, and Auchi sites.
              </p>
            </div>
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-900 space-y-1">
              <strong className="block text-[11px]">Edo Agro-Forestry & Vetiver Buffer Progress</strong>
              <p className="text-[11px] leading-relaxed">
                Vetiver grass biological slope stabilization survival rate is 92% along the Oshiobugie and Queen Ede channels.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Interactive Chat / Natural Language Dialogue */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs h-[650px] flex flex-col overflow-hidden">
          {/* Chat Header */}
          <div className="px-5 py-3.5 bg-emerald-950 text-white flex items-center justify-between border-b border-emerald-900">
            <div className="flex items-center space-x-2">
              <BrainCircuit className="w-5 h-5 text-amber-400" />
              <div>
                <h3 className="font-bold text-sm">EDEFA AI Decision Assistant & Query Copilot</h3>
                <p className="text-[11px] text-emerald-300">Server-Side Gemini Model: gemini-3.8-flash</p>
              </div>
            </div>
          </div>

          {/* Messages stream */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex space-x-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-emerald-800 text-amber-300 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-xl p-3.5 rounded-xl leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-emerald-700 text-white font-medium rounded-tr-none'
                      : 'bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>

                  {/* Render matched records if present */}
                  {m.records && m.records.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-slate-200/80 space-y-1">
                      <div className="text-[10px] font-bold uppercase text-slate-500">Related Database Records:</div>
                      {m.records.map((r: any, i: number) => (
                        <div key={i} className="p-1.5 rounded bg-white border border-slate-200 text-[11px] font-semibold text-emerald-900">
                          {r.id ? `${r.id} - ` : ''}{r.title || r.community || r.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {m.sender === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-slate-800 text-white flex items-center justify-center shrink-0 font-bold">
                    ME
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-slate-500 text-xs">
                <BrainCircuit className="w-4 h-4 animate-spin text-emerald-600" />
                <span>Synthesizing database records & generating decision intelligence...</span>
              </div>
            )}
          </div>

          {/* Chat input form */}
          <form
            onSubmit={e => {
              e.preventDefault();
              handleAskQuery();
            }}
            className="p-3 border-t border-slate-200 bg-slate-50 flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask any question about Nigerian ecological hazards, projects, budgets, or priority rankings..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="flex-1 px-3 py-2 rounded-lg border border-slate-300 bg-white text-xs focus:outline-hidden focus:ring-1 focus:ring-emerald-600"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs inline-flex items-center transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4 mr-1.5" />
              Ask
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
