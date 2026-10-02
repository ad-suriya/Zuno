import type { Metadata } from "next";
import { Noto_Sans, Noto_Sans_Mono, Noto_Sans_Tamil } from "next/font/google";
import "./globals.css";

// wdth axis powers the condensed display style (see design-system/MASTER.md §3).
const notoSans = Noto_Sans({ variable: "--font-noto-sans", subsets: ["latin"], axes: ["wdth"] });
const notoSansTamil = Noto_Sans_Tamil({ variable: "--font-noto-sans-tamil", subsets: ["tamil"], axes: ["wdth"] });
const notoSansMono = Noto_Sans_Mono({ variable: "--font-noto-sans-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Zuno",
  description: "Check a financial offer before you put money at risk.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${notoSans.variable} ${notoSansTamil.variable} ${notoSansMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
