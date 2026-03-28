import React, { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Ghost, Eye, EyeOff, Mail, User, Lock, ArrowLeft } from "lucide-react";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    let result;
    if (isRegister) {
      result = await register(username, email, password);
    } else {
      result = await login(email, password);
    }

    if (!result.success) {
      setError(result.error);
    }
    setSubmitting(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050505] p-4 relative overflow-hidden" data-testid="login-page">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-900/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-red-800/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative z-10 animate-fade-in">
        {/* Logo / Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-red-600/10 border border-red-600/20 mb-4">
            <Ghost className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-3xl font-bold text-white font-['Cairo']">
            الفراغ
          </h1>
          <p className="text-gray-500 text-sm mt-1 font-['Tajawal']">
            {isRegister ? "إنشاء حساب جديد" : "مرحباً بعودتك"}
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-[#121212] border border-neutral-800 rounded-2xl p-6 shadow-2xl shadow-black/50">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username (register only) */}
            {isRegister && (
              <div className="relative animate-fade-in">
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">اسم المستخدم</label>
                <div className="relative">
                  <input
                    data-testid="register-username-input"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="أدخل اسم المستخدم"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
                    minLength={3}
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">البريد الإلكتروني</label>
              <div className="relative">
                <input
                  data-testid="login-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="أدخل بريدك الإلكتروني"
                  className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                  required
                />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">كلمة المرور</label>
              <div className="relative">
                <input
                  data-testid="login-password-input"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="أدخل كلمة المرور"
                  className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  data-testid="toggle-password-visibility"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
                <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 animate-fade-in" data-testid="auth-error-message">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              data-testid="login-submit-button"
              type="submit"
              disabled={submitting}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all active:scale-[0.98] shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_20px_rgba(220,38,38,0.4)] flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-['Cairo']"
            >
              {submitting ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isRegister ? "إنشاء حساب" : "تسجيل الدخول"}
                  <ArrowLeft className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Register/Login */}
          <div className="mt-4 text-center">
            <button
              data-testid="toggle-auth-mode"
              onClick={() => { setIsRegister(!isRegister); setError(""); }}
              className="text-gray-400 hover:text-red-400 text-sm transition-colors font-['Tajawal']"
            >
              {isRegister ? "لديك حساب بالفعل؟ تسجيل الدخول" : "ليس لديك حساب؟ إنشاء حساب جديد"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
