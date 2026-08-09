import { Check } from "lucide-react";

export default function StepIndicator({ steps, currentStep, completedSteps, onStepClick }) {
  return (
    <div className="mb-6 rounded-lg border border-ink/10 bg-white p-5">
      <div className="flex items-center">
        {steps.map((step, i) => {
          const isCompleted = completedSteps.has(i);
          const isCurrent = i === currentStep;
          const isClickable = isCompleted || isCurrent;

          return (
            <div key={step.key} className="flex flex-1 items-center last:flex-none">
              <button
                type="button"
                disabled={!isClickable}
                onClick={() => isClickable && onStepClick(i)}
                className="flex flex-col items-center gap-2 disabled:cursor-not-allowed"
              >
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition-colors ${
                    isCompleted
                      ? "bg-cargo text-white"
                      : isCurrent
                      ? "bg-amber text-ink"
                      : "bg-paper text-slate2 border border-ink/15"
                  }`}
                >
                  {isCompleted ? <Check size={16} strokeWidth={3} /> : i + 1}
                </div>
                <span
                  className={`text-xs font-medium ${
                    isCurrent ? "text-ink" : isCompleted ? "text-cargo" : "text-slate2"
                  }`}
                >
                  {step.title}
                </span>
              </button>
              {i < steps.length - 1 && (
                <div
                  className={`mx-2 h-0.5 flex-1 rounded ${
                    completedSteps.has(i) ? "bg-cargo" : "bg-ink/10"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
