// Royal Enterprises - Crockery Wholesale Accounting System
// Complete In-Browser Relational Database & Full Module Handlers

const INITIAL_DB = {
  products: [
    { id: 1, name: "Dinner Set 72-Pcs Fine Bone China", category: "Dinner Sets", unit: "Set", stock: 45, costRate: 14500, saleRate: 18500 },
    { id: 2, name: "Tea Set 24-Pcs Royal Gold Rim", category: "Tea Sets", unit: "Set", stock: 60, costRate: 4800, saleRate: 6500 },
    { id: 3, name: "Ceramic Bowls 6-Pcs Floral", category: "Bowls", unit: "Box", stock: 120, costRate: 1200, saleRate: 1750 },
    { id: 4, name: "Stainless Steel Hot Pot Trio Set", category: "Hot Pots", unit: "Set", stock: 35, costRate: 5200, saleRate: 7200 },
    { id: 5, name: "Water Glass Set 6-Pcs Turkish Design", category: "Glassware", unit: "Box", stock: 150, costRate: 850, saleRate: 1300 },
    { id: 6, name: "Melamine Serving Tray Set of 3", category: "Trays", unit: "Set", stock: 80, costRate: 1600, saleRate: 2300 }
  ],
  customers: [
    { id: 1, name: "Haji Crockery Murree", phone: "0300-1122334", city: "Murree" },
    { id: 2, name: "Bismillah Traders Rawalpindi", phone: "0321-5544332", city: "Rawalpindi" },
    { id: 3, name: "Al-Madina Crockery Store", phone: "0333-9988776", city: "Islamabad" }
  ],
  suppliers: [
    { id: 1, name: "Royal Crockery Karachi", phone: "0300-8877665", city: "Karachi" },
    { id: 2, name: "Gujranwala Ceramics Factory", phone: "0312-3344556", city: "Gujranwala" },
    { id: 3, name: "China Glassware Importers", phone: "0345-2233445", city: "Lahore" }
  ],
  partners: [
    { id: 1, name: "Partner 1", sharePercentage: 50, capital: 500000, current: 500000 },
    { id: 2, name: "Partner 2", sharePercentage: 50, capital: 500000, current: 500000 }
  ],
  accounts: {
    cash: 85500,
    bank: 450000
  },
  sales: [
    { id: "INV-20261001-0001", date: "2026-10-01", customer: "Haji Crockery Murree", item: "Dinner Set 72-Pcs Fine Bone China", qty: 4, saleRate: 18500, costRate: 14500, totalSale: 74000, totalCost: 58000, profit: 16000, received: 50000, balance: 24000 },
    { id: "INV-20261001-0002", date: "2026-10-01", customer: "Bismillah Traders Rawalpindi", item: "Tea Set 24-Pcs Royal Gold Rim", qty: 6, saleRate: 6500, costRate: 4800, totalSale: 39000, totalCost: 28800, profit: 10200, received: 39000, balance: 0 },
    { id: "INV-20261001-0003", date: "2026-10-01", customer: "Al-Madina Crockery Store", item: "Stainless Steel Hot Pot Trio Set", qty: 5, saleRate: 7200, costRate: 5200, totalSale: 36000, totalCost: 26000, profit: 10000, received: 20000, balance: 16000 }
  ],
  purchases: [
    { id: "PUR-20261001-0001", date: "2026-10-01", supplier: "Royal Crockery Karachi", item: "Dinner Set 72-Pcs Fine Bone China", qty: 20, costRate: 14500, total: 290000, paid: 150000, balance: 140000 },
    { id: "PUR-20261001-0002", date: "2026-10-01", supplier: "Gujranwala Ceramics Factory", item: "Ceramic Bowls 6-Pcs Floral", qty: 50, costRate: 1200, total: 60000, paid: 60000, balance: 0 },
    { id: "PUR-20261001-0003", date: "2026-10-01", supplier: "China Glassware Importers", item: "Water Glass Set 6-Pcs Turkish Design", qty: 100, costRate: 850, total: 85000, paid: 85000, balance: 0 }
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
  capitalTransactions: [
    { id: "CAP-001", date: "2026-10-01", partner: "Partner 1", type: "Opening Equity", account: "Main Bank Account", amount: 500000, remarks: "Initial Capital Deposit" },
    { id: "CAP-002", date: "2026-10-01", partner: "Partner 2", type: "Opening Equity", account: "Main Bank Account", amount: 500000, remarks: "Initial Capital Deposit" }
  ],
  adjustments: [
    { id: "ADJ-001", date: "2026-10-01", product: "Ceramic Bowls 6-Pcs Floral", qty: 4, type: "Breakage", notes: "Broken during showroom display" }
  ],
  customerPayments: [
    { id: "RCT-001", date: "2026-10-01", customer: "Haji Crockery Murree", account: "Cash in Hand", amount: 10000, ref: "Market recovery cash" }
  ],
  supplierPayments: [
    { id: "PAY-001", date: "2026-10-01", supplier: "Royal Crockery Karachi", account: "Main Bank Account", amount: 50000, ref: "Online bank transfer" }
  ]
};

let appState = JSON.parse(JSON.stringify(INITIAL_DB));
let currentTab = "dashboard";

// -------------------------------------------------------------
// Database Persistence Helpers
// -------------------------------------------------------------
function loadDB() {
  if (typeof localStorage !== "undefined" && localStorage.getItem("royalCrockeryDB")) {
    try {
      const saved = JSON.parse(localStorage.getItem("royalCrockeryDB"));
      if (saved && saved.products && saved.sales) {
        appState = saved;
      }
    } catch (e) {
      console.warn("Storage reset to initial state");
    }
  }
}

function saveDB() {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("royalCrockeryDB", JSON.stringify(appState));
  }
  renderAll();
}

function resetSampleData() {
  if (confirm("Reset all database records to original demo sample? (This clears custom entries)")) {
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem("royalCrockeryDB");
    }
    appState = JSON.parse(JSON.stringify(INITIAL_DB));
    saveDB();
    showToast("Database reset to original sample!");
  }
}

function exportDatabaseJSON() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appState, null, 2));
  const downloadAnchor = document.createElement("a");
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", "Royal_Enterprises_DB_" + new Date().toISOString().slice(0, 10) + ".json");
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
  showToast("Database exported successfully!");
}

