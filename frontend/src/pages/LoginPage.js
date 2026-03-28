import React, { useState, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Eye, EyeOff, Mail, User, Lock, ArrowLeft, Upload, CheckCircle } from "lucide-react";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_secure-social-hub-2/artifacts/dki0o21d_LOGO.png";

export default function LoginPage() {
  const { login, verifyEmail, completeRegister, uploadProfileImage } = useAuth();
  const [mode, setMode] = useState("login"); // login | email | verify-sent | complete
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [verificationToken, setVerificationToken] = useState("");
  const [verificationLink, setVerificationLink] = useState("");
  const [profileImage, setProfileImage] = useState(null);
  const [profilePreview, setProfilePreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = await login(username, password);
    if (!result.success) setError(result.error);
    setSubmitting(false);
  };

  const handleVerifyEmail = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = await verifyEmail(email);
    if (result.success) {
      setVerificationToken(result.data.token);
      setVerificationLink(result.data.verification_link);
      setMode("verify-sent");
    } else {
      setError(result.error);
    }
    setSubmitting(false);
  };

  const handleVerifyClick = async () => {
    setSubmitting(true);
    setError("");
    try {
      const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
      const resp = await fetch(`${API}/auth/verify/${verificationToken}`);
      if (resp.ok) {
        setMode("complete");
      } else {
        const data = await resp.json();
        setError(data.detail || "Verification failed");
      }
    } catch {
      setError("Verification failed");
    }
    setSubmitting(false);
  };

  const handleCompleteRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = await completeRegister(verificationToken, username, password);
    if (result.success) {
      if (profileImage) {
        await uploadProfileImage(profileImage);
      }
    } else {
      setError(result.error);
    }
    setSubmitting(false);
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfileImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setProfilePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050505] p-4 relative overflow-hidden" data-testid="login-page">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-orange-900/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-red-800/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative z-10 animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <img src={LOGO_URL} alt="F1RECHAT" className="w-20 h-20 mx-auto mb-3 object-contain" data-testid="app-logo" />
          <h1 className="text-3xl font-bold text-white font-['Cairo']">F1RECHAT</h1>
          <p className="text-gray-500 text-sm mt-1 font-['Tajawal']">
            {mode === "login" && "Welcome back"}
            {mode === "email" && "Create a new account"}
            {mode === "verify-sent" && "Check your email"}
            {mode === "complete" && "Complete your profile"}
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-[#121212] border border-neutral-800 rounded-2xl p-6 shadow-2xl shadow-black/50">

          {/* LOGIN MODE */}
          {mode === "login" && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Username</label>
                <div className="relative">
                  <input
                    data-testid="login-username-input"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
                  />
                  <User className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Password</label>
                <div className="relative">
                  <input
                    data-testid="login-password-input"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
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

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 animate-fade-in" data-testid="auth-error-message">
                  {error}
                </div>
              )}

              <button
                data-testid="login-submit-button"
                type="submit"
                disabled={submitting}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all active:scale-[0.98] shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_20px_rgba(220,38,38,0.4)] flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-['Cairo']"
              >
                {submitting ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Login <ArrowLeft className="w-4 h-4" /></>
                )}
              </button>

              <div className="text-center">
                <button
                  data-testid="toggle-to-register"
                  type="button"
                  onClick={() => { setMode("email"); setError(""); }}
                  className="text-gray-400 hover:text-red-400 text-sm transition-colors font-['Tajawal']"
                >
                  Don't have an account? Create one
                </button>
              </div>
            </form>
          )}

          {/* EMAIL STEP */}
          {mode === "email" && (
            <form onSubmit={handleVerifyEmail} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Email Address</label>
                <div className="relative">
                  <input
                    data-testid="register-email-input"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
                  />
                  <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>
              </div>

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 animate-fade-in" data-testid="auth-error-message">
                  {error}
                </div>
              )}

              <button
                data-testid="verify-email-button"
                type="submit"
                disabled={submitting}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all active:scale-[0.98] shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_20px_rgba(220,38,38,0.4)] flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-['Cairo']"
              >
                {submitting ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Send Verification <Mail className="w-4 h-4" /></>
                )}
              </button>

              <div className="text-center">
                <button
                  data-testid="toggle-to-login"
                  type="button"
                  onClick={() => { setMode("login"); setError(""); }}
                  className="text-gray-400 hover:text-red-400 text-sm transition-colors font-['Tajawal']"
                >
                  Already have an account? Login
                </button>
              </div>
            </form>
          )}

          {/* VERIFY-SENT STEP */}
          {mode === "verify-sent" && (
            <div className="space-y-4 text-center">
              <div className="bg-green-900/20 border border-green-800/30 rounded-lg p-4">
                <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-green-400 text-sm font-['Tajawal']">
                  A verification email has been sent to <strong>{email}</strong>
                </p>
                <p className="text-gray-500 text-xs mt-2 font-['Tajawal']">
                  Click the button below to verify your email
                </p>
              </div>

              <button
                data-testid="verify-confirm-button"
                onClick={handleVerifyClick}
                disabled={submitting}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg transition-all active:scale-[0.98] flex justify-center items-center gap-2 disabled:opacity-50 font-['Cairo']"
              >
                {submitting ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Verify My Email <CheckCircle className="w-4 h-4" /></>
                )}
              </button>

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 animate-fade-in" data-testid="auth-error-message">
                  {error}
                </div>
              )}

              <button
                type="button"
                onClick={() => { setMode("email"); setError(""); }}
                className="text-gray-400 hover:text-red-400 text-sm transition-colors font-['Tajawal']"
              >
                Use a different email
              </button>
            </div>
          )}

          {/* COMPLETE REGISTRATION STEP */}
          {mode === "complete" && (
            <form onSubmit={handleCompleteRegister} className="space-y-4">
              <div className="text-center mb-2">
                <p className="text-green-400 text-sm font-['Tajawal']">Email verified! Complete your profile</p>
              </div>

              {/* Profile Image Upload */}
              <div className="flex flex-col items-center">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="w-24 h-24 rounded-full bg-[#0A0A0A] border-2 border-dashed border-neutral-700 hover:border-red-600 flex items-center justify-center cursor-pointer transition-colors overflow-hidden group"
                  data-testid="profile-image-upload"
                >
                  {profilePreview ? (
                    <img src={profilePreview} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    <Upload className="w-8 h-8 text-gray-600 group-hover:text-red-400 transition-colors" />
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                  data-testid="profile-image-file-input"
                />
                <p className="text-xs text-gray-500 mt-2 font-['Tajawal']">Upload profile picture (optional)</p>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Username</label>
                <div className="relative">
                  <input
                    data-testid="register-username-input"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Choose a username"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
                    minLength={3}
                  />
                  <User className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Password</label>
                <div className="relative">
                  <input
                    data-testid="register-password-input"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a password"
                    className="w-full bg-[#0A0A0A] border border-neutral-800 rounded-lg px-4 py-3 pr-11 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                    required
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                  <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>
              </div>

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 animate-fade-in" data-testid="auth-error-message">
                  {error}
                </div>
              )}

              <button
                data-testid="complete-register-button"
                type="submit"
                disabled={submitting}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all active:scale-[0.98] shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_20px_rgba(220,38,38,0.4)] flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-['Cairo']"
              >
                {submitting ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Create Account <ArrowLeft className="w-4 h-4" /></>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
