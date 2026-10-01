// Royal Enterprises - Crockery Wholesale Accounting System
// Full Client-side Engine for GitHub Pages

const defaultProducts = [
  { id: 1, name: "Dinner Set 72-Pcs Fine Bone China", category: "Dinner Sets", unit: "Set", stock: 45, costRate: 14500, saleRate: 18500 },
  { id: 2, name: "Tea Set 24-Pcs Royal Gold Rim", category: "Tea Sets", unit: "Set", stock: 60, costRate: 4800, saleRate: 6500 },
  { id: 3, name: "Ceramic Bowls 6-Pcs Floral", category: "Bowls", unit: "Box", stock: 120, costRate: 1200, saleRate: 1750 },
  { id: 4, name: "Stainless Steel Hot Pot Trio Set", category: "Hot Pots", unit: "Set", stock: 35, costRate: 5200, saleRate: 7200 },
  { id: 5, name: "Water Glass Set 6-Pcs Turkish Design", category: "Glassware", unit: "Box", stock: 150, costRate: 850, saleRate: 1300 },
  { id: 6, name: "Melamine Serving Tray Set of 3", category: "Trays", unit: "Set", stock: 80, costRate: 1600, saleRate: 2300 }
];

let appState = {
  products: JSON.parse(JSON.stringify(defaultProducts)),
  sales: [
    { id: "INV-20261001-0001", date: "2026-10-01", customer: "Haji Crockery Murree", item: "Dinner Set 72-Pcs Fine Bone China", qty: 4, saleRate: 18500, costRate: 14500, totalSale: 74000, totalCost: 58000, profit: 16000, received: 50000, balance: 24000 },
    { id: "INV-20261001-0002", date: "2026-10-01", customer: "Bismillah Traders Rawalpindi", item: "Tea Set 24-Pcs Royal Gold Rim", qty: 6, saleRate: 6500, costRate: 4800, totalSale: 39000, totalCost: 28800, profit: 10200, received: 39000, balance: 0 },
    { id: "INV-20261001-0003", date: "2026-10-01", customer: "Al-Madina Crockery Store", item: "Stainless Steel Hot Pot Trio Set", qty: 5, saleRate: 7200, costRate: 5200, totalSale: 36000, totalCost: 26000, profit: 10000, received: 20000, balance: 16000 }
  ],
  purchases: [
    { id: "PUR-20261001-0001", date: "2026-10-01", supplier: "Royal Crockery Karachi", item: "Dinner Set 72-Pcs Fine Bone China", qty: 20, costRate: 14500, total: 290000 },
    { id: "PUR-20261001-0002", date: "2026-10-01", supplier: "Gujranwala Ceramics Factory", item: "Ceramic Bowls 6-Pcs Floral", qty: 50, costRate: 1200, total: 60000 },
    { id: "PUR-20261001-0003", date: "2026-10-01", supplier: "China Glassware Importers", item: "Water Glass Set 6-Pcs Turkish Design", qty: 100, costRate: 850, total: 85000 }
  ],
  expenses: [
    { id: "EXP-001", date: "2026-10-01", category: "Shop Rent", desc: "Shop monthly rent payment", account: "Main Bank Account", amount: 35000 },
    { id: "EXP-002", date: "2026-10-01", category: "Labor & Wages", desc: "Unloading crockery containers", account: "Cash in Hand", amount: 8000 },
    { id: "EXP-003", date: "2026-10-01", category: "Tea & Refreshment", desc: "Customer & staff daily tea", account: "Cash in Hand", amount: 1500 }
  ],
  drawings: [
    { id: "DRW-001", date: "2026-10-01", partner: "Partner 1", account: "Cash in Hand", amount: 15000, remarks: "Household withdrawal" },
    { id: "DRW-002", date: "2026-10-01", partner: "Partner 2", account: "Main Bank Account", amount: 15000, remarks: "Personal expenses" }
  ],
  partners: [
    { name: "Partner 1", capital: 500000, current: 500000 },
    { name: "Partner 2", capital: 500000, current: 500000 }
  ],
  accounts: {
    cash: 85500,
    bank: 450000
  }
};

