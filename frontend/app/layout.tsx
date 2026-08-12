import "./globals.css";

export const metadata = {
  title: "Kavya — Love Chat",
  description: "Voice + text chat UI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
