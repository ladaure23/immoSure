import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Eye, EyeOff, Lock, Mail, ArrowLeft, CheckCircle2 } from "lucide-react";
import { login } from "../services/auth";
import { useAuthStore } from "../store/authStore";

const loginSchema = z.object({
  email: z.string().email("Adresse email invalide"),
  password: z.string().min(6, "Minimum 6 caractères"),
});
type LoginData = z.infer<typeof loginSchema>;

const forgotSchema = z.object({
  email: z.string().email("Adresse email invalide"),
});
type ForgotData = z.infer<typeof forgotSchema>;

type View = "login" | "forgot" | "forgot-sent";

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.login);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<View>("login");

  const loginForm = useForm<LoginData>({ resolver: zodResolver(loginSchema) });
  const forgotForm = useForm<ForgotData>({ resolver: zodResolver(forgotSchema) });

  const onLogin = async (data: LoginData) => {
    setLoading(true);
    try {
      const res = await login(data);
      setAuth(res.access_token);
      toast.success("Connexion réussie");
      navigate("/dashboard");
    } catch {
      toast.error("Identifiants incorrects");
    } finally {
      setLoading(false);
    }
  };

  const onForgot = async (data: ForgotData) => {
    setLoading(true);
    try {
      await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: data.email }),
      });
    } finally {
      setLoading(false);
      setView("forgot-sent");
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row font-sans">

      {/* ── Panneau gauche ── */}
      <div className="relative md:w-1/2 bg-[#1a3c6e] flex flex-col items-center justify-center px-10 py-16 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.06]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              45deg,#fff 0px,#fff 1px,transparent 1px,transparent 40px
            ),repeating-linear-gradient(
              -45deg,#fff 0px,#fff 1px,transparent 1px,transparent 40px
            )`,
          }}
        />
        <div className="absolute -top-20 -right-20 w-72 h-72 rounded-full bg-white/5" />
        <div className="absolute -bottom-32 -left-16 w-96 h-96 rounded-full bg-[#2ea043]/10" />

        <div className="relative z-10 flex flex-col items-center text-center animate-fade-in">
          <img src="/logo immosure.jpg" alt="ImmoSure" className="w-52 mb-8 rounded-2xl shadow-2xl" />
          <h1 className="text-3xl font-bold text-white tracking-tight mb-3">
            Bienvenue sur ImmoSure
          </h1>
          <p className="text-blue-200 text-base max-w-xs leading-relaxed">
            La plateforme de gestion locative automatisée pour le Bénin.
          </p>
          <div className="mt-10 flex gap-6 text-white/60 text-sm">
            <div className="flex flex-col items-center gap-1">
              <span className="text-2xl font-bold text-[#2ea043]">89%</span>
              <span>Propriétaire</span>
            </div>
            <div className="w-px bg-white/20" />
            <div className="flex flex-col items-center gap-1">
              <span className="text-2xl font-bold text-white">100%</span>
              <span>Automatisé</span>
            </div>
            <div className="w-px bg-white/20" />
            <div className="flex flex-col items-center gap-1">
              <span className="text-2xl font-bold text-[#2ea043]">MTN</span>
              <span>Mobile Money</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Panneau droit ── */}
      <div className="md:w-1/2 bg-[#f4f5f7] flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-md animate-slide-up">

          {/* ── Vue : Login ── */}
          {view === "login" && (
            <div className="bg-white rounded-2xl shadow-xl px-8 py-10">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-[#1a3c6e] mb-1">Connexion</h2>
                <p className="text-gray-500 text-sm">Accédez à votre espace de gestion</p>
              </div>

              {/* Bouton Google */}
              <button
                type="button"
                onClick={() => toast("Connexion Google bientôt disponible", { icon: "🔜" })}
                className="w-full flex items-center justify-center gap-3 px-4 py-2.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 shadow-sm mb-5"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.64 9.205c0-.639-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                  <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
                  <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
                  <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
                </svg>
                Continuer avec Google
              </button>

              {/* Séparateur */}
              <div className="relative mb-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-3 bg-white text-gray-400">ou</span>
                </div>
              </div>

              <form onSubmit={loginForm.handleSubmit(onLogin)} noValidate className="space-y-5">
                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Adresse email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="email"
                      autoComplete="email"
                      placeholder="vous@exemple.com"
                      className={`w-full pl-10 pr-4 py-2.5 rounded-lg border text-sm transition-colors outline-none
                        focus:ring-2 focus:ring-[#1a3c6e]/20 focus:border-[#1a3c6e]
                        ${loginForm.formState.errors.email ? "border-red-400 bg-red-50" : "border-gray-200 bg-gray-50 hover:border-gray-300"}`}
                      {...loginForm.register("email")}
                    />
                  </div>
                  {loginForm.formState.errors.email && (
                    <p className="mt-1.5 text-xs text-red-500">{loginForm.formState.errors.email.message}</p>
                  )}
                </div>

                {/* Mot de passe */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-sm font-medium text-gray-700">
                      Mot de passe
                    </label>
                    <button
                      type="button"
                      onClick={() => setView("forgot")}
                      className="text-xs text-[#1a3c6e] hover:text-[#2ea043] transition-colors font-medium"
                    >
                      Mot de passe oublié ?
                    </button>
                  </div>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      placeholder="••••••••"
                      className={`w-full pl-10 pr-11 py-2.5 rounded-lg border text-sm transition-colors outline-none
                        focus:ring-2 focus:ring-[#1a3c6e]/20 focus:border-[#1a3c6e]
                        ${loginForm.formState.errors.password ? "border-red-400 bg-red-50" : "border-gray-200 bg-gray-50 hover:border-gray-300"}`}
                      {...loginForm.register("password")}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((v) => !v)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {loginForm.formState.errors.password && (
                    <p className="mt-1.5 text-xs text-red-500">{loginForm.formState.errors.password.message}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-lg font-semibold text-sm text-white transition-all
                    bg-[#2ea043] hover:bg-[#268a38] active:scale-[0.98]
                    disabled:opacity-60 disabled:cursor-not-allowed
                    shadow-md shadow-[#2ea043]/25 mt-2"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                      </svg>
                      Connexion…
                    </span>
                  ) : (
                    "Se connecter"
                  )}
                </button>
              </form>
            </div>
          )}

          {/* ── Vue : Mot de passe oublié ── */}
          {view === "forgot" && (
            <div className="bg-white rounded-2xl shadow-xl px-8 py-10">
              <button
                type="button"
                onClick={() => { setView("login"); forgotForm.reset(); }}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-[#1a3c6e] transition-colors mb-6"
              >
                <ArrowLeft className="w-4 h-4" />
                Retour à la connexion
              </button>

              <div className="mb-8">
                <div className="w-12 h-12 rounded-xl bg-[#1a3c6e]/10 flex items-center justify-center mb-4">
                  <Mail className="w-6 h-6 text-[#1a3c6e]" />
                </div>
                <h2 className="text-2xl font-bold text-[#1a3c6e] mb-1">Mot de passe oublié</h2>
                <p className="text-gray-500 text-sm leading-relaxed">
                  Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
                </p>
              </div>

              <form onSubmit={forgotForm.handleSubmit(onForgot)} noValidate className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Adresse email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="email"
                      autoComplete="email"
                      placeholder="vous@exemple.com"
                      className={`w-full pl-10 pr-4 py-2.5 rounded-lg border text-sm transition-colors outline-none
                        focus:ring-2 focus:ring-[#1a3c6e]/20 focus:border-[#1a3c6e]
                        ${forgotForm.formState.errors.email ? "border-red-400 bg-red-50" : "border-gray-200 bg-gray-50 hover:border-gray-300"}`}
                      {...forgotForm.register("email")}
                    />
                  </div>
                  {forgotForm.formState.errors.email && (
                    <p className="mt-1.5 text-xs text-red-500">{forgotForm.formState.errors.email.message}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-lg font-semibold text-sm text-white transition-all
                    bg-[#1a3c6e] hover:bg-[#132d54] active:scale-[0.98]
                    disabled:opacity-60 disabled:cursor-not-allowed
                    shadow-md mt-2"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                      </svg>
                      Envoi…
                    </span>
                  ) : (
                    "Envoyer le lien"
                  )}
                </button>
              </form>
            </div>
          )}

          {/* ── Vue : Email envoyé ── */}
          {view === "forgot-sent" && (
            <div className="bg-white rounded-2xl shadow-xl px-8 py-10 text-center">
              <div className="flex justify-center mb-5">
                <div className="w-16 h-16 rounded-full bg-[#2ea043]/10 flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8 text-[#2ea043]" />
                </div>
              </div>
              <h2 className="text-xl font-bold text-[#1a3c6e] mb-2">Email envoyé !</h2>
              <p className="text-gray-500 text-sm leading-relaxed mb-8">
                Si cette adresse est associée à un compte, vous recevrez un lien de réinitialisation dans quelques minutes. Pensez à vérifier vos spams.
              </p>
              <button
                type="button"
                onClick={() => { setView("login"); forgotForm.reset(); }}
                className="w-full py-3 rounded-lg font-semibold text-sm text-white transition-all
                  bg-[#1a3c6e] hover:bg-[#132d54] active:scale-[0.98] shadow-md"
              >
                Retour à la connexion
              </button>
            </div>
          )}

          <p className="text-center text-xs text-gray-400 mt-6">
            ImmoSure · Cotonou, Bénin · L'immobilier en toute confiance
          </p>
        </div>
      </div>
    </div>
  );
}
