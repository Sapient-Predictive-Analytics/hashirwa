const issuerId = (args && args.length > 1) ? args[1] : "1";
const url = `https://seminormally-pesky-margot.ngrok-free.dev/api/v1/cl/price?issuer_id=${encodeURIComponent(issuerId)}`;

const resp = await Functions.makeHttpRequest({
  url,
  method: "GET",
  timeout: 9000
});

return Functions.encodeString(JSON.stringify({
  url,
  status: resp.status,
  data: resp.data,
  error: resp.error
}));

