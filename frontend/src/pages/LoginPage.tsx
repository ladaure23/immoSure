import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Eye, EyeOff, Lock, Mail } from "lucide-react";
import { login } from "../services/auth";
import { useAuthStore } from "../store/authStore";

const schema = z.object({
  email: z.string().email("Adresse email invalide"),
  password: z.string().min(6, "Minimum 6 caractères"),
});
type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.login);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
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

  return (
    <div className="min-h-screen flex flex-col md:flex-row font-sans">

      {/* ── Panneau gauche ── */}
      <div className="relative md:w-1/2 bg-[#1a3c6e] flex flex-col items-center justify-center px-10 py-16 overflow-hidden">

        {/* Motif géométrique de fond */}
        <div className="absolute inset-0 opacity-[0.06]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              45deg,
              #fff 0px, #fff 1px,
              transparent 1px, transparent 40px
            ), repeating-linear-gradient(
              -45deg,
              #fff 0px, #fff 1px,
              transparent 1px, transparent 40px
            )`,
          }}
        />

        {/* Cercles décoratifs */}
        <div className="absolute -top-20 -right-20 w-72 h-72 rounded-full bg-white/5" />
        <div className="absolute -bottom-32 -left-16 w-96 h-96 rounded-full bg-[#2ea043]/10" />

        <div className="relative z-10 flex flex-col items-center text-center animate-fade-in">
          <img
            src="/logo immosure.jpg"
            alt="ImmoSure"
            className="w-52 mb-8 rounded-2xl shadow-2xl"
          />
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

          {/* Carte formulaire */}
          <div className="bg-white rounded-2xl shadow-xl px-8 py-10">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-[#1a3c6e] mb-1">
                Connexion
              </h2>
              <p className="text-gray-500 text-sm">
                Accédez à votre espace de gestion
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">

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
                      ${errors.email ? "border-red-400 bg-red-50" : "border-gray-200 bg-gray-50 hover:border-gray-300"}`}
                    {...register("email")}
                  />
                </div>
                {errors.email && (
                  <p className="mt-1.5 text-xs text-red-500">{errors.email.message}</p>
                )}
              </div>

              {/* Mot de passe */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    className={`w-full pl-10 pr-11 py-2.5 rounded-lg border text-sm transition-colors outline-none
                      focus:ring-2 focus:ring-[#1a3c6e]/20 focus:border-[#1a3c6e]
                      ${errors.password ? "border-red-400 bg-red-50" : "border-gray-200 bg-gray-50 hover:border-gray-300"}`}
                    {...register("password")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1.5 text-xs text-red-500">{errors.password.message}</p>
                )}
              </div>

              {/* Bouton */}
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

          <p className="text-center text-xs text-gray-400 mt-6">
            ImmoSure · Cotonou, Bénin · L'immobilier en toute confiance
          </p>
        </div>
      </div>
    </div>
  );
}