// Check LocalStorage
if (typeof localStorage !== "undefined" && localStorage.getItem("royalCrockeryDB")) {
  try {
    const saved = JSON.parse(localStorage.getItem("royalCrockeryDB"));
    if (saved && saved.products && saved.products.length > 0) {
      appState = saved;
    }
  } catch (err) {
    console.warn("Storage reset due to error:", err);
  }
}

function saveDB() {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("royalCrockeryDB", JSON.stringify(appState));
  }
  renderAll();
}

function resetSampleData() {
  if (confirm("Reset all sample demo data?")) {
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem("royalCrockeryDB");
    }
    location.reload();
  }
}

function showTab(tabName) {
  // Hide all tab panes
  const allPanes = document.querySelectorAll(".tab-pane-custom");
  allPanes.forEach(function (pane) {
    pane.style.display = "none";
  });

  // Remove active from all sidebar links
  const allLinks = document.querySelectorAll(".nav-item-link");
  allLinks.forEach(function (link) {
    link.classList.remove("active");
    if (link.getAttribute("data-tab") === tabName) {
      link.classList.add("active");
    }
  });

  // Show target tab pane
  const targetPane = document.getElementById("tab-" + tabName);
  if (targetPane) {
    targetPane.style.display = "block";
  }

  // Update Page Title
  const titles = {
    "dashboard": "Dashboard Overview",
    "partners": "Partners Capital & Equity",
    "purchases": "Purchases & Inward Stock",
    "sales": "Wholesale Sales & Invoicing",
    "customer-ledger": "Customer Running Ledger",
    "supplier-ledger": "Supplier Running Ledger",
    "expenses": "Business Operating Expenses",
    "stock": "Stock Inventory & Valuation",
    "cash-bank": "Cash & Bank Book",
    "drawings": "Partner Personal Drawings",
    "monthly-profit": "Monthly Profit & 50/50 Sharing"
  };

  const titleEl = document.getElementById("pageTitle");
  if (titleEl) {
    titleEl.innerText = titles[tabName] || "Dashboard";
  }
}

function renderAll() {
  // Fill product dropdowns
  const purSelect = document.getElementById("purProduct");
  const saleSelect = document.getElementById("saleProduct");

  if (purSelect && appState.products) {
    purSelect.innerHTML = appState.products.map(function (p) {
      return "<option value=\"" + p.id + "\">" + p.name + " (Stock: " + p.stock + " " + p.unit + ")</option>";
    }).join("");
    updatePurCostRate();
  }

  if (saleSelect && appState.products) {
    saleSelect.innerHTML = appState.products.map(function (p) {
      return "<option value=\"" + p.id + "\">" + p.name + " (Stock: " + p.stock + " " + p.unit + ")</option>";
    }).join("");
    updateSaleRates();
  }

  // Calculate Aggregates
  let totalSales = 0;
  let totalCOGS = 0;
  let receivables = 0;
  appState.sales.forEach(function (s) {
    totalSales += s.totalSale;
    totalCOGS += s.totalCost;
    receivables += s.balance;
  });

  const grossProfit = totalSales - totalCOGS;

  let totalExpenses = 0;
  appState.expenses.forEach(function (e) {
    totalExpenses += e.amount;
  });

  const netProfit = grossProfit - totalExpenses;
  const halfProfit = Math.floor(netProfit / 2);

  let stockValuation = 0;
  appState.products.forEach(function (p) {
    stockValuation += (p.stock * p.costRate);
  });

  const cashBankTotal = appState.accounts.cash + appState.accounts.bank;

  let capitalPool = 0;
  appState.partners.forEach(function (p) {
    capitalPool += p.capital;
  });

  let totalPurchases = 0;
  appState.purchases.forEach(function (p) {
    totalPurchases += p.total;
  });
  const payables = Math.round(totalPurchases * 0.4);

  // Helper setter
  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
  }

  setText("statSales", "PKR " + totalSales.toLocaleString());
  setText("statGrossProfit", "PKR " + grossProfit.toLocaleString());
  setText("statNetProfit", "PKR " + netProfit.toLocaleString());
  setText("statCashBank", "PKR " + cashBankTotal.toLocaleString());
  setText("statStockVal", "PKR " + stockValuation.toLocaleString());
  setText("statReceivables", "PKR " + receivables.toLocaleString());
  setText("statPayables", "PKR " + payables.toLocaleString());
  setText("statCapitalPool", "PKR " + capitalPool.toLocaleString());

  setText("dashP1Share", "PKR " + halfProfit.toLocaleString());
  setText("dashP2Share", "PKR " + halfProfit.toLocaleString());

  setText("p1Capital", "PKR " + appState.partners[0].capital.toLocaleString());
  setText("p1Balance", "PKR " + (appState.partners[0].current + halfProfit).toLocaleString());
  setText("p2Capital", "PKR " + appState.partners[1].capital.toLocaleString());
  setText("p2Balance", "PKR " + (appState.partners[1].current + halfProfit).toLocaleString());

  // Render Table Modules
  renderSalesTable();
  renderPurchasesTable();
  renderExpensesTable();
  renderStockTable();
  renderCashBankTable();
  renderDrawingsTable();
  renderCustomerLedger();
  renderSupplierLedger();
  renderMonthlyProfit(totalSales, totalCOGS, grossProfit, totalExpenses, netProfit, halfProfit);
}

