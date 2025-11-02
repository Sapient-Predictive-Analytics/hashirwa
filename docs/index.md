# Prototype landing (UI will be added)
<h2>Issuer Onboarding (Prototype)</h2>
<form id="issuerForm" onsubmit="return validateIssuer()">
  <label>Issuer Name* <input required id="issuer_name"></label><br>
  <label>Product Name* <input required id="product_name"></label><br>
  <label>Category* <input required id="category"></label><br>
  <label>Certificate Type* <input required id="certificate_type"></label><br>
  <label>Certificate ID* <input required id="certificate_id"></label><br>
  <label>Region* <input required id="region"></label><br>
  <label>Website/QR <input id="website_or_qr" placeholder="https://..."></label><br>
  <button type="submit">Submit (Demo)</button>
</form>

<script>
function validateIssuer(){
  const req = ["issuer_name","product_name","category","certificate_type","certificate_id","region"];
  for (const id of req){
    const el = document.getElementById(id);
    if(!el.value.trim()){
      alert("Please fill " + id.replace("_"," "));
      el.focus();
      return false;
    }
  }
  alert("Submission received (demo). Admin must approve.");
  return false; // demo only
}
</script>

<hr>

<h2>Admin Panel (Mock)</h2>
<table border="1" cellpadding="6">
  <tr><th>Issuer</th><th>Status</th><th>Action</th></tr>
  <tr><td>Sample Farm</td><td id="st1">Pending</td>
      <td><button onclick="approve('st1')">Approve</button></td></tr>
  <tr><td>Green Valley</td><td id="st2">Pending</td>
      <td><button onclick="approve('st2')">Approve</button></td></tr>
</table>

<script>
function approve(cellId){
  document.getElementById(cellId).innerText = "Approved";
}
</script>
