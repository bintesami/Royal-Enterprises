# -*- coding: utf-8 -*-
"""
build_frontend.py
Generates clean, syntax-verified index.html and app.js for Royal Enterprises Crockery Wholesale System.
Includes all 11 modules, 8 dedicated interactive modal forms, database engine, ledger computation, and invoice printing.
"""

import sys
import os

def generate_index_html():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Royal Enterprises - Crockery Wholesale Partnership Accounting</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="d-flex min-vh-100">
  <!-- Mobile Backdrop -->
  <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeSidebar()"></div>

  <!-- Sidebar -->
  <aside class="sidebar d-flex flex-column" id="sidebar">
    <div class="sidebar-brand justify-content-between">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-cup-hot-fill text-warning fs-3"></i>
        <div>
          <div class="text-white">Royal Enterprises</div>
          <small class="text-secondary" style="font-size:0.75rem">Crockery Wholesale ERP</small>
        </div>
      </div>
      <button class="btn btn-sm text-secondary d-lg-none" onclick="closeSidebar()"><i class="bi bi-x-lg fs-5"></i></button>
    </div>
    <ul class="sidebar-menu flex-grow-1">
      <li><a class="nav-item-link active" data-tab="dashboard" onclick="showTab('dashboard')"><i class="bi bi-grid-1x2-fill"></i> Dashboard</a></li>
      <li><a class="nav-item-link" data-tab="partners" onclick="showTab('partners')"><i class="bi bi-people-fill"></i> Partners Capital</a></li>
      <li><a class="nav-item-link" data-tab="purchases" onclick="showTab('purchases')"><i class="bi bi-bag-plus-fill"></i> Purchases</a></li>
      <li><a class="nav-item-link" data-tab="sales" onclick="showTab('sales')"><i class="bi bi-receipt-cutoff"></i> Sales (Create Bill)</a></li>
      <li><a class="nav-item-link" data-tab="customer-ledger" onclick="showTab('customer-ledger')"><i class="bi bi-person-lines-fill"></i> Customer Ledger</a></li>
      <li><a class="nav-item-link" data-tab="supplier-ledger" onclick="showTab('supplier-ledger')"><i class="bi bi-truck"></i> Supplier Ledger</a></li>
      <li><a class="nav-item-link" data-tab="expenses" onclick="showTab('expenses')"><i class="bi bi-wallet2"></i> Expenses</a></li>
      <li><a class="nav-item-link" data-tab="stock" onclick="showTab('stock')"><i class="bi bi-boxes"></i> Stock Inventory</a></li>
      <li><a class="nav-item-link" data-tab="cash-bank" onclick="showTab('cash-bank')"><i class="bi bi-bank2"></i> Cash & Bank</a></li>
      <li><a class="nav-item-link" data-tab="drawings" onclick="showTab('drawings')"><i class="bi bi-cash-stack"></i> Partner Drawings</a></li>
      <li><a class="nav-item-link" data-tab="monthly-profit" onclick="showTab('monthly-profit')"><i class="bi bi-graph-up-arrow"></i> Monthly Profit</a></li>
    </ul>
    <div class="p-3 border-top border-secondary text-secondary small">
      <div class="d-flex align-items-center justify-content-between mb-1">
        <span class="badge bg-success">Database Connected</span>
        <small class="text-white-50">v2.5</small>
      </div>
      <div>11 Integrated Modules</div>
    </div>
  </aside>

  <!-- Main Content Area -->
  <main class="main-content">
    <!-- Toast Notification Container -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 2000;">
      <div id="liveToast" class="toast align-items-center text-white bg-success border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body" id="toastMessage">Entry saved successfully!</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>

    <!-- Mobile Top Navigation Bar -->
    <div class="mobile-top-bar d-lg-none mb-3 rounded-2">
      <button class="btn btn-outline-light btn-sm" onclick="toggleSidebar()"><i class="bi bi-list fs-5"></i> Menu</button>
      <div class="fw-bold fs-6">Royal Enterprises</div>
      <button class="btn btn-primary btn-sm" onclick="openNewSaleModal()"><i class="bi bi-plus-lg"></i> Bill</button>
    </div>

    <!-- Page Header Bar with Context Action & Quick New Entry Menu -->
    <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom top-header-wrap">
      <div>
        <h3 class="fw-bold mb-0" id="pageTitle">Dashboard Overview</h3>
        <small class="text-muted" id="pageSubTitle">Real-Time Crockery Wholesale Accounting & Inventory</small>
      </div>
      <div class="d-flex gap-2 top-header-actions align-items-center">
        <!-- Quick Action Dropdown: Open ANY form from ANY tab -->
        <div class="dropdown">
          <button class="btn btn-outline-primary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="bi bi-grid-3x3-gap"></i> Quick Entry
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow">
            <li><h6 class="dropdown-header">Wholesale Actions</h6></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewSaleModal()"><i class="bi bi-receipt text-primary me-2"></i> Create Wholesale Bill (Sale)</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewPurchaseModal()"><i class="bi bi-bag-plus text-success me-2"></i> Record Purchase Invoice</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewExpenseModal()"><i class="bi bi-wallet2 text-danger me-2"></i> Record Expense</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openCustomerReceiptModal()"><i class="bi bi-cash-coin text-warning me-2"></i> Receive Customer Payment</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openSupplierPaymentModal()"><i class="bi bi-truck text-info me-2"></i> Pay Supplier</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><h6 class="dropdown-header">Partners & Stock</h6></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewCapitalModal()"><i class="bi bi-people text-primary me-2"></i> Add Partner Capital</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewDrawingModal()"><i class="bi bi-cash-stack text-warning me-2"></i> Record Partner Drawing</a></li>
            <li><a class="dropdown-item" href="javascript:void(0)" onclick="openNewAdjustmentModal()"><i class="bi bi-slash-circle text-danger me-2"></i> Stock Breakage / Adjustment</a></li>
          </ul>
        </div>

        <!-- Dynamic Context Action Button (adapts to currently active tab) -->
        <button class="btn btn-primary btn-sm fw-bold" id="headerActionBtn" onclick="handleHeaderAction()">
          <i class="bi bi-plus-circle" id="headerActionIcon"></i> <span id="headerActionText">Create Bill</span>
        </button>

        <!-- Backup & Reset Tools -->
        <button class="btn btn-outline-secondary btn-sm" onclick="exportDatabaseJSON()" title="Export Database Backup (JSON)"><i class="bi bi-download"></i> Backup</button>
        <button class="btn btn-outline-danger btn-sm" onclick="resetSampleData()" title="Reset to Default Data"><i class="bi bi-arrow-counterclockwise"></i></button>
      </div>
    </div>

    <!-- TAB 1: DASHBOARD -->
    <div id="tab-dashboard" class="tab-pane-custom">
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Total Sales (Revenue)</div>
            <div class="stat-val text-primary" id="statSales">PKR 0</div>
            <small class="text-muted">Invoiced wholesale sales</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Gross Profit (Sales - COGS)</div>
            <div class="stat-val text-success" id="statGrossProfit">PKR 0</div>
            <small class="text-success">Margin before expenses</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Net Profit</div>
            <div class="stat-val text-success" id="statNetProfit">PKR 0</div>
            <small class="text-muted">Gross Profit - Expenses</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Cash & Bank Balance</div>
            <div class="stat-val text-info" id="statCashBank">PKR 0</div>
            <small class="text-muted">Available liquidity</small>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Stock Valuation (at Cost)</div>
            <div class="stat-val" id="statStockVal">PKR 0</div>
            <small class="text-muted">Current inventory value</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Customer Receivables</div>
            <div class="stat-val text-warning" id="statReceivables">PKR 0</div>
            <small class="text-muted">Market credit balance</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Supplier Payables</div>
            <div class="stat-val text-danger" id="statPayables">PKR 0</div>
            <small class="text-muted">Pending supplier bills</small>
          </div>
        </div>
        <div class="col-6 col-md-6 col-xl-3">
          <div class="stat-card">
            <div class="stat-label">Total Capital Pool</div>
            <div class="stat-val text-secondary" id="statCapitalPool">PKR 0</div>
            <small class="text-muted">50/50 Partner Investments</small>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
              <span>Recent Wholesale Invoices</span>
              <button class="btn btn-primary btn-sm" onclick="openNewSaleModal()"><i class="bi bi-plus-circle"></i> + Create Wholesale Bill</button>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light small">
                    <tr>
                      <th>Invoice #</th>
                      <th>Customer</th>
                      <th>Total Sale</th>
                      <th>COGS</th>
                      <th>Profit</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody id="dashboardRecentSales"></tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white fw-bold py-3">Partnership 50/50 Split</div>
            <div class="card-body">
              <div class="mb-3">
                <div class="d-flex justify-content-between small fw-bold mb-1">
                  <span>Partner 1 (50%)</span>
                  <span id="dashP1Share">PKR 0</span>
                </div>
                <div class="progress" style="height: 8px;">
                  <div class="progress-bar bg-primary" style="width: 50%"></div>
                </div>
              </div>
              <div class="mb-3">
                <div class="d-flex justify-content-between small fw-bold mb-1">
                  <span>Partner 2 (50%)</span>
                  <span id="dashP2Share">PKR 0</span>
                </div>
                <div class="progress" style="height: 8px;">
                  <div class="progress-bar bg-info" style="width: 50%"></div>
                </div>
              </div>
              <hr>
              <div class="d-grid gap-2">
                <button class="btn btn-outline-primary btn-sm" onclick="openNewCapitalModal()"><i class="bi bi-people"></i> Add Capital</button>
                <button class="btn btn-outline-warning btn-sm" onclick="openNewDrawingModal()"><i class="bi bi-cash-stack"></i> Record Drawing</button>
                <button class="btn btn-outline-secondary btn-sm" onclick="showTab('monthly-profit')"><i class="bi bi-graph-up"></i> View Monthly Sharing</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: PARTNERS CAPITAL -->
    <div id="tab-partners" class="tab-pane-custom">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0">Partner Equity & Capital Accounts</h5>
        <div class="d-flex gap-2">
          <button class="btn btn-primary btn-sm" onclick="openNewCapitalModal()"><i class="bi bi-plus-circle"></i> + Add Capital Contribution</button>
          <button class="btn btn-warning btn-sm text-dark" onclick="openNewDrawingModal()"><i class="bi bi-cash-stack"></i> + Record Drawing</button>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm border-top border-primary border-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="fw-bold mb-0 text-primary">Partner 1</h5>
                <span class="badge bg-primary">50% Profit Share</span>
              </div>
              <div class="row g-2 mt-2">
                <div class="col-6">
                  <div class="stat-label">Initial / Invested Capital</div>
                  <div class="h5 fw-bold text-dark" id="p1Capital">PKR 0</div>
                </div>
                <div class="col-6">
                  <div class="stat-label">Total Drawings Withdrawn</div>
                  <div class="h5 fw-bold text-danger" id="p1Drawings">PKR 0</div>
                </div>
                <div class="col-12 mt-2 pt-2 border-top">
                  <div class="stat-label">Current Available Equity (Capital + 50% Profit - Drawings)</div>
                  <div class="h3 text-success fw-bold" id="p1Balance">PKR 0</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card border-0 shadow-sm border-top border-info border-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="fw-bold mb-0 text-info">Partner 2</h5>
                <span class="badge bg-info">50% Profit Share</span>
              </div>
              <div class="row g-2 mt-2">
                <div class="col-6">
                  <div class="stat-label">Initial / Invested Capital</div>
                  <div class="h5 fw-bold text-dark" id="p2Capital">PKR 0</div>
                </div>
                <div class="col-6">
                  <div class="stat-label">Total Drawings Withdrawn</div>
                  <div class="h5 fw-bold text-danger" id="p2Drawings">PKR 0</div>
                </div>
                <div class="col-12 mt-2 pt-2 border-top">
                  <div class="stat-label">Current Available Equity (Capital + 50% Profit - Drawings)</div>
                  <div class="h3 text-success fw-bold" id="p2Balance">PKR 0</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Capital Transactions Log -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <span>Capital Contributions Log</span>
          <button class="btn btn-outline-primary btn-sm" onclick="openNewCapitalModal()"><i class="bi bi-plus-circle"></i> + Add Capital</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Voucher #</th>
                  <th>Date</th>
                  <th>Partner</th>
                  <th>Deposit Account</th>
                  <th>Contribution Type</th>
                  <th>Amount</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody id="capitalTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: PURCHASES -->
    <div id="tab-purchases" class="tab-pane-custom">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-6">Purchase Invoices Register</span>
            <span class="badge bg-primary ms-2" id="purCountBadge">0 Bills</span>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openNewPurchaseModal()"><i class="bi bi-plus-circle"></i> + Record Purchase Invoice</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Invoice #</th>
                  <th>Date</th>
                  <th>Supplier</th>
                  <th>Item</th>
                  <th>Qty</th>
                  <th>Cost Rate</th>
                  <th>Total Cost</th>
                  <th>Paid</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody id="purchasesTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: SALES -->
    <div id="tab-sales" class="tab-pane-custom">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-6">Wholesale Sales Register</span>
            <span class="badge bg-success ms-2" id="saleCountBadge">0 Invoices</span>
          </div>
          <button class="btn btn-success btn-sm" onclick="openNewSaleModal()"><i class="bi bi-plus-circle"></i> + Create Wholesale Bill</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Invoice #</th>
                  <th>Date</th>
                  <th>Customer</th>
                  <th>Item</th>
                  <th>Qty</th>
                  <th>Sale Total</th>
                  <th>COGS</th>
                  <th>Profit</th>
                  <th>Received</th>
                  <th>Balance</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="salesTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 5: CUSTOMER LEDGER -->
    <div id="tab-customer-ledger" class="tab-pane-custom">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-center">
            <div class="col-md-5">
              <label class="form-label small fw-bold">Select Customer Account</label>
              <select class="form-select form-select-sm" id="ledgerCustomerSelect" onchange="renderCustomerLedger()"></select>
            </div>
            <div class="col-md-7 text-end d-flex gap-2 justify-content-end align-items-end">
              <button class="btn btn-warning btn-sm text-dark" onclick="openCustomerReceiptModal()"><i class="bi bi-cash-coin"></i> + Receive Customer Payment</button>
              <button class="btn btn-outline-secondary btn-sm" onclick="printCustomerLedger()"><i class="bi bi-printer"></i> Print Statement</button>
            </div>
          </div>
        </div>
      </div>
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <span id="custLedgerTitle">Customer Statement</span>
          <span class="badge bg-warning text-dark fs-6" id="custLedgerBalance">Balance: PKR 0</span>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Date</th>
                  <th>Ref # / Transaction Details</th>
                  <th>Debit (Sale Invoiced)</th>
                  <th>Credit (Cash Received)</th>
                  <th>Running Balance</th>
                </tr>
              </thead>
              <tbody id="custLedgerBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 6: SUPPLIER LEDGER -->
    <div id="tab-supplier-ledger" class="tab-pane-custom">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-center">
            <div class="col-md-5">
              <label class="form-label small fw-bold">Select Supplier Account</label>
              <select class="form-select form-select-sm" id="ledgerSupplierSelect" onchange="renderSupplierLedger()"></select>
            </div>
            <div class="col-md-7 text-end d-flex gap-2 justify-content-end align-items-end">
              <button class="btn btn-danger btn-sm text-white" onclick="openSupplierPaymentModal()"><i class="bi bi-credit-card"></i> + Pay Supplier</button>
              <button class="btn btn-outline-secondary btn-sm" onclick="printSupplierLedger()"><i class="bi bi-printer"></i> Print Statement</button>
            </div>
          </div>
        </div>
      </div>
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <span id="suppLedgerTitle">Supplier Statement</span>
          <span class="badge bg-danger fs-6" id="suppLedgerBalance">Balance: PKR 0</span>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Date</th>
                  <th>Ref # / Transaction Details</th>
                  <th>Debit (Payment Made)</th>
                  <th>Credit (Purchase Bill)</th>
                  <th>Running Balance</th>
                </tr>
              </thead>
              <tbody id="suppLedgerBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 7: EXPENSES -->
    <div id="tab-expenses" class="tab-pane-custom">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-6">Business Operating Expenses</span>
            <span class="badge bg-danger ms-2" id="expTotalBadge">PKR 0</span>
          </div>
          <button class="btn btn-danger btn-sm" onclick="openNewExpenseModal()"><i class="bi bi-plus-circle"></i> + Record New Expense</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Voucher #</th>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Description / Paid To</th>
                  <th>Payment Account</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody id="expenseTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 8: STOCK INVENTORY -->
    <div id="tab-stock" class="tab-pane-custom">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-6">Crockery Stock Status & Inventory Valuation</span>
            <span class="badge bg-info ms-2" id="stockValBadge">Valuation: PKR 0</span>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-danger btn-sm" onclick="openNewAdjustmentModal()"><i class="bi bi-slash-circle"></i> + Record Breakage / Adjustment</button>
            <button class="btn btn-primary btn-sm" onclick="openNewPurchaseModal()"><i class="bi bi-bag-plus"></i> + Add Stock (Purchase)</button>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Unit</th>
                  <th>Stock Qty</th>
                  <th>Cost Rate</th>
                  <th>Sale Rate</th>
                  <th>Valuation (Cost)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="stockTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Breakage & Adjustments Log -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <span>Damage & Stock Breakage Log</span>
          <button class="btn btn-outline-danger btn-sm" onclick="openNewAdjustmentModal()"><i class="bi bi-plus-circle"></i> + Write Off Breakage</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Voucher #</th>
                  <th>Date</th>
                  <th>Product Item</th>
                  <th>Qty Adjusted</th>
                  <th>Adjustment Type</th>
                  <th>Reason / Notes</th>
                </tr>
              </thead>
              <tbody id="adjustmentTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 9: CASH & BANK -->
    <div id="tab-cash-bank" class="tab-pane-custom">
      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="stat-card border-top border-success border-3">
            <div class="stat-label">Cash in Hand (Shop Drawer)</div>
            <div class="stat-val text-success" id="cashInHandVal">PKR 0</div>
            <small class="text-muted">Available physical cash</small>
          </div>
        </div>
        <div class="col-md-6">
          <div class="stat-card border-top border-primary border-3">
            <div class="stat-label">Main Bank Account Balance</div>
            <div class="stat-val text-primary" id="bankAccountVal">PKR 0</div>
            <small class="text-muted">Commercial bank account liquidity</small>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <span>Cash & Bank Summary</span>
          <div class="d-flex gap-2">
            <button class="btn btn-warning btn-sm text-dark" onclick="openCustomerReceiptModal()"><i class="bi bi-cash"></i> + Customer Cash Receipt</button>
            <button class="btn btn-danger btn-sm" onclick="openNewExpenseModal()"><i class="bi bi-wallet2"></i> + Cash Expense</button>
          </div>
        </div>
        <div class="card-body">
          <p class="text-muted mb-0">All cash transactions from Sales, Purchases, Expenses, Partner Capital, and Drawings automatically reconcile with these balances in real time.</p>
        </div>
      </div>
    </div>

    <!-- TAB 10: PARTNER DRAWINGS -->
    <div id="tab-drawings" class="tab-pane-custom">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-6">Partner Drawings Register</span>
            <span class="badge bg-warning text-dark ms-2" id="drawingCountBadge">0 Records</span>
          </div>
          <button class="btn btn-warning btn-sm text-dark" onclick="openNewDrawingModal()"><i class="bi bi-plus-circle"></i> + Record Partner Drawing</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Voucher #</th>
                  <th>Date</th>
                  <th>Partner</th>
                  <th>Withdrawn Account</th>
                  <th>Amount</th>
                  <th>Remarks / Purpose</th>
                </tr>
              </thead>
              <tbody id="drawingsTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 11: MONTHLY PROFIT -->
    <div id="tab-monthly-profit" class="tab-pane-custom">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-bold py-3">Monthly Profit & 50/50 Sharing Summary</div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-bordered align-middle text-center">
              <thead class="table-dark">
                <tr>
                  <th>Period</th>
                  <th>Sales Revenue</th>
                  <th>COGS (Cost)</th>
                  <th>Gross Profit</th>
                  <th>Expenses</th>
                  <th>Net Profit</th>
                  <th>Partner 1 (50%)</th>
                  <th>Partner 2 (50%)</th>
                </tr>
              </thead>
              <tbody id="monthlyProfitBody"></tbody>
            </table>
          </div>
          <div class="alert alert-info mt-3 mb-0 small">
            <i class="bi bi-info-circle-fill"></i> <strong>Perpetual Crockery Wholesale Accounting:</strong> Gross profit is calculated continuously as (Wholesale Sales - Cost of Goods Sold). Net profit deducts all shop rent, labor, freight, and utility operating expenses, then splits equally (50% each) into each partner's current account balance.
          </div>
        </div>
      </div>
    </div>

  </main>