function updatePurCostRate() {
  const sel = document.getElementById("purProduct");
  if (!sel) return;
  const p = appState.products.find(function (x) { return x.id == sel.value; });
  if (p) {
    document.getElementById("purCostRate").value = p.costRate;
    calcPurTotal();
  }
}

function calcPurTotal() {
  const qty = parseInt(document.getElementById("purQty").value) || 0;
  const rate = parseFloat(document.getElementById("purCostRate").value) || 0;
  const disp = document.getElementById("purTotalDisplay");
  if (disp) disp.value = "PKR " + (qty * rate).toLocaleString();
}

function handleNewPurchase(e) {
  if (e && e.preventDefault) e.preventDefault();
  const sel = document.getElementById("purProduct");
  const p = appState.products.find(function (x) { return x.id == sel.value; });
  const qty = parseInt(document.getElementById("purQty").value) || 0;
  const rate = parseFloat(document.getElementById("purCostRate").value) || 0;
  const total = qty * rate;
  const supplier = document.getElementById("purSupplier").value;

  if (p && qty > 0) {
    p.stock += qty;
    appState.purchases.unshift({
      id: "PUR-20261001-000" + (appState.purchases.length + 1),
      date: new Date().toISOString().split("T")[0],
      supplier: supplier,
      item: p.name,
      qty: qty,
      costRate: rate,
      total: total
    });
    saveDB();
    alert("Purchase recorded! " + qty + " units added to stock.");
  }
}

function updateSaleRates() {
  const sel = document.getElementById("saleProduct");
  if (!sel) return;
  const p = appState.products.find(function (x) { return x.id == sel.value; });
  if (p) {
    document.getElementById("saleRate").value = p.saleRate;
    calcSaleTotal();
  }
}

function calcSaleTotal() {
  const qty = parseInt(document.getElementById("saleQty").value) || 0;
  const rate = parseFloat(document.getElementById("saleRate").value) || 0;
  const total = qty * rate;
  const totDisp = document.getElementById("saleTotalDisplay");
  if (totDisp) totDisp.value = "PKR " + total.toLocaleString();

  const rec = parseFloat(document.getElementById("saleReceived").value) || 0;
  const balDisp = document.getElementById("saleBalanceDisplay");
  if (balDisp) balDisp.value = "PKR " + Math.max(0, total - rec).toLocaleString();
}

function handleNewSale(e) {
  if (e && e.preventDefault) e.preventDefault();
  const sel = document.getElementById("saleProduct");
  const p = appState.products.find(function (x) { return x.id == sel.value; });
  const qty = parseInt(document.getElementById("saleQty").value) || 0;

  if (!p || p.stock < qty) {
    alert("Insufficient stock! Available stock is: " + (p ? p.stock : 0));
    return;
  }

  const saleRate = parseFloat(document.getElementById("saleRate").value) || 0;
  const totalSale = qty * saleRate;
  const totalCost = qty * p.costRate;
  const profit = totalSale - totalCost;
  const received = parseFloat(document.getElementById("saleReceived").value) || 0;
  const balance = Math.max(0, totalSale - received);
  const cust = document.getElementById("saleCustomer").value;

  p.stock -= qty;
  appState.accounts.cash += received;

  const newSale = {
    id: "INV-20261001-000" + (appState.sales.length + 1),
    date: new Date().toISOString().split("T")[0],
    customer: cust,
    item: p.name,
    qty: qty,
    saleRate: saleRate,
    costRate: p.costRate,
    totalSale: totalSale,
    totalCost: totalCost,
    profit: profit,
    received: received,
    balance: balance
  };

  appState.sales.unshift(newSale);
  saveDB();
  previewInvoice(newSale.id);
}