function showToast(msg) {
  const msgEl = document.getElementById("toastMessage");
  if (msgEl) msgEl.innerText = msg;
  const toastEl = document.getElementById("liveToast");
  if (toastEl && typeof bootstrap !== "undefined" && bootstrap.Toast) {
    const t = bootstrap.Toast.getOrCreateInstance(toastEl);
    t.show();
  }
}

// -------------------------------------------------------------
// Navigation & Sidebar
// -------------------------------------------------------------
function showTab(tabName) {
  closeSidebar();
  currentTab = tabName;

  const allPanes = document.querySelectorAll(".tab-pane-custom");
  allPanes.forEach(function (pane) { pane.style.display = "none"; });

  const allLinks = document.querySelectorAll(".nav-item-link");
  allLinks.forEach(function (link) {
    link.classList.remove("active");
    if (link.getAttribute("data-tab") === tabName) { link.classList.add("active"); }
  });

  const targetPane = document.getElementById("tab-" + tabName);
  if (targetPane) { targetPane.style.display = "block"; }

  const titles = {
    "dashboard": ["Dashboard Overview", "Real-Time Crockery Wholesale Accounting & Inventory"],
    "partners": ["Partners Capital & Equity", "50/50 Equity, Investments & Available Balances"],
    "purchases": ["Purchases & Stock Inward", "Record Wholesale Stock Shipments & Invoices"],
    "sales": ["Wholesale Sales & Invoicing", "Generate Wholesale Customer Invoices & Credit Bills"],
    "customer-ledger": ["Customer Running Ledger", "Market Customer Invoices, Receipts & Running Balances"],
    "supplier-ledger": ["Supplier Running Ledger", "Factory & Importer Purchases, Payments & Dues"],
    "expenses": ["Business Operating Expenses", "Shop Rent, Labor, Freight, Electricity & Daily Tea"],
    "stock": ["Stock Inventory & Valuation", "Real-Time Stock Counts, Unit Rates & Breakage Log"],
    "cash-bank": ["Cash & Bank Book", "Shop Cash Drawer & Commercial Bank Account Liquidity"],
    "drawings": ["Partner Personal Drawings", "Individual Withdrawals & Household Expenses"],
    "monthly-profit": ["Monthly Profit & 50/50 Sharing", "Perpetual Gross Profit, Expenses & Partner Distribution"]
  };

  const info = titles[tabName] || ["Dashboard Overview", "Crockery Wholesale Accounting"];
  const titleEl = document.getElementById("pageTitle");
  const subEl = document.getElementById("pageSubTitle");
  if (titleEl) titleEl.innerText = info[0];
  if (subEl) subEl.innerText = info[1];

  updateHeaderActionButton(tabName);
}

function updateHeaderActionButton(tabName) {
  const btnText = document.getElementById("headerActionText");
  const btnIcon = document.getElementById("headerActionIcon");
  if (!btnText || !btnIcon) return;

  switch (tabName) {
    case "purchases":
      btnText.innerText = "Record Purchase";
      btnIcon.className = "bi bi-bag-plus";
      break;
    case "expenses":
      btnText.innerText = "Record Expense";
      btnIcon.className = "bi bi-wallet2";
      break;
    case "stock":
      btnText.innerText = "Stock Breakage";
      btnIcon.className = "bi bi-slash-circle";
      break;
    case "customer-ledger":
      btnText.innerText = "Receive Payment";
      btnIcon.className = "bi bi-cash-coin";
      break;
    case "supplier-ledger":
      btnText.innerText = "Pay Supplier";
      btnIcon.className = "bi bi-truck";
      break;
    case "partners":
      btnText.innerText = "Add Capital";
      btnIcon.className = "bi bi-people";
      break;
    case "drawings":
      btnText.innerText = "Record Drawing";
      btnIcon.className = "bi bi-cash-stack";
      break;
    case "sales":
    case "dashboard":
    default:
      btnText.innerText = "Create Sale Bill";
      btnIcon.className = "bi bi-receipt-cutoff";
      break;
  }
}

function handleHeaderAction() {
  switch (currentTab) {
    case "purchases":
      openNewPurchaseModal();
      break;
    case "expenses":
      openNewExpenseModal();
      break;
    case "stock":
      openNewAdjustmentModal();
      break;
    case "customer-ledger":
      openCustomerReceiptModal();
      break;
    case "supplier-ledger":
      openSupplierPaymentModal();
      break;
    case "partners":
      openNewCapitalModal();
      break;
    case "drawings":
      openNewDrawingModal();
      break;
    case "sales":
    case "dashboard":
    default:
      openNewSaleModal();
      break;
  }
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  const bd = document.getElementById("sidebarBackdrop");
  if (sb) sb.classList.toggle("show");
  if (bd) bd.classList.toggle("show");
}

function closeSidebar() {
  const sb = document.getElementById("sidebar");
  const bd = document.getElementById("sidebarBackdrop");
  if (sb) sb.classList.remove("show");
  if (bd) bd.classList.remove("show");
}

function openModal(id) {
  if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
    const el = document.getElementById(id);
    if (el) {
      let m = bootstrap.Modal.getInstance(el);
      if (!m) m = new bootstrap.Modal(el);
      m.show();
    }
  }
}

function closeModal(id) {
  if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
    const el = document.getElementById(id);
    if (el) {
      const m = bootstrap.Modal.getInstance(el);
      if (m) m.hide();
    }
  }
}

// -------------------------------------------------------------
// 1. MODAL: CREATE WHOLESALE BILL / SALE INVOICE
// -------------------------------------------------------------
function openNewSaleModal() {
  const nextSeq = String(appState.sales.length + 1).padStart(4, "0");
  const nextNo = "INV-" + new Date().toISOString().slice(0, 10).replace(/-/g, "") + "-" + nextSeq;
  document.getElementById("mSaleInvNo").value = nextNo;
  document.getElementById("mSaleDate").value = new Date().toISOString().split("T")[0];

  const custSel = document.getElementById("mSaleCustomer");
  custSel.innerHTML = appState.customers.map(function (c) {
    return "<option value=\"" + c.name + "\">" + c.name + " (" + c.city + ")</option>";
  }).join("");

  const prodSel = document.getElementById("mSaleProduct");
  prodSel.innerHTML = appState.products.map(function (p) {
    return "<option value=\"" + p.id + "\">" + p.name + "</option>";
  }).join("");

  document.getElementById("mSaleQty").value = 2;
  document.getElementById("mSaleReceived").value = 0;
  onModalSaleProductChange();
  openModal("modalNewSale");
}

