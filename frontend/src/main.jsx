import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const apiBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, body) {
  const response = await fetch(`${apiBase}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function App() {
  const [form, setForm] = useState({ item: "ergonomic chair", quantity: 2, budget: 210 });
  const [result, setResult] = useState(null);
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function negotiate(event) {
    event.preventDefault();
    setLoading(true); setError(""); setPayment(null);
    try { setResult(await request("/negotiations", { ...form, quantity: Number(form.quantity), budget: Number(form.budget) })); }
    catch (reason) { setError(reason.message); }
    finally { setLoading(false); }
  }

  async function createTestOrder() {
    const offer = result.selected_offer;
    setError("");
    try {
      const idempotency_key = crypto.randomUUID();
      setPayment(await request("/payments/orders", { negotiation_id: result.negotiation_id, idempotency_key, amount: offer.total_price, currency: offer.currency }));
    } catch (reason) { setError(reason.message); }
  }

  return <main>
    <section className="hero"><p className="eyebrow">SAFE PROCUREMENT DEMO</p><h1>NegotiAgent</h1><p>Three-round supplier negotiation with deterministic policy and payment safeguards.</p></section>
    <section className="card"><h2>Start a negotiation</h2><form onSubmit={negotiate}>
      <label>Item<input value={form.item} onChange={(event) => setForm({ ...form, item: event.target.value })} required /></label>
      <label>Quantity<input type="number" min="1" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: event.target.value })} required /></label>
      <label>Budget (INR)<input type="number" min="1" value={form.budget} onChange={(event) => setForm({ ...form, budget: event.target.value })} required /></label>
      <button disabled={loading}>{loading ? "Negotiating…" : "Compare offers"}</button>
    </form></section>
    {error && <p className="error">{error}</p>}
    {result && <section className="card"><h2>Decision</h2><p><strong>{result.decision}</strong></p>{result.selected_offer ? <><div className="selected"><span>{result.selected_offer.vendor_id}</span><strong>₹{result.selected_offer.total_price}</strong><span>{result.selected_offer.delivery_days} day delivery</span></div><button className="secondary" onClick={createTestOrder}>Create Razorpay test order</button></> : <p>No policy-approved offer was found.</p>}
      <p className="advisor"><strong>Advisor ({result.advisor.source}):</strong> {result.advisor.rationale}</p>
      {payment && <p className="success">Test order created: {payment.order_id} ({payment.amount_subunits} paise)</p>}
      <h3>All offers</h3><div className="offers">{result.offers.map((offer, index) => <div key={index}><span>Round {Math.floor(index / 3) + 1}</span><span>{offer.vendor_id}</span><strong>₹{offer.total_price}</strong><span>{offer.delivery_days}d</span></div>)}</div>
    </section>}
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
