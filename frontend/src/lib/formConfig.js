// Field config mirrors the Excel exactly — same 4 groups, same 31 fields,
// same order. See docs/excel-field-mapping.md for the original headers.

export const stepsConfig = [
  {
    key: "loading_dispatch",
    title: "Loading & Dispatch",
    fields: [
      { name: "loading_location", label: "Loading Location", required: true },
      { name: "truck_number", label: "Truck Number", required: true },
      { name: "driver_mobile", label: "Driver Mobile", type: "tel" },
      { name: "weight_at_pi_yard_mt", label: "Weight at PI Yard", type: "number", unit: "MT" },
      { name: "eway_bill_no", label: "E-Way Bill No." },
      { name: "date_of_dispatch", label: "Date of Dispatch", type: "date", required: true },
      { name: "lr_no", label: "Lorry Receipt (LR) No.", required: true },
      { name: "delivery_chalan", label: "Delivery Chalan" },
      { name: "cost_of_material", label: "Cost of Material", type: "number", unit: "₹" },
    ],
  },
  {
    key: "transportation",
    title: "Transportation",
    fields: [
      { name: "transporter_name", label: "Transporter Name", required: true },
      { name: "transporter_mobile", label: "Transporter Mobile", type: "tel" },
      { name: "capacity_of_truck_mt", label: "Capacity of Truck", type: "number", unit: "MT" },
      { name: "length_of_truck_ft", label: "Length of Truck", type: "number", unit: "ft" },
      {
        name: "rate_fixed_for_transportation",
        label: "Rate Fixed for Transportation",
        type: "number",
        unit: "₹",
      },
      { name: "advance_paid", label: "Advance Paid", type: "number", unit: "₹" },
      { name: "advance_payment_date", label: "Advance Payment Date", type: "date" },
      { name: "advance_paid_to", label: "Advance Paid To" },
      { name: "final_payment", label: "Final Payment", type: "number", unit: "₹" },
      {
        name: "total_payment_to_transport",
        label: "Total Payment to Transport",
        type: "number",
        unit: "₹",
      },
    ],
  },
  {
    key: "delivery_weight",
    title: "Delivery & Weight at ITC",
    fields: [
      { name: "truck_entry_date", label: "Truck Entry Date", type: "date" },
      {
        name: "truck_exit_date",
        label: "Truck Exit Date (Tare weight & unloading)",
        type: "date",
      },
      { name: "weight_at_itc_yard_mt", label: "Weight at ITC Yard", type: "number", unit: "MT" },
      { name: "wc_number", label: "WC Number" },
      // weight_loss_mt is auto-calculated below, not entered directly
    ],
  },
  {
    key: "invoice_gst",
    title: "Invoice & GST",
    fields: [
      { name: "invoice_number", label: "Invoice Number", required: true },
      { name: "invoice_amount_raised", label: "Invoice Amount Raised", type: "number", unit: "₹" },
      { name: "amount_raised_date", label: "Amount Raised Date (ITC)", type: "date" },
      { name: "gst_amount", label: "GST Amount", type: "number", unit: "₹" },
      { name: "payment_received_date", label: "Payment Received Date (ITC)", type: "date" },
      {
        name: "total_amount_received",
        label: "Total Amount Received (ITC)",
        type: "number",
        unit: "₹",
      },
      // margin_pnl is auto-calculated below, not entered directly
    ],
  },
];

export const initialFormData = stepsConfig
  .flatMap((s) => s.fields)
  .reduce((acc, f) => ({ ...acc, [f.name]: "" }), {});