function onModalSaleProductChange() {
  const prodId = parseInt(document.getElementById("mSaleProduct").value, 10);
  const p = appState.products.find(function (x) { return x.id === prodId; });
  if (p) {
    document.getElementById("mSaleRate").value = p.saleRate;
    const badge = document.getElementById("mSaleStockBadge");
    if (badge) {
      badge.innerText = "Available Stock: " + p.stock + " " + p.unit;
      badge.className = p.stock > 10 ? "badge bg-success mb-1" : "badge bg-warning text-dark mb-1";
    }
  }
  calcModalSale();
}

function calcModalSale() {
  const qty = parseFloat(document.getElementById("mSaleQty").value) || 0;
  const rate = parseFloat(document.getElementById("mSaleRate").value) || 0;
  const total = qty * rate;
  document.getElementById("mSaleTotalDisplay").value = "PKR " + total.toLocaleString();

  const rec = parseFloat(document.getElementById("mSaleReceived").value) || 0;
  const bal = Math.max(0, total - rec);
  document.getElementById("mSaleBalanceDisplay").value = "PKR " + bal.toLocaleString();
}

function handleNewSaleSubmit(event) {
  event.preventDefault();
  const invNo = document.getElementById("mSaleInvNo").value;
  const date = document.getElementById("mSaleDate").value;
  const customer = document.getElementById("mSaleCustomer").value;
  const prodId = parseInt(document.getElementById("mSaleProduct").value, 10);
  const qty = parseInt(document.getElementById("mSaleQty").value, 10) || 1;
  const saleRate = parseFloat(document.getElementById("mSaleRate").value) || 0;
  const received = parseFloat(document.getElementById("mSaleReceived").value) || 0;
  const account = document.getElementById("mSaleAccount").value;

  const product = appState.products.find(function (p) { return p.id === prodId; });
  if (!product) { alert("Product not found"); return; }

  if (product.stock < qty) {
    if (!confirm("Warning: Stock is only " + product.stock + " " + product.unit + ". Proceed with negative/backordered stock?")) {
      return;
    }
  }

  // Deduct inventory
  product.stock -= qty;

  const totalSale = qty * saleRate;
  const totalCost = qty * product.costRate;
  const profit = totalSale - totalCost;
  const balance = Math.max(0, totalSale - received);

  // Update cash/bank accounts
  if (received > 0) {
    if (account === "Cash in Hand") {
      appState.accounts.cash += received;
    } else {
      appState.accounts.bank += received;
    }
  }

  const newSale = {
    id: invNo,
    date: date,
    customer: customer,
    item: product.name,
    qty: qty,
    saleRate: saleRate,
    costRate: product.costRate,
    totalSale: totalSale,
    totalCost: totalCost,
    profit: profit,
    received: received,
    balance: balance
  };

  appState.sales.unshift(newSale);
  saveDB();
  closeModal("modalNewSale");
  showToast("Sale Invoice " + invNo + " created & saved successfully!");

  // Immediately open printable preview
  previewInvoice(invNo);
}

// -------------------------------------------------------------
// 2. MODAL: RECORD PURCHASE INVOICE
// -------------------------------------------------------------
function openNewPurchaseModal() {
  const nextSeq = String(appState.purchases.length + 1).padStart(4, "0");
  const nextNo = "PUR-" + new Date().toISOString().slice(0, 10).replace(/-/g, "") + "-" + nextSeq;
  document.getElementById("mPurNo").value = nextNo;
  document.getElementById("mPurDate").value = new Date().toISOString().split("T")[0];

  const suppSel = document.getElementById("mPurSupplier");
  suppSel.innerHTML = appState.suppliers.map(function (s) {
    return "<option value=\"" + s.name + "\">" + s.name + " (" + s.city + ")</option>";
  }).join("");

  const prodSel = document.getElementById("mPurProduct");
  prodSel.innerHTML = appState.products.map(function (p) {
    return "<option value=\"" + p.id + "\">" + p.name + "</option>";
  }).join("");

  document.getElementById("mPurQty").value = 10;
  document.getElementById("mPurPaid").value = 0;
  onModalPurProductChange();
  openModal("modalNewPurchase");
}

function onModalPurProductChange() {
  const prodId = parseInt(document.getElementById("mPurProduct").value, 10);
  const p = appState.products.find(function (x) { return x.id === prodId; });
  if (p) {
    document.getElementById("mPurCostRate").value = p.costRate;
  }
  calcModalPur();
}

function calcModalPur() {
  const qty = parseFloat(document.getElementById("mPurQty").value) || 0;
  const rate = parseFloat(document.getElementById("mPurCostRate").value) || 0;
  const total = qty * rate;
  document.getElementById("mPurTotalDisplay").value = "PKR " + total.toLocaleString();

  const paid = parseFloat(document.getElementById("mPurPaid").value) || 0;
  const bal = Math.max(0, total - paid);
  document.getElementById("mPurBalanceDisplay").value = "PKR " + bal.toLocaleString();
}

