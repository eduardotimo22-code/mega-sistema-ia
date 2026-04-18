import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const backendUrl = process.env.MODAL_BASE_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: "MODAL_BASE_URL no configurado" }, { status: 500 });
  }

  const body = await req.json();

  try {
    const res = await fetch(`${backendUrl}/send-whatsapp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
