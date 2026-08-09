export default function FormField({
  label,
  name,
  value,
  onChange,
  type = "text",
  unit,
  required = false,
  disabled = false,
  readOnly = false,
}) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-ink">
        {label}
        {required && <span className="text-alert"> *</span>}
        {unit && <span className="text-slate2 font-normal"> ({unit})</span>}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value ?? ""}
        onChange={(e) => onChange(name, e.target.value)}
        required={required}
        disabled={disabled}
        readOnly={readOnly}
        className={`mt-1 w-full rounded-md border px-3 py-2 text-sm focus:outline-none ${
          readOnly
            ? "border-ink/10 bg-paper font-mono tabular text-slate2"
            : "border-ink/15 bg-white focus:border-amber"
        } ${type === "number" || type === "tel" ? "font-mono tabular" : ""}`}
      />
    </div>
  );
}
