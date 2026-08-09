// Mock data — shaped exactly like the real /api/v1/dashboard response will be.
// Swap this file's exports for real react-query hooks once the backend
// Dashboard API (Module 9) is ready; component code does not need to change.

export const currentUser = {
  name: "Ayush Verma",
  role: "company_admin",
  company: "Manna Logistics Pvt. Ltd.",
};

export const summaryStats = {
  totalRecords: 1284,
  activeTrips: 47,
  delivered: 968,
  pendingDeliveries: 61,
  pendingPayments: 22,
  totalRevenue: 18450000,
  totalTransportCost: 12980000,
  profitLoss: 5470000,
  margin: 29.6,
  weightLossMt: 14.8,
};

export const lifecycleStages = [
  { key: "draft", label: "Draft", count: 12 },
  { key: "loading", label: "Loading", count: 18 },
  { key: "dispatched", label: "Dispatched", count: 25 },
  { key: "in_transit", label: "In Transit", count: 47 },
  { key: "delivered", label: "Delivered", count: 61 },
  { key: "invoice_raised", label: "Invoice Raised", count: 34 },
  { key: "payment_received", label: "Payment Received", count: 22 },
  { key: "closed", label: "Closed", count: 968 },
];

export const revenueTrend = [
  { month: "Feb", revenue: 2100000, cost: 1480000 },
  { month: "Mar", revenue: 2400000, cost: 1690000 },
  { month: "Apr", revenue: 2250000, cost: 1590000 },
  { month: "May", revenue: 2680000, cost: 1870000 },
  { month: "Jun", revenue: 3120000, cost: 2190000 },
  { month: "Jul", revenue: 2980000, cost: 2080000 },
  { month: "Aug", revenue: 2920000, cost: 2020000 },
];

export const recentRecords = [
  {
    record_id: "1",
    lr_no: "LR-88214",
    truck_number: "UK07 GT 4521",
    transporter_name: "Bhandari Roadways",
    loading_location: "Dehradun Plant",
    status: "in_transit",
    invoice_amount_raised: 184500,
    date_of_dispatch: "2026-08-06",
  },
  {
    record_id: "2",
    lr_no: "LR-88213",
    truck_number: "UP15 BT 9078",
    transporter_name: "Singh Carriers",
    loading_location: "Haridwar Yard",
    status: "delivered",
    invoice_amount_raised: 221300,
    date_of_dispatch: "2026-08-06",
  },
  {
    record_id: "3",
    lr_no: "LR-88212",
    truck_number: "HR55 AK 3312",
    transporter_name: "Bhandari Roadways",
    loading_location: "Dehradun Plant",
    status: "payment_received",
    invoice_amount_raised: 156800,
    date_of_dispatch: "2026-08-05",
  },
  {
    record_id: "4",
    lr_no: "LR-88211",
    truck_number: "UK07 GT 1187",
    transporter_name: "Verma Transport Co.",
    loading_location: "Rishikesh Depot",
    status: "invoice_raised",
    invoice_amount_raised: 198200,
    date_of_dispatch: "2026-08-05",
  },
  {
    record_id: "5",
    lr_no: "LR-88210",
    truck_number: "UK07 GT 5540",
    transporter_name: "Singh Carriers",
    loading_location: "Dehradun Plant",
    status: "dispatched",
    invoice_amount_raised: 143900,
    date_of_dispatch: "2026-08-04",
  },
];

export const statusLabel = {
  draft: "Draft",
  loading: "Loading",
  dispatched: "Dispatched",
  in_transit: "In Transit",
  delivered: "Delivered",
  invoice_raised: "Invoice Raised",
  payment_received: "Payment Received",
  closed: "Closed",
};

export const formatINR = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);