function handleNewPurchaseSubmit(event) {
  event.preventDefault();
  const purNo = document.getElementById("mPurNo").value;
  const date = document.getElementById("mPurDate").value;
  const supplier = document.getElementById("mPurSupplier").value;
  const prodId = parseInt(document.getElementById("mPurProduct").value, 10);
  const qty = parseInt(document.getElementById("mPurQty").value, 10) || 1;
  const costRate = parseFloat(document.getElementById("mPurCostRate").value) || 0;
  const paid = parseFloat(document.getElementById("mPurPaid").value) || 0;
  const account = document.getElementById("mPurAccount").value;

  const product = appState.products.find(function (p) { return p.id === prodId; });
  if (!product) { alert("Product not found"); return; }

  // Perpetual Weighted Average / Update Cost & Stock
  const oldVal = product.stock * product.costRate;
  const newVal = qty * costRate;
  product.stock += qty;
  if (product.stock > 0) {
    product.costRate = Math.round((oldVal + newVal) / product.stock);
  }

  const total = qty * costRate;
  const balance = Math.max(0, total - paid);

  // Deduct paid amount from account
  if (paid > 0) {
    if (account === "Cash in Hand") {
      appState.accounts.cash -= paid;
    } else {
      appState.accounts.bank -= paid;
    }
  }

  const newPur = {
    id: purNo,
    date: date,
    supplier: supplier,
    item: product.name,
    qty: qty,
    costRate: costRate,
    total: total,
    paid: paid,
    balance: balance
  };

  appState.purchases.unshift(newPur);
  saveDB();
  closeModal("modalNewPurchase");
  showToast("Purchase " + purNo + " recorded. Stock increased by " + qty + "!");
}

// -------------------------------------------------------------
// 3. MODAL: RECORD BUSINESS EXPENSE
// -------------------------------------------------------------
function openNewExpenseModal() {
  const nextNo = "EXP-" + String(appState.expenses.length + 1).padStart(3, "0");
  document.getElementById("mExpNo").value = nextNo;
  document.getElementById("mExpDate").value = new Date().toISOString().split("T")[0];
  document.getElementById("mExpAmount").value = "";
  document.getElementById("mExpDesc").value = "";
  openModal("modalNewExpense");
}

function handleNewExpenseSubmit(event) {
  event.preventDefault();
  const expNo = document.getElementById("mExpNo").value;
  const date = document.getElementById("mExpDate").value;
  const category = document.getElementById("mExpCategory").value;
  const account = document.getElementById("mExpAccount").value;
  const amount = parseFloat(document.getElementById("mExpAmount").value) || 0;
  const desc = document.getElementById("mExpDesc").value;

  if (amount <= 0) { alert("Amount must be greater than 0"); return; }

  // Deduct from account
  if (account === "Cash in Hand") {
    appState.accounts.cash -= amount;
  } else {
    appState.accounts.bank -= amount;
  }

  const newExp = {
    id: expNo,
    date: date,
    category: category,
    desc: desc,
    account: account,
    amount: amount
  };

  appState.expenses.unshift(newExp);
  saveDB();
  closeModal("modalNewExpense");
  showToast("Expense " + expNo + " (" + category + ") recorded successfully!");
}

// -------------------------------------------------------------
// 4. MODAL: STOCK BREAKAGE & INVENTORY ADJUSTMENT
// -------------------------------------------------------------
function openNewAdjustmentModal() {
  const nextNo = "ADJ-" + String(appState.adjustments.length + 1).padStart(3, "0");
  document.getElementById("mAdjNo").value = nextNo;
  document.getElementById("mAdjDate").value = new Date().toISOString().split("T")[0];

  const prodSel = document.getElementById("mAdjProduct");
  prodSel.innerHTML = appState.products.map(function (p) {
    return "<option value=\"" + p.id + "\">" + p.name + " (Stock: " + p.stock + " " + p.unit + ")</option>";
  }).join("");

  document.getElementById("mAdjQty").value = 1;
  document.getElementById("mAdjNotes").value = "";
  onModalAdjProductChange();
  openModal("modalNewAdjustment");
}

function onModalAdjProductChange() {
  const prodId = parseInt(document.getElementById("mAdjProduct").value, 10);
  const p = appState.products.find(function (x) { return x.id === prodId; });
  if (p) {
    const badge = document.getElementById("mAdjStockBadge");
    if (badge) badge.innerText = "Current Stock: " + p.stock + " " + p.unit;
  }
}

function handleNewAdjustmentSubmit(event) {
  event.preventDefault();
  const adjNo = document.getElementById("mAdjNo").value;
  const date = document.getElementById("mAdjDate").value;
  const prodId = parseInt(document.getElementById("mAdjProduct").value, 10);
  const type = document.getElementById("mAdjType").value;
  const qty = parseInt(document.getElementById("mAdjQty").value, 10) || 1;
  const notes = document.getElementById("mAdjNotes").value;

  const product = appState.products.find(function (p) { return p.id === prodId; });
  if (!product) { alert("Product not found"); return; }

  if (type === "Breakage" || type === "Shortage" || type === "Return to Vendor") {
    product.stock = Math.max(0, product.stock - qty);
  } else if (type === "Excess") {
    product.stock += qty;
  }

  const newAdj = {
    id: adjNo,
    date: date,
    product: product.name,
    qty: qty,
    type: type,
    notes: notes
  };

  appState.adjustments.unshift(newAdj);
  saveDB();
  closeModal("modalNewAdjustment");
  showToast("Adjustment " + adjNo + " recorded. Stock updated!");
}

// -------------------------------------------------------------
// 5. MODAL: ADD PARTNER CAPITAL CONTRIBUTION
// -------------------------------------------------------------
function openNewCapitalModal() {
  const nextNo = "CAP-" + String(appState.capitalTransactions.length + 1).padStart(3, "0");
  document.getElementById("mCapNo").value = nextNo;
  document.getElementById("mCapDate").value = new Date().toISOString().split("T")[0];
  document.getElementById("mCapAmount").value = "";
  document.getElementById("mCapRemarks").value = "";
  openModal("modalNewCapital");
}

function handleNewCapitalSubmit(event) {
  event.preventDefault();
  const capNo = document.getElementById("mCapNo").value;
  const date = document.getElementById("mCapDate").value;
  const partnerName = document.getElementById("mCapPartner").value;
  const account = document.getElementById("mCapAccount").value;
  const type = document.getElementById("mCapType").value;
  const amount = parseFloat(document.getElementById("mCapAmount").value) || 0;
  const remarks = document.getElementById("mCapRemarks").value;

  if (amount <= 0) { alert("Amount must be greater than 0"); return; }

  // Update Partner Capital
  const partner = appState.partners.find(function (p) { return p.name === partnerName; });
  if (partner) {
    partner.capital += amount;
  }

  // Deposit in account
  if (account === "Cash in Hand") {
    appState.accounts.cash += amount;
  } else {
    appState.accounts.bank += amount;
  }

  const newCap = {
    id: capNo,
    date: date,
    partner: partnerName,
    type: type,
    account: account,
    amount: amount,
    remarks: remarks
  };

  appState.capitalTransactions.unshift(newCap);
  saveDB();
  closeModal("modalNewCapital");
  showToast("Capital contribution of PKR " + amount.toLocaleString() + " added for " + partnerName + "!");
}

