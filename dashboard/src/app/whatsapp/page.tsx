import { Shell } from "@/components/shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getWhatsAppMessages, getWhatsAppStats } from "@/lib/twilio";
import { agent, business } from "@/lib/config";
import { WhatsAppForm } from "./whatsapp-form";

export const dynamic = "force-dynamic";

const statusStyles: Record<string, string> = {
  delivered: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  read:      "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  sent:      "bg-blue-500/20 text-blue-400 border-blue-500/30",
  queued:    "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  failed:    "bg-red-500/20 text-red-400 border-red-500/30",
  undelivered: "bg-red-500/20 text-red-400 border-red-500/30",
};

const statusLabel: Record<string, string> = {
  delivered:   "Entregado",
  read:        "Leido",
  sent:        "Enviado",
  queued:      "En cola",
  failed:      "Fallido",
  undelivered: "No entregado",
};

export default async function WhatsAppPage() {
  const messages = await getWhatsAppMessages(50);
  const stats = getWhatsAppStats(messages);

  return (
    <Shell>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-4xl font-bold italic tracking-tight">
          WhatsApp
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          Seguimiento automatico y envios manuales
        </p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KpiCard label="Enviados hoy" value={stats.enviadosHoy} />
        <KpiCard label="Total historial" value={stats.enviados} />
        <KpiCard label="Entregados" value={stats.entregados} accent="#10b981" />
        <KpiCard label="Fallidos" value={stats.fallidos} accent={stats.fallidos > 0 ? "#ef4444" : undefined} />
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Send form — left column */}
        <div className="col-span-1">
          <WhatsAppForm agentName={agent.name} businessName={business.name} />

          {/* Info card */}
          <Card className="border-white/[0.06] bg-white/[0.02] mt-4">
            <CardContent className="pt-4 space-y-3">
              <InfoRow label="Numero" value={process.env.TWILIO_WHATSAPP_NUMBER || "No configurado"} />
              <InfoRow label="Estado" value="Online" accent="#10b981" />
              <InfoRow label="Automatico" value="Post-llamada" />
            </CardContent>
          </Card>
        </div>

        {/* Message history — right columns */}
        <div className="col-span-2">
          <h2 className="font-heading text-xl font-semibold italic mb-4">
            Historial de mensajes
          </h2>

          {messages.length === 0 ? (
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] py-16 text-center">
              <p className="text-2xl mb-2">💬</p>
              <p className="text-sm text-neutral-500">
                No hay mensajes enviados aun.
              </p>
              <p className="text-xs text-neutral-600 mt-1">
                Los mensajes aparecen aqui despues de cada llamada o envio manual.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {messages.map((msg) => (
                <Card
                  key={msg.sid}
                  className="border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
                >
                  <CardContent className="flex items-start gap-4 py-3.5">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-base">
                      💬
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium font-mono text-neutral-300">
                          {msg.to}
                        </span>
                        <Badge
                          variant="outline"
                          className={`text-[10px] ${statusStyles[msg.status] || "border-neutral-600 text-neutral-500"}`}
                        >
                          {statusLabel[msg.status] || msg.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-neutral-500 line-clamp-2">{msg.body}</p>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="text-[10px] text-neutral-600">
                        {msg.dateSent
                          ? new Date(msg.dateSent).toLocaleDateString("es-MX", {
                              day: "numeric",
                              month: "short",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : ""}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </Shell>
  );
}

function KpiCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: string;
}) {
  return (
    <Card className="border-white/[0.06] bg-white/[0.02]">
      <CardHeader className="pb-1">
        <CardTitle className="text-xs font-normal uppercase tracking-widest text-neutral-500">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p
          className="text-3xl font-heading font-bold italic tracking-tight"
          style={accent ? { color: accent } : undefined}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

function InfoRow({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-neutral-500">{label}</span>
      <span
        className="text-xs font-medium font-mono"
        style={accent ? { color: accent } : undefined}
      >
        {value}
      </span>
    </div>
  );
}
