const TWILIO_BASE = "https://api.twilio.com/2010-04-01";

function headers() {
  const sid = process.env.TWILIO_ACCOUNT_SID!;
  const token = process.env.TWILIO_AUTH_TOKEN!;
  return {
    Authorization: `Basic ${Buffer.from(`${sid}:${token}`).toString("base64")}`,
  };
}

export interface WaMessage {
  sid: string;
  to: string;
  from: string;
  body: string;
  status: string;
  dateSent: string;
  direction: string;
  errorCode: string | null;
}

export async function getWhatsAppMessages(limit = 30): Promise<WaMessage[]> {
  const sid = process.env.TWILIO_ACCOUNT_SID;
  const waNumber = process.env.TWILIO_WHATSAPP_NUMBER;
  if (!sid || !waNumber) return [];

  const from = `whatsapp:${waNumber}`;
  const url = `${TWILIO_BASE}/Accounts/${sid}/Messages.json?From=${encodeURIComponent(from)}&PageSize=${limit}`;

  try {
    const res = await fetch(url, { headers: headers(), next: { revalidate: 30 } });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.messages ?? []).map((m: any) => ({
      sid: m.sid,
      to: m.to?.replace("whatsapp:", "") ?? "",
      from: m.from?.replace("whatsapp:", "") ?? "",
      body: m.body ?? "",
      status: m.status ?? "",
      dateSent: m.date_sent ?? m.date_created ?? "",
      direction: m.direction ?? "",
      errorCode: m.error_code ?? null,
    }));
  } catch {
    return [];
  }
}

export function getWhatsAppStats(messages: WaMessage[]) {
  const today = new Date().toDateString();
  const enviados = messages.length;
  const enviadosHoy = messages.filter(
    (m) => new Date(m.dateSent).toDateString() === today
  ).length;
  const entregados = messages.filter((m) =>
    ["delivered", "read"].includes(m.status)
  ).length;
  const fallidos = messages.filter((m) => m.status === "failed" || m.errorCode).length;

  return { enviados, enviadosHoy, entregados, fallidos };
}
