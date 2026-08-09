import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Radio, Eye, EyeOff, ArrowRight } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Wired to POST /api/v1/auth/login once the backend is running locally.
    // For this preview, any non-empty input proceeds to the dashboard.
    if (!email || !password) {
      setError("Enter your email and password to continue.");
      return;
    }
    navigate("/dashboard");
  };

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-ink p-10 text-white lg:flex">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-amber text-ink">
            <Radio size={20} strokeWidth={2.5} />
          </div>
          <span className="font-display text-lg font-semibold">TrackSphere</span>
        </div>

        <div className="max-w-sm">
          <p className="font-display text-3xl font-semibold leading-tight">
            One platform.
            <br />
            Multiple companies.
            <br />
            <span className="text-amber">Complete tracking.</span>
          </p>
          <p className="mt-4 text-sm text-paper/60">
            From loading dock to payment received — every consignment, every
            company, on one rail.
          </p>
        </div>

        {/* Decorative rail echoing the dashboard's signature element */}
        <div>
          <div className="flex h-2 w-full overflow-hidden rounded-full bg-white/10">
            <div className="h-full w-[15%] bg-amber" />
            <div className="h-full w-[45%] border-l border-ink bg-amber/60" />
            <div className="h-full w-[40%] border-l border-ink bg-cargo" />
          </div>
          <div className="mt-3 flex justify-between text-[11px] uppercase tracking-wide text-paper/40">
            <span>Draft</span>
            <span>In Transit</span>
            <span>Closed</span>
          </div>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center bg-paper p-8">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-ink text-amber">
              <Radio size={18} strokeWidth={2.5} />
            </div>
            <span className="font-display text-base font-semibold text-ink">
              TrackSphere
            </span>
          </div>

          <h1 className="font-display text-2xl font-semibold text-ink">
            Sign in
          </h1>
          <p className="mt-1 text-sm text-slate2">
            Enter your company credentials to continue.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-ink">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="mt-1 w-full rounded-md border border-ink/15 bg-white px-3 py-2.5 text-sm focus:border-amber focus:outline-none"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ink">
                Password
              </label>
              <div className="relative mt-1">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-md border border-ink/15 bg-white px-3 py-2.5 pr-10 text-sm focus:border-amber focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate2"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <p role="alert" className="text-sm text-alert">
                {error}
              </p>
            )}

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-slate2">
                <input type="checkbox" className="rounded border-ink/20" />
                Keep me signed in
              </label>
              <a href="#" className="font-medium text-amber-dark hover:underline">
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              className="flex w-full items-center justify-center gap-2 rounded-md bg-ink py-2.5 text-sm font-medium text-white transition-colors hover:bg-ink-light"
            >
              Sign in
              <ArrowRight size={16} />
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-slate2">
            Trouble signing in? Contact your Company Admin or Super Admin.
          </p>
        </div>
      </div>
    </div>
  );
}