// -------------------------------------------------------------
// 6. MODAL: RECORD PARTNER DRAWING / WITHDRAWAL
// -------------------------------------------------------------
function openNewDrawingModal() {
  const nextNo = "DRW-" + String(appState.drawings.length + 1).padStart(3, "0");
  document.getElementById("mDrwNo").value = nextNo;
  document.getElementById("mDrwDate").value = new Date().toISOString().split("T")[0];
  document.getElementById("mDrwAmount").value = "";
  document.getElementById("mDrwRemarks").value = "";
  openModal("modalNewDrawing");
}

function handleNewDrawingSubmit(event) {
  event.preventDefault();
  const drwNo = document.getElementById("mDrwNo").value;
  const date = document.getElementById("mDrwDate").value;
  const partnerName = document.getElementById("mDrwPartner").value;
  const account = document.getElementById("mDrwAccount").value;
  const amount = parseFloat(document.getElementById("mDrwAmount").value) || 0;
  const remarks = document.getElementById("mDrwRemarks").value;

  if (amount <= 0) { alert("Amount must be greater than 0"); return; }

  // Deduct from account
  if (account === "Cash in Hand") {
    appState.accounts.cash -= amount;
  } else {
    appState.accounts.bank -= amount;
  }

  const newDrw = {
    id: drwNo,
    date: date,
    partner: partnerName,
    account: account,
    amount: amount,
    remarks: remarks
  };

  appState.drawings.unshift(newDrw);
  saveDB();
  closeModal("modalNewDrawing");
  showToast("Drawing of PKR " + amount.toLocaleString() + " recorded for " + partnerName + "!");
}

// -------------------------------------------------------------
// 7. MODAL: RECEIVE CUSTOMER PAYMENT / RECOVERY
// -------------------------------------------------------------
function openCustomerReceiptModal() {
  const nextNo = "RCT-" + String(appState.customerPayments.length + 1).padStart(3, "0");
  document.getElementById("mRcptNo").value = nextNo;
  document.getElementById("mRcptDate").value = new Date().toISOString().split("T")[0];

  const custSel = document.getElementById("mRcptCustomer");
  custSel.innerHTML = appState.customers.map(function (c) {
    const bal = getCustomerBalance(c.name);
    return "<option value=\"" + c.name + "\">" + c.name + " (Due: PKR " + bal.toLocaleString() + ")</option>";
  }).join("");

  document.getElementById("mRcptAmount").value = "";
  document.getElementById("mRcptRef").value = "";
  onModalCustRcptChange();
  openModal("modalCustomerReceipt");
}

function onModalCustRcptChange() {
  const cust = document.getElementById("mRcptCustomer").value;
  const bal = getCustomerBalance(cust);
  const textEl = document.getElementById("mRcptCurrentBalText");
  if (textEl) {
    textEl.innerText = "Current Outstanding Receivable: PKR " + bal.toLocaleString();
  }
}

function handleCustomerReceiptSubmit(event) {
  event.preventDefault();
  const rcptNo = document.getElementById("mRcptNo").value;
  const date = document.getElementById("mRcptDate").value;
  const customer = document.getElementById("mRcptCustomer").value;
  const account = document.getElementById("mRcptAccount").value;
  const amount = parseFloat(document.getElementById("mRcptAmount").value) || 0;
  const ref = document.getElementById("mRcptRef").value;

  if (amount <= 0) { alert("Amount must be greater than 0"); return; }

  // Add to deposit account
  if (account === "Cash in Hand") {
    appState.accounts.cash += amount;
  } else {
    appState.accounts.bank += amount;
  }

  const newRcpt = {
    id: rcptNo,
    date: date,
    customer: customer,
    account: account,
    amount: amount,
    ref: ref
  };

  appState.customerPayments.unshift(newRcpt);
  saveDB();
  closeModal("modalCustomerReceipt");
  showToast("Customer payment of PKR " + amount.toLocaleString() + " recorded from " + customer + "!");
}

// -------------------------------------------------------------
// 8. MODAL: SUPPLIER PAYMENT VOUCHER
// -------------------------------------------------------------
function openSupplierPaymentModal() {
  const nextNo = "PAY-" + String(appState.supplierPayments.length + 1).padStart(3, "0");
  document.getElementById("mPayNo").value = nextNo;
  document.getElementById("mPayDate").value = new Date().toISOString().split("T")[0];

  const suppSel = document.getElementById("mPaySupplier");
  suppSel.innerHTML = appState.suppliers.map(function (s) {
    const bal = getSupplierBalance(s.name);
    return "<option value=\"" + s.name + "\">" + s.name + " (Due: PKR " + bal.toLocaleString() + ")</option>";
  }).join("");

  document.getElementById("mPayAmount").value = "";
  document.getElementById("mPayRef").value = "";
  onModalSuppPayChange();
  openModal("modalSupplierPayment");
}

function onModalSuppPayChange() {
  const supp = document.getElementById("mPaySupplier").value;
  const bal = getSupplierBalance(supp);
  const textEl = document.getElementById("mPayCurrentBalText");
  if (textEl) {
    textEl.innerText = "Current Outstanding Payable: PKR " + bal.toLocaleString();
  }
}

function handleSupplierPaymentSubmit(event) {
  event.preventDefault();
  const payNo = document.getElementById("mPayNo").value;
  const date = document.getElementById("mPayDate").value;
  const supplier = document.getElementById("mPaySupplier").value;
  const account = document.getElementById("mPayAccount").value;
  const amount = parseFloat(document.getElementById("mPayAmount").value) || 0;
  const ref = document.getElementById("mPayRef").value;

  if (amount <= 0) { alert("Amount must be greater than 0"); return; }

  // Deduct from payment account
  if (account === "Cash in Hand") {
    appState.accounts.cash -= amount;
  } else {
    appState.accounts.bank -= amount;
  }

  const newPay = {
    id: payNo,
    date: date,
    supplier: supplier,
    account: account,
    amount: amount,
    ref: ref
  };

  appState.supplierPayments.unshift(newPay);
  saveDB();
  closeModal("modalSupplierPayment");
  showToast("Supplier payment of PKR " + amount.toLocaleString() + " recorded for " + supplier + "!");
}