</div>

<!-- ========================================== -->
<!-- 8 DEDICATED MODAL FORMS + INVOICE MODAL -->
<!-- ========================================== -->

<!-- MODAL 1: Wholesale Sale Bill / Invoice Form -->
<div class="modal fade" id="modalNewSale" tabindex="-1" aria-labelledby="modalNewSaleLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header bg-primary text-white">
        <h5 class="modal-title fw-bold" id="modalNewSaleLabel"><i class="bi bi-receipt-cutoff me-2"></i> Create Wholesale Bill / Sale Invoice</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalSaleForm" onsubmit="handleNewSaleSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label small fw-bold">Invoice Number</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mSaleInvNo" readonly>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mSaleDate" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Customer</label>
              <select class="form-select form-select-sm" id="mSaleCustomer" required></select>
            </div>

            <div class="col-md-8">
              <div class="d-flex justify-content-between align-items-center">
                <label class="form-label small fw-bold">Product Item</label>
                <span class="badge bg-secondary mb-1" id="mSaleStockBadge">Available Stock: 0</span>
              </div>
              <select class="form-select form-select-sm" id="mSaleProduct" onchange="onModalSaleProductChange()" required></select>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Quantity</label>
              <input type="number" class="form-control form-control-sm" id="mSaleQty" min="1" value="1" oninput="calcModalSale()" required>
            </div>

            <div class="col-md-4">
              <label class="form-label small fw-bold">Wholesale Sale Rate (PKR)</label>
              <input type="number" class="form-control form-control-sm" id="mSaleRate" min="1" oninput="calcModalSale()" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Total Bill Amount</label>
              <input type="text" class="form-control form-control-sm bg-light fw-bold text-primary" id="mSaleTotalDisplay" readonly value="PKR 0">
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Deposit Account</label>
              <select class="form-select form-select-sm" id="mSaleAccount">
                <option value="Cash in Hand">Cash in Hand</option>
                <option value="Main Bank Account">Main Bank Account</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label small fw-bold">Cash Received Now (PKR)</label>
              <input type="number" class="form-control form-control-sm" id="mSaleReceived" min="0" value="0" oninput="calcModalSale()">
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Balance (Customer Credit)</label>
              <input type="text" class="form-control form-control-sm bg-light fw-bold text-danger" id="mSaleBalanceDisplay" readonly value="PKR 0">
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-success btn-sm"><i class="bi bi-check2-circle"></i> Save & Print Wholesale Invoice</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 2: Record Purchase Invoice Form -->
<div class="modal fade" id="modalNewPurchase" tabindex="-1" aria-labelledby="modalNewPurchaseLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="modalNewPurchaseLabel"><i class="bi bi-bag-plus me-2"></i> Record Purchase Invoice (Stock Addition)</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalPurForm" onsubmit="handleNewPurchaseSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label small fw-bold">Purchase Order / Bill #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mPurNo" readonly>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mPurDate" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Supplier</label>
              <select class="form-select form-select-sm" id="mPurSupplier" required></select>
            </div>

            <div class="col-md-8">
              <label class="form-label small fw-bold">Product Item</label>
              <select class="form-select form-select-sm" id="mPurProduct" onchange="onModalPurProductChange()" required></select>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Quantity Received</label>
              <input type="number" class="form-control form-control-sm" id="mPurQty" min="1" value="10" oninput="calcModalPur()" required>
            </div>

            <div class="col-md-4">
              <label class="form-label small fw-bold">Cost Rate (PKR)</label>
              <input type="number" class="form-control form-control-sm" id="mPurCostRate" min="1" oninput="calcModalPur()" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Total Bill Amount</label>
              <input type="text" class="form-control form-control-sm bg-light fw-bold text-dark" id="mPurTotalDisplay" readonly value="PKR 0">
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold">Payment Account</label>
              <select class="form-select form-select-sm" id="mPurAccount">
                <option value="Main Bank Account">Main Bank Account</option>
                <option value="Cash in Hand">Cash in Hand</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label small fw-bold">Amount Paid Now (PKR)</label>
              <input type="number" class="form-control form-control-sm" id="mPurPaid" min="0" value="0" oninput="calcModalPur()">
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Balance (Supplier Payable)</label>
              <input type="text" class="form-control form-control-sm bg-light fw-bold text-danger" id="mPurBalanceDisplay" readonly value="PKR 0">
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary btn-sm"><i class="bi bi-check2-circle"></i> Save Purchase & Update Stock</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 3: Record Business Expense Form -->
<div class="modal fade" id="modalNewExpense" tabindex="-1" aria-labelledby="modalNewExpenseLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-danger text-white">
        <h5 class="modal-title fw-bold" id="modalNewExpenseLabel"><i class="bi bi-wallet2 me-2"></i> Record Business Expense</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalExpForm" onsubmit="handleNewExpenseSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Voucher #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mExpNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mExpDate" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Expense Head</label>
              <select class="form-select form-select-sm" id="mExpCategory" required>
                <option value="Shop Rent">Shop Rent</option>
                <option value="Electricity Bill">Electricity Bill</option>
                <option value="Labor & Wages">Labor & Wages</option>
                <option value="Freight & Carriage">Freight & Carriage</option>
                <option value="Tea & Refreshment">Tea & Refreshment</option>
                <option value="Packaging Material">Packaging Material</option>
                <option value="Shop Maintenance">Shop Maintenance</option>
                <option value="Miscellaneous">Miscellaneous</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Paid From Account</label>
              <select class="form-select form-select-sm" id="mExpAccount">
                <option value="Cash in Hand">Cash in Hand</option>
                <option value="Main Bank Account">Main Bank Account</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Amount (PKR)</label>
              <input type="number" class="form-control form-control-sm fw-bold text-danger" id="mExpAmount" min="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Description / Paid To</label>
              <input type="text" class="form-control form-control-sm" id="mExpDesc" placeholder="e.g. Shop monthly rent or container labor charges" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-danger btn-sm"><i class="bi bi-check2-circle"></i> Save Expense</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 4: Stock Breakage & Inventory Adjustment Form -->
