import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/shared/Navbar";
import Footer from "@/components/shared/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AIVIS — AI 검색 노출 진단",
  description:
    "ChatGPT·Perplexity·Gemini에 추천되는 비즈니스가 되세요. AI 노출 준비도를 30초 만에 무료 진단합니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${inter.className} bg-slate-950 antialiased`}>
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
