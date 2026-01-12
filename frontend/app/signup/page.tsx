"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { signup, setAuthToken } from "@/lib/api-client";
import type { SignupRequest } from "@/lib/types";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<SignupRequest>({
    email: "",
    password: "",
    password_confirm: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState("");
  const [passwordStrength, setPasswordStrength] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  });

  // Check password strength as user types
  useEffect(() => {
    const password = formData.password;
    const strength = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password),
    };
    setPasswordStrength(strength);
  }, [formData.password]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }

    // Clear general error when user starts typing
    if (generalError) {
      setGeneralError("");
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else {
      // Check strength requirements
      if (formData.password.length < 8) {
        newErrors.password = "Password must be at least 8 characters";
      } else if (!/[A-Z]/.test(formData.password)) {
        newErrors.password = "Password must contain uppercase letter";
      } else if (!/[a-z]/.test(formData.password)) {
        newErrors.password = "Password must contain lowercase letter";
      } else if (!/\d/.test(formData.password)) {
        newErrors.password = "Password must contain number";
      } else if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(formData.password)) {
        newErrors.password = "Password must contain special character";
      }
    }

    // Password confirm validation
    if (!formData.password_confirm) {
      newErrors.password_confirm = "Please confirm password";
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setGeneralError("");

    try {
      const response = await signup(formData);

      // Store the JWT token
      setAuthToken(response.token);

      // Redirect to dashboard
      router.push("/dashboard");
      router.refresh(); // Refresh to update the UI
    } catch (error: any) {
      console.error("Signup error:", error);
      if (error.getUserMessage) {
        // Handle API error
        const message = error.getUserMessage();
        if (message.includes("already registered")) {
          setErrors({ email: "Email already registered" });
        } else {
          setGeneralError(message);
        }
      } else {
        setGeneralError("An error occurred during signup. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const isPasswordStrong = Object.values(passwordStrength).every(Boolean);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
          <p className="text-gray-600">Sign up to get started with your tasks</p>
        </div>

        {generalError && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {generalError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.email ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="you@example.com"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.password ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Create a strong password"
            />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
          </div>

          <div>
            <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.password_confirm ? "border-red-500" : "border-gray-300"
              }`}
              placeholder="Confirm your password"
            />
            {errors.password_confirm && (
              <p className="mt-1 text-sm text-red-600">{errors.password_confirm}</p>
            )}
          </div>

          {/* Password strength indicator */}
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Password must contain:</h3>
            <ul className="text-xs space-y-1">
              <li className={`flex items-center ${passwordStrength.length ? 'text-green-600' : 'text-gray-500'}`}>
                <span className="mr-2">{passwordStrength.length ? '✓' : '○'}</span>
                At least 8 characters
              </li>
              <li className={`flex items-center ${passwordStrength.uppercase ? 'text-green-600' : 'text-gray-500'}`}>
                <span className="mr-2">{passwordStrength.uppercase ? '✓' : '○'}</span>
                Uppercase letter (A-Z)
              </li>
              <li className={`flex items-center ${passwordStrength.lowercase ? 'text-green-600' : 'text-gray-500'}`}>
                <span className="mr-2">{passwordStrength.lowercase ? '✓' : '○'}</span>
                Lowercase letter (a-z)
              </li>
              <li className={`flex items-center ${passwordStrength.number ? 'text-green-600' : 'text-gray-500'}`}>
                <span className="mr-2">{passwordStrength.number ? '✓' : '○'}</span>
                Number (0-9)
              </li>
              <li className={`flex items-center ${passwordStrength.special ? 'text-green-600' : 'text-gray-500'}`}>
                <span className="mr-2">{passwordStrength.special ? '✓' : '○'}</span>
                Special character (!@#$%^&*)
              </li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={loading || !isPasswordStrong}
            className={`w-full py-3 px-4 rounded-lg font-medium text-white shadow-md transition-colors ${
              loading || !isPasswordStrong
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            }`}
          >
            {loading ? "Creating Account..." : "Sign Up"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            Already have an account?{" "}
            <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}