<div class="modal fade" id="modalNewAdjustment" tabindex="-1" aria-labelledby="modalNewAdjustmentLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-secondary text-white">
        <h5 class="modal-title fw-bold" id="modalNewAdjustmentLabel"><i class="bi bi-slash-circle me-2"></i> Stock Breakage & Inventory Adjustment</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalAdjForm" onsubmit="handleNewAdjustmentSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Adjustment #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mAdjNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mAdjDate" required>
            </div>
            <div class="col-12">
              <div class="d-flex justify-content-between align-items-center">
                <label class="form-label small fw-bold">Product Item</label>
                <span class="badge bg-secondary mb-1" id="mAdjStockBadge">Current Stock: 0</span>
              </div>
              <select class="form-select form-select-sm" id="mAdjProduct" onchange="onModalAdjProductChange()" required></select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Adjustment Type</label>
              <select class="form-select form-select-sm" id="mAdjType" required>
                <option value="Breakage">Breakage / Damaged</option>
                <option value="Shortage">Inventory Shortage</option>
                <option value="Excess">Stock Found Excess</option>
                <option value="Return to Vendor">Return to Supplier</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Quantity</label>
              <input type="number" class="form-control form-control-sm" id="mAdjQty" min="1" value="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Reason / Details</label>
              <input type="text" class="form-control form-control-sm" id="mAdjNotes" placeholder="e.g. Broken during carton transit or showroom display" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-dark btn-sm"><i class="bi bi-check2-circle"></i> Save Stock Adjustment</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 5: Add Partner Capital Contribution Form -->