// -------------------------------------------------------------
// Financial Balances & Calculations
// -------------------------------------------------------------
function getCustomerBalance(custName) {
  let bal = 0;
  appState.sales.forEach(function (s) {
    if (s.customer === custName) {
      bal += s.totalSale;
      bal -= s.received;
    }
  });
  appState.customerPayments.forEach(function (p) {
    if (p.customer === custName) {
      bal -= p.amount;
    }
  });
  return bal;
}

function getSupplierBalance(suppName) {
  let bal = 0;
  appState.purchases.forEach(function (p) {
    if (p.supplier === suppName) {
      bal += p.total;
      bal -= p.paid;
    }
  });
  appState.supplierPayments.forEach(function (sp) {
    if (sp.supplier === suppName) {
      bal -= sp.amount;
    }
  });
  return bal;
}

function calculateTotals() {
  let totalSales = 0;
  let totalCOGS = 0;
  let totalGrossProfit = 0;

  appState.sales.forEach(function (s) {
    totalSales += s.totalSale;
    totalCOGS += s.totalCost;
    totalGrossProfit += s.profit;
  });

  let totalExpenses = 0;
  appState.expenses.forEach(function (e) {
    totalExpenses += e.amount;
  });

  const netProfit = totalGrossProfit - totalExpenses;
  const partnerShare = Math.round(netProfit * 0.5);

  let stockValuation = 0;
  appState.products.forEach(function (p) {
    stockValuation += (p.stock * p.costRate);
  });

  let totalReceivables = 0;
  appState.customers.forEach(function (c) {
    totalReceivables += getCustomerBalance(c.name);
  });

  let totalPayables = 0;
  appState.suppliers.forEach(function (s) {
    totalPayables += getSupplierBalance(s.name);
  });

  const totalCapitalPool = appState.partners.reduce(function (sum, p) { return sum + p.capital; }, 0);

  return {
    sales: totalSales,
    cogs: totalCOGS,
    grossProfit: totalGrossProfit,
    expenses: totalExpenses,
    netProfit: netProfit,
    partnerShare: partnerShare,
    stockValuation: stockValuation,
    receivables: totalReceivables,
    payables: totalPayables,
    capitalPool: totalCapitalPool,
    cash: appState.accounts.cash,
    bank: appState.accounts.bank
  };
}

// -------------------------------------------------------------
// Render All UI Views
// -------------------------------------------------------------
function renderAll() {
  const totals = calculateTotals();

  // 1. Dashboard Stats
  setInnerText("statSales", "PKR " + totals.sales.toLocaleString());
  setInnerText("statGrossProfit", "PKR " + totals.grossProfit.toLocaleString());
  setInnerText("statNetProfit", "PKR " + totals.netProfit.toLocaleString());
  setInnerText("statCashBank", "PKR " + (totals.cash + totals.bank).toLocaleString());
  setInnerText("statStockVal", "PKR " + totals.stockValuation.toLocaleString());
  setInnerText("statReceivables", "PKR " + totals.receivables.toLocaleString());
  setInnerText("statPayables", "PKR " + totals.payables.toLocaleString());
  setInnerText("statCapitalPool", "PKR " + totals.capitalPool.toLocaleString());

  setInnerText("dashP1Share", "PKR " + totals.partnerShare.toLocaleString());
  setInnerText("dashP2Share", "PKR " + totals.partnerShare.toLocaleString());

  // 2. Partners Tab
  const p1Draw = appState.drawings.filter(function (d) { return d.partner === "Partner 1"; }).reduce(function (s, d) { return s + d.amount; }, 0);
  const p2Draw = appState.drawings.filter(function (d) { return d.partner === "Partner 2"; }).reduce(function (s, d) { return s + d.amount; }, 0);
  const p1Cap = appState.partners[0].capital;
  const p2Cap = appState.partners[1].capital;
  const p1Avail = p1Cap + totals.partnerShare - p1Draw;
  const p2Avail = p2Cap + totals.partnerShare - p2Draw;

  setInnerText("p1Capital", "PKR " + p1Cap.toLocaleString());
  setInnerText("p1Drawings", "PKR " + p1Draw.toLocaleString());
  setInnerText("p1Balance", "PKR " + p1Avail.toLocaleString());

  setInnerText("p2Capital", "PKR " + p2Cap.toLocaleString());
  setInnerText("p2Drawings", "PKR " + p2Draw.toLocaleString());
  setInnerText("p2Balance", "PKR " + p2Avail.toLocaleString());

  // 3. Tables Rendering
  renderDashboardSales();
  renderPurchasesTable();
  renderSalesTable();
  renderCustomerSelect();
  renderCustomerLedger();
  renderSupplierSelect();
  renderSupplierLedger();
  renderExpensesTable(totals.expenses);
  renderStockTable(totals.stockValuation);
  renderAdjustmentsTable();
  renderCashBank(totals.cash, totals.bank);
  renderCapitalTable();
  renderDrawingsTable();
  renderMonthlyProfit(totals.sales, totals.cogs, totals.grossProfit, totals.expenses, totals.netProfit, totals.partnerShare);
}

function setInnerText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

function renderDashboardSales() {
  const tbody = document.getElementById("dashboardRecentSales");
  if (!tbody) return;
  const recents = appState.sales.slice(0, 5);
  tbody.innerHTML = recents.map(function (s) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + s.id + "</span></td>" +
      "<td class=\"fw-bold\">" + s.customer + "</td>" +
      "<td class=\"text-primary fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td class=\"text-muted\">PKR " + s.totalCost.toLocaleString() + "</td>" +
      "<td class=\"text-success fw-bold\">PKR " + s.profit.toLocaleString() + "</td>" +
      "<td><button class=\"btn btn-outline-primary btn-sm py-0\" onclick=\"previewInvoice('" + s.id + "')\"><i class=\"bi bi-printer\"></i> Bill</button></td>" +
      "</tr>";
  }).join("");
}

