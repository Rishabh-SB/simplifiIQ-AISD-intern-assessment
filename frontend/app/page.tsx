"use client";

import React, { useState } from "react";
import {
  Sparkles,
  ArrowRight,
  Building2,
  Mail,
  User,
  Globe,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

export default function LeadFormPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company_name: "",
    company_url: "",
  });
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus({
      type: "loading",
      message: "Connecting to automation pipeline...",
    });
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      "https://rishabhsb-simplifiiq-intern-assessment.hf.space";

    try {
      const response = await fetch(`${backendUrl}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();

      if (response.ok) {
        setStatus({
          type: "success",
          message:
            "Lead Captured! Your custom audit PDF is being generated in the background. Check your inbox shortly.",
        });
        setFormData({ name: "", email: "", company_name: "", company_url: "" });
      } else {
        setStatus({
          type: "error",
          message: data.detail || "Server validation error.",
        });
      }
    } catch (err) {
      setStatus({
        type: "error",
        message:
          "Failed to contact backend API. Is your Uvicorn server running on port 8000?",
      });
    }
  };

  return (
    <div className="w-full max-w-xl bg-slate-800/60 backdrop-blur-md border border-slate-700/50 rounded-2xl shadow-2xl p-6 md:p-10">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center bg-blue-600/10 text-blue-400 border border-blue-500/20 rounded-xl px-3 py-1 text-xs font-semibold uppercase gap-1.5 mb-3">
          <Sparkles className="w-3.5 h-3.5" /> Pipeline Active
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          SimplifIQ Intel Engine
        </h1>
        <p className="text-sm text-slate-400 mt-2">
          Submit details below to generate a tailored automation audit report
          PDF directly to your email.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
            Full Name
          </label>
          <div className="relative">
            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              placeholder="Alex Chen"
              className="w-full bg-slate-900/50 border border-slate-700 focus:border-blue-500 rounded-xl py-3 pl-11 pr-4 text-sm text-white outline-none"
            />
          </div>
        </div>
        <div>
          <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              placeholder="alex@company.com"
              className="w-full bg-slate-900/50 border border-slate-700 focus:border-blue-500 rounded-xl py-3 pl-11 pr-4 text-sm text-white outline-none"
            />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
              Company Name
            </label>
            <div className="relative">
              <Building2 className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="company_name"
                required
                value={formData.company_name}
                onChange={handleChange}
                placeholder="SimplifIQ"
                className="w-full bg-slate-900/50 border border-slate-700 focus:border-blue-500 rounded-xl py-3 pl-11 pr-4 text-sm text-white outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
              Company Website
            </label>
            <div className="relative">
              <Globe className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="company_url"
                required
                value={formData.company_url}
                onChange={handleChange}
                placeholder="simplifiq.ai"
                className="w-full bg-slate-900/50 border border-slate-700 focus:border-blue-500 rounded-xl py-3 pl-11 pr-4 text-sm text-white outline-none"
              />
            </div>
          </div>
        </div>
        <button
          type="submit"
          disabled={status.type === "loading"}
          className="w-full mt-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white font-semibold rounded-xl py-3.5 px-4 text-sm flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {status.type === "loading" ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              Generate Audit Report <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {status.type !== "idle" && status.type !== "loading" && (
        <div
          className={`mt-6 p-4 rounded-xl border flex items-start gap-3 text-sm ${
            status.type === "success"
              ? "bg-emerald-950/30 border-emerald-500/20 text-emerald-400"
              : "bg-rose-950/30 border-rose-500/20 text-rose-400"
          }`}
        >
          {status.type === "success" ? (
            <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          )}
          <div>{status.message}</div>
        </div>
      )}
    </div>
  );
}