<div class="modal fade" id="modalNewCapital" tabindex="-1" aria-labelledby="modalNewCapitalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-primary text-white">
        <h5 class="modal-title fw-bold" id="modalNewCapitalLabel"><i class="bi bi-people me-2"></i> Add Partner Capital Contribution</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalCapForm" onsubmit="handleNewCapitalSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Voucher #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mCapNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mCapDate" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Partner</label>
              <select class="form-select form-select-sm" id="mCapPartner" required>
                <option value="Partner 1">Partner 1 (50%)</option>
                <option value="Partner 2">Partner 2 (50%)</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Deposit Into Account</label>
              <select class="form-select form-select-sm" id="mCapAccount">
                <option value="Main Bank Account">Main Bank Account</option>
                <option value="Cash in Hand">Cash in Hand</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Contribution Type</label>
              <select class="form-select form-select-sm" id="mCapType">
                <option value="Additional Capital">Additional Capital Investment</option>
                <option value="Working Capital Injection">Working Capital Injection</option>
                <option value="Opening Equity">Opening Equity</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Amount (PKR)</label>
              <input type="number" class="form-control form-control-sm fw-bold text-primary" id="mCapAmount" min="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Remarks</label>
              <input type="text" class="form-control form-control-sm" id="mCapRemarks" placeholder="e.g. Additional investment for new container purchase" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary btn-sm"><i class="bi bi-check2-circle"></i> Save Capital Deposit</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 6: Record Partner Drawing Form -->