function renderPurchasesTable() {
  const tbody = document.getElementById("purchasesTableBody");
  const countBadge = document.getElementById("purCountBadge");
  if (countBadge) countBadge.innerText = appState.purchases.length + " Bills";
  if (!tbody) return;
  tbody.innerHTML = appState.purchases.map(function (p) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + p.id + "</span></td>" +
      "<td>" + p.date + "</td>" +
      "<td class=\"fw-bold\">" + p.supplier + "</td>" +
      "<td>" + p.item + "</td>" +
      "<td>" + p.qty + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-dark\">PKR " + p.total.toLocaleString() + "</td>" +
      "<td class=\"text-success\">PKR " + p.paid.toLocaleString() + "</td>" +
      "<td class=\"text-danger fw-bold\">PKR " + p.balance.toLocaleString() + "</td>" +
      "</tr>";
  }).join("");
}

function renderSalesTable() {
  const tbody = document.getElementById("salesTableBody");
  const countBadge = document.getElementById("saleCountBadge");
  if (countBadge) countBadge.innerText = appState.sales.length + " Invoices";
  if (!tbody) return;
  tbody.innerHTML = appState.sales.map(function (s) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + s.id + "</span></td>" +
      "<td>" + s.date + "</td>" +
      "<td class=\"fw-bold\">" + s.customer + "</td>" +
      "<td>" + s.item + "</td>" +
      "<td>" + s.qty + "</td>" +
      "<td class=\"text-primary fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td class=\"text-muted\">PKR " + s.totalCost.toLocaleString() + "</td>" +
      "<td class=\"text-success fw-bold\">PKR " + s.profit.toLocaleString() + "</td>" +
      "<td class=\"text-success\">PKR " + s.received.toLocaleString() + "</td>" +
      "<td class=\"text-danger fw-bold\">PKR " + s.balance.toLocaleString() + "</td>" +
      "<td><button class=\"btn btn-outline-primary btn-sm py-0\" onclick=\"previewInvoice('" + s.id + "')\"><i class=\"bi bi-printer\"></i> Bill</button></td>" +
      "</tr>";
  }).join("");
}

function renderCustomerSelect() {
  const sel = document.getElementById("ledgerCustomerSelect");
  if (!sel || sel.options.length > 0) return;
  sel.innerHTML = appState.customers.map(function (c) {
    return "<option value=\"" + c.name + "\">" + c.name + " (" + c.city + ")</option>";
  }).join("");
}

function renderCustomerLedger() {
  const sel = document.getElementById("ledgerCustomerSelect");
  if (!sel) return;
  const cust = sel.value || (appState.customers[0] ? appState.customers[0].name : "");
  const tbody = document.getElementById("custLedgerBody");
  const titleEl = document.getElementById("custLedgerTitle");
  if (titleEl) titleEl.innerText = "Customer Ledger: " + cust;

  const cSales = appState.sales.filter(function (s) { return s.customer === cust; });
  const cPayments = appState.customerPayments.filter(function (p) { return p.customer === cust; });

  let runBal = 0;
  let html = "";

  cSales.forEach(function (s) {
    runBal += s.totalSale;
    html += "<tr>" +
      "<td>" + s.date + "</td>" +
      "<td>Invoice " + s.id + " (" + s.item + " x " + s.qty + ")</td>" +
      "<td class=\"fw-bold text-dark\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td>-</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";

    if (s.received > 0) {
      runBal -= s.received;
      html += "<tr class=\"table-light\">" +
        "<td>" + s.date + "</td>" +
        "<td>Cash Received on Invoice (" + s.id + ")</td>" +
        "<td>-</td>" +
        "<td class=\"text-success fw-bold\">PKR " + s.received.toLocaleString() + "</td>" +
        "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
        "</tr>";
    }
  });

  cPayments.forEach(function (p) {
    runBal -= p.amount;
    html += "<tr class=\"table-success-subtle\">" +
      "<td>" + p.date + "</td>" +
      "<td>Market Recovery: " + p.id + " (" + p.ref + ")</td>" +
      "<td>-</td>" +
      "<td class=\"text-success fw-bold\">PKR " + p.amount.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";
  });

  if (tbody) {
    tbody.innerHTML = html || '<tr><td colspan="5" class="text-center py-3 text-muted">No transaction history found for this customer</td></tr>';
  }
  const balEl = document.getElementById("custLedgerBalance");
  if (balEl) balEl.innerText = "Receivable: PKR " + runBal.toLocaleString();
}

function printCustomerLedger() {
  window.print();
}

function renderSupplierSelect() {
  const sel = document.getElementById("ledgerSupplierSelect");
  if (!sel || sel.options.length > 0) return;
  sel.innerHTML = appState.suppliers.map(function (s) {
    return "<option value=\"" + s.name + "\">" + s.name + " (" + s.city + ")</option>";
  }).join("");
}

function renderSupplierLedger() {
  const sel = document.getElementById("ledgerSupplierSelect");
  if (!sel) return;
  const supp = sel.value || (appState.suppliers[0] ? appState.suppliers[0].name : "");
  const tbody = document.getElementById("suppLedgerBody");
  const titleEl = document.getElementById("suppLedgerTitle");
  if (titleEl) titleEl.innerText = "Supplier Ledger: " + supp;

  const sPurchases = appState.purchases.filter(function (p) { return p.supplier === supp; });
  const sPayments = appState.supplierPayments.filter(function (sp) { return sp.supplier === supp; });

  let runBal = 0;
  let html = "";

  sPurchases.forEach(function (p) {
    runBal += p.total;
    html += "<tr>" +
      "<td>" + p.date + "</td>" +
      "<td>Purchase Bill " + p.id + " (" + p.item + " x " + p.qty + ")</td>" +
      "<td>-</td>" +
      "<td class=\"fw-bold text-dark\">PKR " + p.total.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";

    if (p.paid > 0) {
      runBal -= p.paid;
      html += "<tr class=\"table-light\">" +
        "<td>" + p.date + "</td>" +
        "<td>Payment Made at Invoicing</td>" +
        "<td class=\"text-success fw-bold\">PKR " + p.paid.toLocaleString() + "</td>" +
        "<td>-</td>" +
        "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
        "</tr>";
    }
  });

  sPayments.forEach(function (sp) {
    runBal -= sp.amount;
    html += "<tr class=\"table-info-subtle\">" +
      "<td>" + sp.date + "</td>" +
      "<td>Bank Payment: " + sp.id + " (" + sp.ref + ")</td>" +
      "<td class=\"text-success fw-bold\">PKR " + sp.amount.toLocaleString() + "</td>" +
      "<td>-</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";
  });

  if (tbody) {
    tbody.innerHTML = html || '<tr><td colspan="5" class="text-center py-3 text-muted">No transaction history found for this supplier</td></tr>';
  }
  const balEl = document.getElementById("suppLedgerBalance");
  if (balEl) balEl.innerText = "Payable Due: PKR " + runBal.toLocaleString();
}

