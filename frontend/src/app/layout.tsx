import type { Metadata } from "next";
import { Noto_Sans, Noto_Sans_Tamil } from "next/font/google";
import "./globals.css";

const notoSans = Noto_Sans({ variable: "--font-noto-sans", subsets: ["latin"] });
const notoSansTamil = Noto_Sans_Tamil({ variable: "--font-noto-sans-tamil", subsets: ["tamil"] });

export const metadata: Metadata = {
  title: "Zuno",
  description: "Check a financial offer before you put money at risk.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${notoSans.variable} ${notoSansTamil.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