<div class="modal fade" id="modalNewDrawing" tabindex="-1" aria-labelledby="modalNewDrawingLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-warning text-dark">
        <h5 class="modal-title fw-bold" id="modalNewDrawingLabel"><i class="bi bi-cash-stack me-2"></i> Record Partner Drawing / Withdrawal</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalDrwForm" onsubmit="handleNewDrawingSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Voucher #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mDrwNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mDrwDate" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Partner</label>
              <select class="form-select form-select-sm" id="mDrwPartner" required>
                <option value="Partner 1">Partner 1</option>
                <option value="Partner 2">Partner 2</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Withdraw From Account</label>
              <select class="form-select form-select-sm" id="mDrwAccount">
                <option value="Cash in Hand">Cash in Hand</option>
                <option value="Main Bank Account">Main Bank Account</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Amount Withdrawn (PKR)</label>
              <input type="number" class="form-control form-control-sm fw-bold text-danger" id="mDrwAmount" min="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Remarks / Purpose</label>
              <input type="text" class="form-control form-control-sm" id="mDrwRemarks" placeholder="e.g. Household monthly expenses" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-warning text-dark btn-sm"><i class="bi bi-check2-circle"></i> Save Partner Drawing</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 7: Customer Payment / Recovery Form -->
<div class="modal fade" id="modalCustomerReceipt" tabindex="-1" aria-labelledby="modalCustomerReceiptLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-warning text-dark">
        <h5 class="modal-title fw-bold" id="modalCustomerReceiptLabel"><i class="bi bi-cash-coin me-2"></i> Receive Customer Payment / Recovery</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalCustRcptForm" onsubmit="handleCustomerReceiptSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Receipt #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mRcptNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mRcptDate" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Customer Account</label>
              <select class="form-select form-select-sm" id="mRcptCustomer" onchange="onModalCustRcptChange()" required></select>
              <div class="small text-muted mt-1" id="mRcptCurrentBalText">Current Receivable: PKR 0</div>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Deposit Account</label>
              <select class="form-select form-select-sm" id="mRcptAccount">
                <option value="Cash in Hand">Cash in Hand</option>
                <option value="Main Bank Account">Main Bank Account</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Amount Received (PKR)</label>
              <input type="number" class="form-control form-control-sm fw-bold text-success" id="mRcptAmount" min="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Reference / Cheque #</label>
              <input type="text" class="form-control form-control-sm" id="mRcptRef" placeholder="e.g. Market recovery / Cheque # 8829" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-success btn-sm"><i class="bi bi-check2-circle"></i> Save Customer Payment</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 8: Supplier Payment Voucher Form -->
