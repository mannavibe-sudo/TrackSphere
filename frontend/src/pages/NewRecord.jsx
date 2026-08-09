import { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Save, ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import StepIndicator from "../components/form/StepIndicator";
import FormField from "../components/form/FormField";
import { stepsConfig, initialFormData } from "../lib/formConfig";

export default function NewRecord() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [formData, setFormData] = useState(initialFormData);
  const [saveStatus, setSaveStatus] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const step = stepsConfig[currentStep];
  const isLastStep = currentStep === stepsConfig.length - 1;

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Auto-calculated fields — same logic the backend derives them with,
  // shown here read-only so the user sees the number before it's saved.
  const weightLossMt = useMemo(() => {
    const pi = parseFloat(formData.weight_at_pi_yard_mt);
    const itc = parseFloat(formData.weight_at_itc_yard_mt);
    if (isNaN(pi) || isNaN(itc)) return "";
    return (pi - itc).toFixed(2);
  }, [formData.weight_at_pi_yard_mt, formData.weight_at_itc_yard_mt]);

  const marginPnl = useMemo(() => {
    const received = parseFloat(formData.total_amount_received);
    const transportCost = parseFloat(formData.total_payment_to_transport);
    const materialCost = parseFloat(formData.cost_of_material);
    if (isNaN(received)) return "";
    return (received - (transportCost || 0) - (materialCost || 0)).toFixed(2);
  }, [formData.total_amount_received, formData.total_payment_to_transport, formData.cost_of_material]);

  // Simulated autosave — real version PATCHes /api/v1/records/{id} here.
  useEffect(() => {
    const hasAnyValue = Object.values(formData).some((v) => v !== "");
    if (!hasAnyValue) return;
    setSaveStatus("Saving draft...");
    const t = setTimeout(() => setSaveStatus("Draft saved"), 500);
    return () => clearTimeout(t);
  }, [formData]);

  const validateStep = () => {
    const missing = step.fields.filter((f) => f.required && !formData[f.name]);
    return missing;
  };

  const handleNext = () => {
    const missing = validateStep();
    if (missing.length > 0) {
      alert(`Please fill: ${missing.map((f) => f.label).join(", ")}`);
      return;
    }
    setCompletedSteps((prev) => new Set(prev).add(currentStep));
    if (isLastStep) {
      setSubmitted(true);
    } else {
      setCurrentStep((s) => s + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) setCurrentStep((s) => s - 1);
  };

  const handleStepClick = (i) => setCurrentStep(i);

  if (submitted) {
    return (
      <div className="flex min-h-screen bg-paper">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <TopNav />
          <main className="flex flex-1 items-center justify-center p-6">
            <div className="max-w-md rounded-lg border border-ink/10 bg-white p-8 text-center">
              <CheckCircle2 size={40} className="mx-auto text-cargo" />
              <h2 className="mt-4 font-display text-xl font-semibold text-ink">
                Record submitted
              </h2>
              <p className="mt-2 text-sm text-slate2">
                LR {formData.lr_no || "—"} has moved from Draft to Loading. You can
                still view it from Records; only a Company Admin can edit it further.
              </p>
              <button
                onClick={() => navigate("/dashboard")}
                className="mt-6 rounded-md bg-ink px-4 py-2 text-sm font-medium text-white hover:bg-ink-light"
              >
                Back to Dashboard
              </button>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <TopNav />

        <main className="flex-1 p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-ink">New Record</h1>
              <p className="text-sm text-slate2">
                Fill in each step — you can come back and edit any completed step
                until you submit.
              </p>
            </div>
            <span className="flex items-center gap-1.5 text-xs text-slate2">
              <Save size={13} />
              {saveStatus}
            </span>
          </div>

          <StepIndicator
            steps={stepsConfig}
            currentStep={currentStep}
            completedSteps={completedSteps}
            onStepClick={handleStepClick}
          />

          <div className="rounded-lg border border-ink/10 bg-white p-6">
            <h2 className="mb-5 font-display text-base font-semibold text-ink">
              {step.title}
            </h2>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {step.fields.map((f) => (
                <FormField
                  key={f.name}
                  label={f.label}
                  name={f.name}
                  type={f.type || "text"}
                  unit={f.unit}
                  required={f.required}
                  value={formData[f.name]}
                  onChange={handleChange}
                />
              ))}

              {/* Auto-calculated fields, shown read-only in context */}
              {step.key === "delivery_weight" && (
                <FormField
                  label="Weight Loss"
                  name="weight_loss_mt"
                  unit="MT"
                  value={weightLossMt}
                  onChange={() => {}}
                  readOnly
                />
              )}
              {step.key === "invoice_gst" && (
                <FormField
                  label="Margin (P&L)"
                  name="margin_pnl"
                  unit="₹"
                  value={marginPnl}
                  onChange={() => {}}
                  readOnly
                />
              )}
            </div>

            <div className="mt-8 flex items-center justify-between border-t border-ink/10 pt-5">
              <button
                type="button"
                onClick={handleBack}
                disabled={currentStep === 0}
                className="flex items-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium text-slate2 hover:bg-paper disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ArrowLeft size={15} />
                Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-1.5 rounded-md bg-ink px-5 py-2 text-sm font-medium text-white hover:bg-ink-light"
              >
                {isLastStep ? "Submit Record" : "Save & Continue"}
                {!isLastStep && <ArrowRight size={15} />}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