function handleNewExpense(e) {
  if (e && e.preventDefault) e.preventDefault();
  const cat = document.getElementById("expCategory").value;
  const desc = document.getElementById("expDesc").value;
  const acc = document.getElementById("expAccount").value;
  const amt = parseFloat(document.getElementById("expAmount").value) || 0;

  if (amt <= 0) return;

  if (acc === "Cash in Hand") {
    appState.accounts.cash -= amt;
  } else {
    appState.accounts.bank -= amt;
  }

  appState.expenses.unshift({
    id: "EXP-00" + (appState.expenses.length + 1),
    date: new Date().toISOString().split("T")[0],
    category: cat,
    desc: desc,
    account: acc,
    amount: amt
  });

  saveDB();
  alert("Expense of PKR " + amt.toLocaleString() + " recorded!");
  document.getElementById("expAmount").value = "";
  document.getElementById("expDesc").value = "";
}

function handleNewDrawing(e) {
  if (e && e.preventDefault) e.preventDefault();
  const part = document.getElementById("drwPartner").value;
  const acc = document.getElementById("drwAccount").value;
  const amt = parseFloat(document.getElementById("drwAmount").value) || 0;
  const rem = document.getElementById("drwRemarks").value;

  if (amt <= 0) return;

  if (acc === "Cash in Hand") {
    appState.accounts.cash -= amt;
  } else {
    appState.accounts.bank -= amt;
  }

  const p = appState.partners.find(function (x) { return x.name === part; });
  if (p) p.current -= amt;

  appState.drawings.unshift({
    id: "DRW-00" + (appState.drawings.length + 1),
    date: new Date().toISOString().split("T")[0],
    partner: part,
    account: acc,
    amount: amt,
    remarks: rem
  });

  saveDB();
  alert("Partner drawing of PKR " + amt.toLocaleString() + " recorded!");
  document.getElementById("drwAmount").value = "";
  document.getElementById("drwRemarks").value = "";
}

function recordBreakagePrompt() {
  const pId = prompt("Enter Product ID to write off breakage (1 to 6):");
  const p = appState.products.find(function (x) { return x.id == pId; });
  if (p) {
    const bQty = parseInt(prompt("How many units broken/damaged? Currently in stock: " + p.stock));
    if (bQty && bQty > 0 && bQty <= p.stock) {
      p.stock -= bQty;
      saveDB();
      alert("Stock written off! " + bQty + " units deducted for breakage.");
    }
  }
}

function renderSalesTable() {
  const tbody = document.getElementById("salesTableBody");
  const recent = document.getElementById("dashboardRecentSales");

  if (tbody) {
    tbody.innerHTML = appState.sales.map(function (s) {
      return "<tr>" +
        "<td class=\"fw-bold text-primary\">" + s.id + "</td>" +
        "<td>" + s.customer + "</td>" +
        "<td>" + s.item + "</td>" +
        "<td>" + s.qty + "</td>" +
        "<td class=\"fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
        "<td class=\"text-muted\">PKR " + s.totalCost.toLocaleString() + "</td>" +
        "<td class=\"text-success fw-bold\">+PKR " + s.profit.toLocaleString() + "</td>" +
        "<td class=\"text-info\">PKR " + s.received.toLocaleString() + "</td>" +
        "<td class=\"" + (s.balance > 0 ? "text-danger fw-bold" : "text-success") + "\">PKR " + s.balance.toLocaleString() + "</td>" +
        "<td><button class=\"btn btn-sm btn-outline-primary py-0 px-2\" onclick=\"previewInvoice('" + s.id + "')\"><i class=\"bi bi-printer\"></i> Bill</button></td>" +
        "</tr>";
    }).join("");
  }

  if (recent) {
    recent.innerHTML = appState.sales.slice(0, 5).map(function (s) {
      return "<tr>" +
        "<td class=\"fw-bold text-primary\">" + s.id + "</td>" +
        "<td>" + s.customer + "</td>" +
        "<td class=\"fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
        "<td class=\"text-muted\">PKR " + s.totalCost.toLocaleString() + "</td>" +
        "<td class=\"text-success fw-bold\">+PKR " + s.profit.toLocaleString() + "</td>" +
        "<td><span class=\"badge " + (s.balance === 0 ? "bg-success" : "bg-warning text-dark") + "\">" + (s.balance === 0 ? "Paid" : "Credit") + "</span></td>" +
        "</tr>";
    }).join("");
  }
}