<div class="modal fade" id="modalSupplierPayment" tabindex="-1" aria-labelledby="modalSupplierPaymentLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-danger text-white">
        <h5 class="modal-title fw-bold" id="modalSupplierPaymentLabel"><i class="bi bi-truck me-2"></i> Supplier Payment Voucher</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form id="modalSuppPayForm" onsubmit="handleSupplierPaymentSubmit(event)">
        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-bold">Payment Voucher #</label>
              <input type="text" class="form-control form-control-sm bg-light" id="mPayNo" readonly>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Date</label>
              <input type="date" class="form-control form-control-sm" id="mPayDate" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Supplier Account</label>
              <select class="form-select form-select-sm" id="mPaySupplier" onchange="onModalSuppPayChange()" required></select>
              <div class="small text-muted mt-1" id="mPayCurrentBalText">Current Payable: PKR 0</div>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Paid From Account</label>
              <select class="form-select form-select-sm" id="mPayAccount">
                <option value="Main Bank Account">Main Bank Account</option>
                <option value="Cash in Hand">Cash in Hand</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold">Amount Paid (PKR)</label>
              <input type="number" class="form-control form-control-sm fw-bold text-danger" id="mPayAmount" min="1" required>
            </div>
            <div class="col-12">
              <label class="form-label small fw-bold">Payment Reference / Cheque #</label>
              <input type="text" class="form-control form-control-sm" id="mPayRef" placeholder="e.g. Bank online transfer / Cheque # 9912" required>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-danger btn-sm"><i class="bi bi-check2-circle"></i> Save Supplier Payment</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- MODAL 9: Printable Wholesale Invoice Preview -->
