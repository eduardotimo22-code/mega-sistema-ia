"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const SCENARIOS = [
  {
    id: "cita_confirmada",
    label: "Cita confirmada",
    color: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    fields: ["nombre_cliente", "fecha", "hora"],
  },
  {
    id: "seguimiento",
    label: "Seguimiento",
    color: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    fields: ["nombre_cliente"],
  },
  {
    id: "primer_contacto",
    label: "Primer contacto",
    color: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    fields: [],
  },
  {
    id: "personalizado",
    label: "Personalizado",
    color: "bg-neutral-500/20 text-neutral-400 border-neutral-500/30",
    fields: [],
  },
];

const FIELD_LABELS: Record<string, string> = {
  nombre_cliente: "Nombre del cliente",
  fecha: "Fecha (ej: lunes 21 de abril)",
  hora: "Hora (ej: 10:00 AM)",
};

export function WhatsAppForm({ agentName, businessName }: { agentName: string; businessName: string }) {
  const [scenario, setScenario] = useState("seguimiento");
  const [phone, setPhone] = useState("");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [customMessage, setCustomMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">("idle");
  const [resultMsg, setResultMsg] = useState("");

  const selected = SCENARIOS.find((s) => s.id === scenario)!;

  function handleField(key: string, value: string) {
    setFields((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSend() {
    if (!phone) return;
    setStatus("sending");
    setResultMsg("");

    const body =
      scenario === "personalizado"
        ? { phone, message: customMessage }
        : {
            phone,
            scenario,
            variables: {
              nombre_cliente: fields.nombre_cliente || "Cliente",
              fecha: fields.fecha || "",
              hora: fields.hora || "",
              business_name: businessName,
              agent_name: agentName,
            },
          };

    try {
      const res = await fetch("/api/whatsapp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.status === "ok") {
        setStatus("ok");
        setResultMsg("Mensaje enviado correctamente.");
        setPhone("");
        setFields({});
        setCustomMessage("");
      } else {
        setStatus("error");
        setResultMsg(data.message || "Error al enviar.");
      }
    } catch {
      setStatus("error");
      setResultMsg("Error de conexion con el servidor.");
    }
  }

  return (
    <Card className="border-white/[0.06] bg-white/[0.02]">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-normal uppercase tracking-widest text-neutral-500">
          Enviar mensaje
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Scenario selector */}
        <div>
          <p className="text-xs text-neutral-500 mb-2">Tipo de mensaje</p>
          <div className="flex flex-wrap gap-2">
            {SCENARIOS.map((s) => (
              <button
                key={s.id}
                onClick={() => setScenario(s.id)}
                className={`rounded-md border px-3 py-1.5 text-xs transition-all ${
                  scenario === s.id
                    ? s.color
                    : "border-white/[0.06] text-neutral-500 hover:text-neutral-300"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Phone */}
        <div>
          <label className="text-xs text-neutral-500 block mb-1.5">
            Numero de telefono
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+521234567890"
            className="w-full rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-white/20"
          />
        </div>

        {/* Dynamic fields per scenario */}
        {selected.fields.map((key) => (
          <div key={key}>
            <label className="text-xs text-neutral-500 block mb-1.5">
              {FIELD_LABELS[key] || key}
            </label>
            <input
              type="text"
              value={fields[key] || ""}
              onChange={(e) => handleField(key, e.target.value)}
              placeholder={FIELD_LABELS[key] || key}
              className="w-full rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-white/20"
            />
          </div>
        ))}

        {/* Custom message textarea */}
        {scenario === "personalizado" && (
          <div>
            <label className="text-xs text-neutral-500 block mb-1.5">
              Mensaje
            </label>
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              rows={4}
              placeholder="Escribe el mensaje aqui..."
              className="w-full rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-white/20 resize-none"
            />
          </div>
        )}

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={!phone || status === "sending"}
          className="w-full bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-40"
        >
          {status === "sending" ? "Enviando..." : "Enviar WhatsApp"}
        </Button>

        {/* Result */}
        {status === "ok" && (
          <p className="text-xs text-emerald-400">{resultMsg}</p>
        )}
        {status === "error" && (
          <p className="text-xs text-red-400">{resultMsg}</p>
        )}
      </CardContent>
    </Card>
  );
}