function renderPurchasesTable() {
  const tbody = document.getElementById("purchasesTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.purchases.map(function (p) {
    return "<tr>" +
      "<td class=\"fw-bold text-primary\">" + p.id + "</td>" +
      "<td>" + p.date + "</td>" +
      "<td>" + p.supplier + "</td>" +
      "<td>" + p.item + "</td>" +
      "<td>" + p.qty + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td class=\"fw-bold\">PKR " + p.total.toLocaleString() + "</td>" +
      "</tr>";
  }).join("");
}

function renderExpensesTable() {
  const tbody = document.getElementById("expenseTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.expenses.map(function (e) {
    return "<tr>" +
      "<td class=\"fw-bold\">" + e.id + "</td>" +
      "<td>" + e.date + "</td>" +
      "<td><span class=\"badge bg-secondary\">" + e.category + "</span></td>" +
      "<td>" + e.desc + "</td>" +
      "<td>" + e.account + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + e.amount.toLocaleString() + "</td>" +
      "</tr>";
  }).join("");
}

function renderStockTable() {
  const tbody = document.getElementById("stockTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.products.map(function (p) {
    const isLow = p.stock <= 40;
    return "<tr>" +
      "<td class=\"fw-bold\">" + p.name + "</td>" +
      "<td><span class=\"badge bg-light text-dark border\">" + p.category + "</span></td>" +
      "<td>" + p.unit + "</td>" +
      "<td class=\"fw-bold " + (isLow ? "text-warning" : "text-success") + "\">" + p.stock + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td>PKR " + p.saleRate.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-primary\">PKR " + (p.stock * p.costRate).toLocaleString() + "</td>" +
      "<td><span class=\"badge " + (isLow ? "bg-warning text-dark" : "bg-success") + "\">" + (isLow ? "Low Stock" : "In Stock") + "</span></td>" +
      "</tr>";
  }).join("");
}

function renderCashBankTable() {
  const cashEl = document.getElementById("cashInHandVal");
  const bankEl = document.getElementById("bankAccountVal");
  if (cashEl) cashEl.innerText = "PKR " + appState.accounts.cash.toLocaleString();
  if (bankEl) bankEl.innerText = "PKR " + appState.accounts.bank.toLocaleString();
}

function renderDrawingsTable() {
  const tbody = document.getElementById("drawingsTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.drawings.map(function (d) {
    return "<tr>" +
      "<td class=\"fw-bold\">" + d.id + "</td>" +
      "<td>" + d.date + "</td>" +
      "<td><span class=\"badge bg-primary\">" + d.partner + "</span></td>" +
      "<td>" + d.account + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + d.amount.toLocaleString() + "</td>" +
      "<td>" + d.remarks + "</td>" +
      "</tr>";
  }).join("");
}

function renderCustomerLedger() {
  const sel = document.getElementById("ledgerCustomerSelect");
  if (!sel) return;
  const cust = sel.value;
  const tbody = document.getElementById("custLedgerBody");
  const titleEl = document.getElementById("custLedgerTitle");
  if (titleEl) titleEl.innerText = "Customer Running Statement: " + cust;

  const cSales = appState.sales.filter(function (s) { return s.customer === cust; });
  let runBal = 0;
  let html = "";
  cSales.forEach(function (s) {
    runBal += s.totalSale;
    html += "<tr>" +
      "<td>" + s.date + "</td>" +
      "<td>Sale Invoice: " + s.id + " (" + s.item + " x " + s.qty + ")</td>" +
      "<td class=\"fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td>-</td>" +
      "<td class=\"fw-bold\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";

    if (s.received > 0) {
      runBal -= s.received;
      html += "<tr class=\"table-light\">" +
        "<td>" + s.date + "</td>" +
        "<td>Cash Payment Received against " + s.id + "</td>" +
        "<td>-</td>" +
        "<td class=\"text-success fw-bold\">PKR " + s.received.toLocaleString() + "</td>" +
        "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
        "</tr>";
    }
  });

  if (tbody) {
    tbody.innerHTML = html || "<tr><td colspan=\"5\" class=\"text-center py-3 text-muted\">No transactions recorded yet.</td></tr>";
  }
  const balEl = document.getElementById("custLedgerBalance");
  if (balEl) balEl.innerText = "Balance: PKR " + runBal.toLocaleString();
}