<div class="modal fade" id="invoiceModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title fw-bold"><i class="bi bi-receipt"></i> Wholesale Invoice Preview</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body p-4" id="printableInvoiceArea">
        <div class="d-flex justify-content-between border-bottom pb-3 mb-3">
          <div>
            <h4 class="fw-bold text-primary mb-0">ROYAL ENTERPRISES</h4>
            <div class="small text-muted">Wholesale Crockery Merchants & Importers</div>
            <div class="small text-muted">Phone: +92 300 1234567 | Address: Wholesale Crockery Market, Rawalpindi / Murree</div>
          </div>
          <div class="text-end">
            <h5 class="fw-bold text-danger" id="invNoModal">INV-0000</h5>
            <div class="small text-muted" id="invDateModal">Date: 2026-10-01</div>
          </div>
        </div>
        <div class="mb-3">
          <strong>Bill To Customer:</strong> <span id="invCustModal">Customer Name</span>
        </div>
        <table class="table table-bordered mb-3">
          <thead class="table-light small">
            <tr>
              <th>Item Description</th>
              <th class="text-center">Quantity</th>
              <th class="text-end">Wholesale Rate</th>
              <th class="text-end">Total Amount</th>
            </tr>
          </thead>
          <tbody id="invItemsModal"></tbody>
          <tfoot>
            <tr>
              <th colspan="3" class="text-end">Total Invoice Amount:</th>
              <th class="text-end fw-bold" id="invTotalModal">PKR 0</th>
            </tr>
            <tr>
              <th colspan="3" class="text-end">Cash Received:</th>
              <th class="text-end text-success fw-bold" id="invRecModal">PKR 0</th>
            </tr>
            <tr>
              <th colspan="3" class="text-end">Balance (Receivable):</th>
              <th class="text-end text-danger fw-bold" id="invBalModal">PKR 0</th>
            </tr>
          </tfoot>
        </table>
        <div class="d-flex justify-content-between mt-5 pt-4 text-center small text-muted">
          <div style="border-top: 1px solid #999; width: 150px;">Prepared By</div>
          <div style="border-top: 1px solid #999; width: 150px;">Customer Signature</div>
          <div style="border-top: 1px solid #999; width: 150px;">Partner Approval</div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary btn-sm" onclick="window.print()"><i class="bi bi-printer"></i> Print Invoice</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="app.js"></script>
</body>
</html>
'''

def generate_app_js():
    return '''// Royal Enterprises - Crockery Wholesale Accounting System
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
    return "<option value=\\"" + c.name + "\\">" + c.name + " (" + c.city + ")</option>";
  }).join("");

  const prodSel = document.getElementById("mSaleProduct");
  prodSel.innerHTML = appState.products.map(function (p) {
    return "<option value=\\"" + p.id + "\\">" + p.name + "</option>";
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
    return "<option value=\\"" + s.name + "\\">" + s.name + " (" + s.city + ")</option>";
  }).join("");

  const prodSel = document.getElementById("mPurProduct");
  prodSel.innerHTML = appState.products.map(function (p) {
    return "<option value=\\"" + p.id + "\\">" + p.name + "</option>";
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
    return "<option value=\\"" + p.id + "\\">" + p.name + " (Stock: " + p.stock + " " + p.unit + ")</option>";
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
    return "<option value=\\"" + c.name + "\\">" + c.name + " (Due: PKR " + bal.toLocaleString() + ")</option>";
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
    return "<option value=\\"" + s.name + "\\">" + s.name + " (Due: PKR " + bal.toLocaleString() + ")</option>";
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + s.id + "</span></td>" +
      "<td class=\\"fw-bold\\">" + s.customer + "</td>" +
      "<td class=\\"text-primary fw-bold\\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td class=\\"text-muted\\">PKR " + s.totalCost.toLocaleString() + "</td>" +
      "<td class=\\"text-success fw-bold\\">PKR " + s.profit.toLocaleString() + "</td>" +
      "<td><button class=\\"btn btn-outline-primary btn-sm py-0\\" onclick=\\"previewInvoice('" + s.id + "')\\"><i class=\\"bi bi-printer\\"></i> Bill</button></td>" +
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + p.id + "</span></td>" +
      "<td>" + p.date + "</td>" +
      "<td class=\\"fw-bold\\">" + p.supplier + "</td>" +
      "<td>" + p.item + "</td>" +
      "<td>" + p.qty + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td class=\\"fw-bold text-dark\\">PKR " + p.total.toLocaleString() + "</td>" +
      "<td class=\\"text-success\\">PKR " + p.paid.toLocaleString() + "</td>" +
      "<td class=\\"text-danger fw-bold\\">PKR " + p.balance.toLocaleString() + "</td>" +
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + s.id + "</span></td>" +
      "<td>" + s.date + "</td>" +
      "<td class=\\"fw-bold\\">" + s.customer + "</td>" +
      "<td>" + s.item + "</td>" +
      "<td>" + s.qty + "</td>" +
      "<td class=\\"text-primary fw-bold\\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td class=\\"text-muted\\">PKR " + s.totalCost.toLocaleString() + "</td>" +
      "<td class=\\"text-success fw-bold\\">PKR " + s.profit.toLocaleString() + "</td>" +
      "<td class=\\"text-success\\">PKR " + s.received.toLocaleString() + "</td>" +
      "<td class=\\"text-danger fw-bold\\">PKR " + s.balance.toLocaleString() + "</td>" +
      "<td><button class=\\"btn btn-outline-primary btn-sm py-0\\" onclick=\\"previewInvoice('" + s.id + "')\\"><i class=\\"bi bi-printer\\"></i> Bill</button></td>" +
      "</tr>";
  }).join("");
}