function printSupplierLedger() {
  window.print();
}

function renderExpensesTable(totalExp) {
  const tbody = document.getElementById("expenseTableBody");
  const badge = document.getElementById("expTotalBadge");
  if (badge) badge.innerText = "Total: PKR " + totalExp.toLocaleString();
  if (!tbody) return;
  tbody.innerHTML = appState.expenses.map(function (e) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + e.id + "</span></td>" +
      "<td>" + e.date + "</td>" +
      "<td><span class=\"badge bg-secondary\">" + e.category + "</span></td>" +
      "<td>" + e.desc + "</td>" +
      "<td><i class=\"bi bi-credit-card text-muted me-1\"></i>" + e.account + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + e.amount.toLocaleString() + "</td>" +
      "</tr>";
  }).join("");
}

function renderStockTable(val) {
  const tbody = document.getElementById("stockTableBody");
  const badge = document.getElementById("stockValBadge");
  if (badge) badge.innerText = "Valuation: PKR " + val.toLocaleString();
  if (!tbody) return;
  tbody.innerHTML = appState.products.map(function (p) {
    const itemVal = p.stock * p.costRate;
    const isLow = p.stock < 15;
    return "<tr>" +
      "<td class=\"fw-bold\">" + p.name + "</td>" +
      "<td><span class=\"badge bg-light text-dark border\">" + p.category + "</span></td>" +
      "<td>" + p.unit + "</td>" +
      "<td class=\"fw-bold " + (isLow ? "text-danger" : "text-dark") + "\">" + p.stock + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td>PKR " + p.saleRate.toLocaleString() + "</td>" +
      "<td class=\"fw-bold text-primary\">PKR " + itemVal.toLocaleString() + "</td>" +
      "<td><span class=\"badge " + (isLow ? "bg-warning text-dark" : "bg-success") + "\">" + (isLow ? "Low Stock" : "In Stock") + "</span></td>" +
      "</tr>";
  }).join("");
}

function renderAdjustmentsTable() {
  const tbody = document.getElementById("adjustmentTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.adjustments.map(function (a) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + a.id + "</span></td>" +
      "<td>" + a.date + "</td>" +
      "<td class=\"fw-bold\">" + a.product + "</td>" +
      "<td>" + a.qty + "</td>" +
      "<td><span class=\"badge bg-danger\">" + a.type + "</span></td>" +
      "<td>" + a.notes + "</td>" +
      "</tr>";
  }).join("");
}

function renderCashBank(cash, bank) {
  setInnerText("cashInHandVal", "PKR " + cash.toLocaleString());
  setInnerText("bankAccountVal", "PKR " + bank.toLocaleString());
}

function renderCapitalTable() {
  const tbody = document.getElementById("capitalTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.capitalTransactions.map(function (c) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + c.id + "</span></td>" +
      "<td>" + c.date + "</td>" +
      "<td class=\"fw-bold text-primary\">" + c.partner + "</td>" +
      "<td>" + c.account + "</td>" +
      "<td><span class=\"badge bg-info text-dark\">" + c.type + "</span></td>" +
      "<td class=\"fw-bold text-success\">PKR " + c.amount.toLocaleString() + "</td>" +
      "<td>" + c.remarks + "</td>" +
      "</tr>";
  }).join("");
}

function renderDrawingsTable() {
  const tbody = document.getElementById("drawingsTableBody");
  const countBadge = document.getElementById("drawingCountBadge");
  if (countBadge) countBadge.innerText = appState.drawings.length + " Records";
  if (!tbody) return;
  tbody.innerHTML = appState.drawings.map(function (d) {
    return "<tr>" +
      "<td><span class=\"badge bg-light text-dark border\">" + d.id + "</span></td>" +
      "<td>" + d.date + "</td>" +
      "<td class=\"fw-bold text-warning-emphasis\">" + d.partner + "</td>" +
      "<td>" + d.account + "</td>" +
      "<td class=\"fw-bold text-danger\">PKR " + d.amount.toLocaleString() + "</td>" +
      "<td>" + d.remarks + "</td>" +
      "</tr>";
  }).join("");
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

// -------------------------------------------------------------
// Wholesale Invoice Preview & Print
// -------------------------------------------------------------
function previewInvoice(invId) {
  const s = appState.sales.find(function (x) { return x.id === invId; });
  if (!s) return;

  setInnerText("invNoModal", s.id);
  setInnerText("invDateModal", "Date: " + s.date);
  setInnerText("invCustModal", s.customer);

  const itemsEl = document.getElementById("invItemsModal");
  if (itemsEl) {
    itemsEl.innerHTML = "<tr>" +
      "<td><strong>" + s.item + "</strong></td>" +
      "<td class=\"text-center\">" + s.qty + "</td>" +
      "<td class=\"text-end\">PKR " + s.saleRate.toLocaleString() + "</td>" +
      "<td class=\"text-end fw-bold\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "</tr>";
  }

  setInnerText("invTotalModal", "PKR " + s.totalSale.toLocaleString());
  setInnerText("invRecModal", "PKR " + s.received.toLocaleString());
  setInnerText("invBalModal", "PKR " + s.balance.toLocaleString());

  openModal("invoiceModal");
}

// -------------------------------------------------------------
// App Bootstrap
// -------------------------------------------------------------
window.addEventListener("DOMContentLoaded", function () {
  loadDB();
  renderAll();
  showTab("dashboard");
});