function renderSupplierLedger() {
  const sel = document.getElementById("ledgerSupplierSelect");
  if (!sel) return;
  const supp = sel.value;
  const tbody = document.getElementById("suppLedgerBody");
  const titleEl = document.getElementById("suppLedgerTitle");
  if (titleEl) titleEl.innerText = "Supplier Running Statement: " + supp;

  const sPurchases = appState.purchases.filter(function (p) { return p.supplier === supp; });
  let runBal = 0;
  let html = "";
  sPurchases.forEach(function (p) {
    runBal += p.total;
    html += "<tr>" +
      "<td>" + p.date + "</td>" +
      "<td>Purchase Invoice: " + p.id + " (" + p.item + " x " + p.qty + ")</td>" +
      "<td>-</td>" +
      "<td class=\"fw-bold\">PKR " + p.total.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";
  });

  if (tbody) {
    tbody.innerHTML = html || "<tr><td colspan=\"5\" class=\"text-center py-3 text-muted\">No transactions recorded yet.</td></tr>";
  }
  const balEl = document.getElementById("suppLedgerBalance");
  if (balEl) balEl.innerText = "Payable Balance: PKR " + runBal.toLocaleString();
}

function renderMonthlyProfit(sales, cogs, gp, exp, np, half) {
  const tbody = document.getElementById("monthlyProfitBody");
  if (!tbody) return;
  tbody.innerHTML = "<tr class=\"fw-bold\">" +
    "<td>October 2026</td>" +
    "<td class=\"text-primary\">PKR " + sales.toLocaleString() + "</td>" +
    "<td class=\"text-muted\">PKR " + cogs.toLocaleString() + "</td>" +
    "<td class=\"text-success\">PKR " + gp.toLocaleString() + "</td>" +
    "<td class=\"text-danger\">PKR " + exp.toLocaleString() + "</td>" +
    "<td class=\"text-success fs-5\">PKR " + np.toLocaleString() + "</td>" +
    "<td class=\"text-info\">PKR " + half.toLocaleString() + "</td>" +
    "<td class=\"text-info\">PKR " + half.toLocaleString() + "</td>" +
    "</tr>";
}

function previewInvoice(invId) {
  const s = appState.sales.find(function (x) { return x.id === invId; });
  if (!s) return;

  const noEl = document.getElementById("invNoModal");
  if (noEl) noEl.innerText = s.id;

  const dateEl = document.getElementById("invDateModal");
  if (dateEl) dateEl.innerText = "Date: " + s.date;

  const custEl = document.getElementById("invCustModal");
  if (custEl) custEl.innerText = s.customer;

  const itemsEl = document.getElementById("invItemsModal");
  if (itemsEl) {
    itemsEl.innerHTML = "<tr>" +
      "<td><strong>" + s.item + "</strong></td>" +
      "<td class=\"text-center\">" + s.qty + "</td>" +
      "<td class=\"text-end\">PKR " + s.saleRate.toLocaleString() + "</td>" +
      "<td class=\"text-end fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "</tr>";
  }

  const totEl = document.getElementById("invTotalModal");
  if (totEl) totEl.innerText = "PKR " + s.totalSale.toLocaleString();

  const recEl = document.getElementById("invRecModal");
  if (recEl) recEl.innerText = "PKR " + s.received.toLocaleString();

  const balEl = document.getElementById("invBalModal");
  if (balEl) balEl.innerText = "PKR " + s.balance.toLocaleString();

  if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
    const modalEl = document.getElementById("invoiceModal");
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

// Window load init
window.addEventListener("DOMContentLoaded", function () {
  renderAll();
  showTab("dashboard");
});