function renderCustomerSelect() {
  const sel = document.getElementById("ledgerCustomerSelect");
  if (!sel || sel.options.length > 0) return;
  sel.innerHTML = appState.customers.map(function (c) {
    return "<option value=\\"" + c.name + "\\">" + c.name + " (" + c.city + ")</option>";
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
      "<td class=\\"fw-bold text-dark\\">PKR " + s.totalSale.toLocaleString() + "</td>" +
      "<td>-</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";

    if (s.received > 0) {
      runBal -= s.received;
      html += "<tr class=\\"table-light\\">" +
        "<td>" + s.date + "</td>" +
        "<td>Cash Received on Invoice (" + s.id + ")</td>" +
        "<td>-</td>" +
        "<td class=\\"text-success fw-bold\\">PKR " + s.received.toLocaleString() + "</td>" +
        "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
        "</tr>";
    }
  });

  cPayments.forEach(function (p) {
    runBal -= p.amount;
    html += "<tr class=\\"table-success-subtle\\">" +
      "<td>" + p.date + "</td>" +
      "<td>Market Recovery: " + p.id + " (" + p.ref + ")</td>" +
      "<td>-</td>" +
      "<td class=\\"text-success fw-bold\\">PKR " + p.amount.toLocaleString() + "</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
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
    return "<option value=\\"" + s.name + "\\">" + s.name + " (" + s.city + ")</option>";
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
      "<td class=\\"fw-bold text-dark\\">PKR " + p.total.toLocaleString() + "</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
      "</tr>";

    if (p.paid > 0) {
      runBal -= p.paid;
      html += "<tr class=\\"table-light\\">" +
        "<td>" + p.date + "</td>" +
        "<td>Payment Made at Invoicing</td>" +
        "<td class=\\"text-success fw-bold\\">PKR " + p.paid.toLocaleString() + "</td>" +
        "<td>-</td>" +
        "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
        "</tr>";
    }
  });

  sPayments.forEach(function (sp) {
    runBal -= sp.amount;
    html += "<tr class=\\"table-info-subtle\\">" +
      "<td>" + sp.date + "</td>" +
      "<td>Bank Payment: " + sp.id + " (" + sp.ref + ")</td>" +
      "<td class=\\"text-success fw-bold\\">PKR " + sp.amount.toLocaleString() + "</td>" +
      "<td>-</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + runBal.toLocaleString() + "</td>" +
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + e.id + "</span></td>" +
      "<td>" + e.date + "</td>" +
      "<td><span class=\\"badge bg-secondary\\">" + e.category + "</span></td>" +
      "<td>" + e.desc + "</td>" +
      "<td><i class=\\"bi bi-credit-card text-muted me-1\\"></i>" + e.account + "</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + e.amount.toLocaleString() + "</td>" +
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
      "<td class=\\"fw-bold\\">" + p.name + "</td>" +
      "<td><span class=\\"badge bg-light text-dark border\\">" + p.category + "</span></td>" +
      "<td>" + p.unit + "</td>" +
      "<td class=\\"fw-bold " + (isLow ? "text-danger" : "text-dark") + "\\">" + p.stock + "</td>" +
      "<td>PKR " + p.costRate.toLocaleString() + "</td>" +
      "<td>PKR " + p.saleRate.toLocaleString() + "</td>" +
      "<td class=\\"fw-bold text-primary\\">PKR " + itemVal.toLocaleString() + "</td>" +
      "<td><span class=\\"badge " + (isLow ? "bg-warning text-dark" : "bg-success") + "\\">" + (isLow ? "Low Stock" : "In Stock") + "</span></td>" +
      "</tr>";
  }).join("");
}

function renderAdjustmentsTable() {
  const tbody = document.getElementById("adjustmentTableBody");
  if (!tbody) return;
  tbody.innerHTML = appState.adjustments.map(function (a) {
    return "<tr>" +
      "<td><span class=\\"badge bg-light text-dark border\\">" + a.id + "</span></td>" +
      "<td>" + a.date + "</td>" +
      "<td class=\\"fw-bold\\">" + a.product + "</td>" +
      "<td>" + a.qty + "</td>" +
      "<td><span class=\\"badge bg-danger\\">" + a.type + "</span></td>" +
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + c.id + "</span></td>" +
      "<td>" + c.date + "</td>" +
      "<td class=\\"fw-bold text-primary\\">" + c.partner + "</td>" +
      "<td>" + c.account + "</td>" +
      "<td><span class=\\"badge bg-info text-dark\\">" + c.type + "</span></td>" +
      "<td class=\\"fw-bold text-success\\">PKR " + c.amount.toLocaleString() + "</td>" +
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
      "<td><span class=\\"badge bg-light text-dark border\\">" + d.id + "</span></td>" +
      "<td>" + d.date + "</td>" +
      "<td class=\\"fw-bold text-warning-emphasis\\">" + d.partner + "</td>" +
      "<td>" + d.account + "</td>" +
      "<td class=\\"fw-bold text-danger\\">PKR " + d.amount.toLocaleString() + "</td>" +
      "<td>" + d.remarks + "</td>" +
      "</tr>";
  }).join("");
}

function renderMonthlyProfit(sales, cogs, gp, exp, np, half) {
  const tbody = document.getElementById("monthlyProfitBody");
  if (!tbody) return;
  tbody.innerHTML = "<tr class=\\"fw-bold\\">" +
    "<td>October 2026</td>" +
    "<td class=\\"text-primary\\">PKR " + sales.toLocaleString() + "</td>" +
    "<td class=\\"text-muted\\">PKR " + cogs.toLocaleString() + "</td>" +
    "<td class=\\"text-success\\">PKR " + gp.toLocaleString() + "</td>" +
    "<td class=\\"text-danger\\">PKR " + exp.toLocaleString() + "</td>" +
    "<td class=\\"text-success fs-5\\">PKR " + np.toLocaleString() + "</td>" +
    "<td class=\\"text-info\\">PKR " + half.toLocaleString() + "</td>" +
    "<td class=\\"text-info\\">PKR " + half.toLocaleString() + "</td>" +
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
      "<td class=\\"text-center\\">" + s.qty + "</td>" +
      "<td class=\\"text-end\\">PKR " + s.saleRate.toLocaleString() + "</td>" +
      "<td class=\\"text-end fw-bold\\">PKR " + s.totalSale.toLocaleString() + "</td>" +
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
'''

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(root, "index.html")
    app_path = os.path.join(root, "app.js")

    print("Writing index.html...")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(generate_index_html())

    print("Writing app.js...")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(generate_app_js())

    print("Frontend built successfully!")

if __name__ == "__main__":
    main()
