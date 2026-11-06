"use client";

import React, { useEffect, useState } from "react";
import { Header } from "./header";
import { Sidebar } from "./sidebar";
import { MobileNav } from "./mobile-nav";
import { SearchDialog } from "../search/search-dialog";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [searchOpen, setSearchOpen] = useState(false);

  // Global keyboard shortcut for ⌘K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen flex w-full bg-[#F8F9FA] dark:bg-[#0B0D13] text-gray-900 dark:text-gray-100">
      {/* Desktop Collapsible Glass Sidebar */}
      <Sidebar />

      {/* Main Body */}
      <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0">
        <Header onSearchClick={() => setSearchOpen(true)} />
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>

      {/* Mobile Floating Bottom Bar */}
      <MobileNav />

      {/* Global Cmd+K Search Modal */}
      <SearchDialog open={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
}

