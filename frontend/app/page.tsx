import Hero from "@/components/landing/Hero";
import ProblemSection from "@/components/landing/ProblemSection";
import IndustryTabs from "@/components/landing/IndustryTabs";
import HowItWorks from "@/components/landing/HowItWorks";
import MonitorTeaser from "@/components/landing/MonitorTeaser";
import CtaBanner from "@/components/landing/CtaBanner";

export default function Home() {
  return (
    <>
      <Hero />
      <ProblemSection />
      <IndustryTabs />
      <HowItWorks />
      <MonitorTeaser />
      <CtaBanner />
    </>
  );
}
