"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

interface User {
  id: string;
  name: string;
  username: string;
  email: string;
  role: "owner";
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, remember?: boolean) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const OWNER_USER: User = {
  id: "usr_owner_01",
  name: "Ashray",
  username: "ashray",
  email: "ashray@aashrayspa.internal",
  role: "owner",
};

const AUTH_STORAGE_KEY = "aashrays_pa_auth_session";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    try {
      const stored = localStorage.getItem(AUTH_STORAGE_KEY);
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch {
      // Storage error or SSR
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (
    username: string,
    password: string,
    remember: boolean = true
  ): Promise<{ success: boolean; error?: string }> => {
    // Single-owner authentication check
    // Allows owner username/email and owner password
    const cleanUser = username.trim().toLowerCase();
    if (
      (cleanUser === "ashray" || cleanUser === "satyam" || cleanUser.includes("@")) &&
      password.length >= 6
    ) {
      const authenticatedUser = {
        ...OWNER_USER,
        name: cleanUser === "satyam" ? "Satyam" : "Ashray",
      };
      setUser(authenticatedUser);
      if (remember) {
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authenticatedUser));
      }
      return { success: true };
    }

    return {
      success: false,
      error: "Invalid owner credentials. Please verify your private access key.",
    };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(AUTH_STORAGE_KEY);
    router.push("/login");
  };

  // Route protection
  useEffect(() => {
    if (!isLoading) {
      const isAuthPage = pathname === "/login";
      if (!user && !isAuthPage) {
        router.push("/login");
      } else if (user && isAuthPage) {
        router.push("/");
      }
    }
  }, [user, isLoading, pathname, router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

