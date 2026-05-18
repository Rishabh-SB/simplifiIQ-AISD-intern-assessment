"use client";

import { useState } from "react";

interface FormFields {
  [key: string]: string;
  name: string;
  email: string;
  company: string;
}

export default function Home() {
  const [formData, setFormData] = useState<FormFields>({
    name: "",
    email: "",
    company: "",
  });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    // Hard client-side baseline verification check (No whitespace-only submittals)
    if (
      !formData.name.trim() ||
      !formData.email.trim() ||
      !formData.company.trim()
    ) {
      setStatus({
        type: "error",
        message: "Please fill out all fields before submitting.",
      });
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (res.ok) {
        setStatus({
          type: "success",
          message:
            "Audit sequence initialized! Please check your inbox shortly for a copy of your report.",
        });
        setFormData({ name: "", email: "", company: "" });
      } else {
        // Checks if backend returned structural Pydantic array details vs custom detail messages
        const errorMsg = Array.isArray(data.detail)
          ? `Validation error: ${data.detail[0].msg}`
          : data.detail ||
            "The processing server rejected this request format.";
        setStatus({ type: "error", message: errorMsg });
      }
    } catch {
      // Handles hard offline drop error states where fetch cannot even ping the port gateway
      setStatus({
        type: "error",
        message:
          "Network Timeout: Unable to connect to the backend orchestration server. Please verify it is running on port 8000.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="w-screen min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-x-hidden">
      <div className="absolute inset-0 w-full h-full bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_70%,transparent_100%)]" />

      <div className="w-full max-w-md bg-slate-900/80 border border-slate-800/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl relative z-10 hover:border-slate-700/60 transition-all duration-300">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 mb-3 font-bold text-xl">
            SΩ
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            SimplifIQ Lead Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Initialize AI Automation Assessments instantly.
          </p>
        </div>

        {status && (
          <div
            className={`mb-6 p-4 rounded-xl text-sm border font-medium transition-all duration-200 ${
              status.type === "success"
                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                : "bg-rose-500/10 border-rose-500/20 text-rose-400"
            }`}
          >
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {[
            {
              id: "name",
              label: "Full Name",
              type: "text",
              placeholder: "John Doe",
            },
            {
              id: "email",
              label: "Email Address",
              type: "email",
              placeholder: "john@company.com",
            },
            {
              id: "company",
              label: "Company Name",
              type: "text",
              placeholder: "Acme Corp",
            },
          ].map((field) => (
            <div key={field.id}>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                {field.label}
              </label>
              <input
                type={field.type}
                required
                disabled={loading}
                value={formData[field.id]}
                onChange={(e) =>
                  setFormData({ ...formData, [field.id]: e.target.value })
                }
                placeholder={field.placeholder}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-600 font-medium text-sm transition-all outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold text-sm py-3.5 rounded-xl shadow-lg shadow-indigo-600/10 transition-all outline-none focus:ring-2 focus:ring-indigo-500/40 disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin h-4 w-4 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Processing Audit Pipeline...</span>
              </>
            ) : (
              <span>Generate Audit Assessment</span>
            )}
          </button>
        </form>
      </div>
    </main>
  );
}
