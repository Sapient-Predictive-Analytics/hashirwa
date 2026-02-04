// HashiRWA Functions source
// Modes:
//   cert  -> args: ["cert", "<subject>"]
//   price -> args: ["price", "<sku>"]
//
// IMPORTANT: Replace SHIM_BASE with public URL pointing to the Flask app port (default 8080).
// args: ["price","1"] or ["cert","1"]

const mode = (args && args.length > 0) ? args[0] : "price";
const issuerId = (args && args.length > 1) ? args[1] : "1";

const BASE = "https://seminormally-pesky-margot.ngrok-free.dev"; // <-- update API URL as necessary

const path = (mode === "cert")
  ? `/api/v1/cl/cert?issuer_id=${encodeURIComponent(issuerId)}`
  : `/api/v1/cl/price?issuer_id=${encodeURIComponent(issuerId)}`;

const url = `${BASE}${path}`;

const resp = await Functions.makeHttpRequest({
  url,
  method: "GET",
  timeout: 9000
});

if (resp.error) {
  throw Error(`shim error: ${JSON.stringify(resp.error)}`);
}

// resp.data might be a string (pipe-separated). Keep it tiny.
return Functions.encodeString(String(resp.data));
