import React, { useEffect, useRef, useState } from 'react';
import { sha256 } from 'ethers';

// --- YARDIMCI HOOK: Scroll Animasyonları İçin ---
const useIntersectionObserver = () => {
  const [isVisible, setIsVisible] = useState(false);
  const domRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
          // Eleman göründükten sonra izlemeyi bırak (sadece 1 kere çalışsın)
          observer.unobserve(domRef.current);
        }
      },
      { threshold: 0.1 } // Elemanın %10'u göründüğünde tetikle
    );
    
    if (domRef.current) observer.observe(domRef.current);
    return () => observer.disconnect();
  }, []);

  return [isVisible, domRef];
};

// --- ANİMASYON WRAPPER BİLEŞENİ ---
const FadeIn = ({ children, delay = "0ms", className = "" }) => {
  const [isVisible, domRef] = useIntersectionObserver();
  return (
    <div
      ref={domRef}
      className={`transition-all duration-1000 ease-out transform ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
      } ${className}`}
      style={{ transitionDelay: delay }}
    >
      {children}
    </div>
  );
};

// --- İKONLAR (Lucide / Heroicons tarzı SVG'ler) ---
const Icons = {
  Chaos: () => (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.121 15.536c-1.171 1.952-3.07 1.952-4.242 0-1.172-1.953-1.172-5.119 0-7.072 1.171-1.952 3.07-1.952 4.242 0M8 10.5h4m-4 3h4m9-1.5a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  Hash: () => (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  ),
  Quantum: () => (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  ),
  Blockchain: () => (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
    </svg>
  )
};

// --- ALT BİLEŞENLER ---

const StepCard = ({ number, title, description, Icon, delay }) => (
  <FadeIn delay={delay} className="h-full">
    <div className="relative p-6 rounded-2xl h-full border border-gray-800 bg-[#0A1929]/50 backdrop-blur-sm hover:border-[#00FFA3]/50 hover:bg-[#00FFA3]/5 transition-all duration-300 group">
      {/* Kart numarası arka plan fligranı */}
      <div className="absolute top-2 right-4 text-7xl font-bold text-white/5 pointer-events-none group-hover:text-[#00FFA3]/10 transition-colors">
        {number}
      </div>
      
      <div className="w-14 h-14 rounded-xl bg-gray-800/80 border border-gray-700 flex items-center justify-center text-[#00FFA3] mb-6 group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(0,255,163,0.3)] transition-all">
        <Icon />
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-3 tracking-wide">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  </FadeIn>
);

const InteractivePipelineDiagram = ({ entropyData, blockNumber, showToast }) => {
  const [chaosParams, setChaosParams] = useState({ a: 0.200, b: 0.200, c: 5.700 });
  const [extractedBits, setExtractedBits] = useState(["10110010", "00110101", "11001011"]);
  const [hexSeeds, setHexSeeds] = useState(["0x7F3A", "0x2B9C", "0xE54D"]);
  const [hashValue, setHashValue] = useState("a7ffc6f8bf1ed76651c14756a061...");
  const [kyberKeys, setKyberKeys] = useState({ pub: "0x4A3F...B2C1", cipher: "0x8D7E...F4A2" });

  // Değerleri her 1.5 saniyede bir hafifçe dalgalandıran animasyon efekti
  useEffect(() => {
    if (entropyData && entropyData.length >= 3) {
      // Asıl simülasyondaki (App.js) formül ile birebir aynı hesaplama
      setChaosParams({
        a: (0.15 + (entropyData[0] / 255) * 0.1).toFixed(3),
        b: (0.15 + (entropyData[1] / 255) * 0.1).toFixed(3),
        c: (4.0 + (entropyData[2] / 255) * 6.0).toFixed(3)
      });
      
      // Çekilen entropi verisini bit (ikilik) formatına çevir
      setExtractedBits([
        entropyData[0].toString(2).padStart(8, '0'),
        entropyData[1].toString(2).padStart(8, '0'),
        entropyData[2].toString(2).padStart(8, '0')
      ]);

      // İlk 3 byte'ı diyagramda havalı görünsün diye Hex formatına çevir
      setHexSeeds([
        "0x" + entropyData[0].toString(16).toUpperCase().padStart(2, '0') + "3A",
        "0x" + entropyData[1].toString(16).toUpperCase().padStart(2, '0') + "9C",
        "0x" + entropyData[2].toString(16).toUpperCase().padStart(2, '0') + "4D"
      ]);

      // Gelen asıl verinin (byte array) gerçek SHA-256 hash özetini hesapla
      const hash = sha256(new Uint8Array(entropyData));
      const cleanHash = hash.replace('0x', '');
      
      // "0x" kısmını atıp, tasarıma sığması için ilk 28 karakterini ve '...' alıyoruz
      setHashValue(cleanHash.substring(0, 28) + "...");

      // Aynı hash üzerinden Kyber için rastgele (pseudo) Public Key ve Ciphertext türet
      const upperHash = cleanHash.toUpperCase();
      setKyberKeys({
        pub: "0x" + upperHash.substring(0, 4) + "..." + upperHash.substring(4, 8),
        cipher: "0x" + upperHash.substring(8, 12) + "..." + upperHash.substring(12, 16)
      });
    } else {
      // Veri yokken veya yeni açıldığında sahte dalgalanma efekti (Canlılık hissi için)
      const interval = setInterval(() => {
        setChaosParams({
          a: (0.2 + (Math.random() * 0.02 - 0.01)).toFixed(3),
          b: (0.2 + (Math.random() * 0.02 - 0.01)).toFixed(3),
          c: (5.7 + (Math.random() * 0.4 - 0.2)).toFixed(3)
        });
      }, 1500);
      return () => clearInterval(interval);
    }
  }, [entropyData]);

  return (
    <FadeIn delay="200ms" className="w-full max-w-7xl mx-auto my-16">
      <div className="relative rounded-[2.5rem] border border-gray-800 bg-[#0A1929]/40 backdrop-blur-xl p-6 md:p-10 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5),0_0_0_1px_rgba(0,255,163,0.1)]">
      
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
              <span className="w-3 h-3 bg-[#00FFA3] rounded-full animate-pulse shadow-[0_0_15px_#00FFA3]"></span>
              Interactive Architecture Flow
            </h2>
            <p className="text-gray-400 mt-2 text-sm">Hybrid chaos-based entropy generation with post-quantum encryption</p>
          </div>
          <div className="flex gap-2">
            <span className="px-4 py-2 bg-[#00FFA3]/10 text-[#00FFA3] rounded-full text-xs font-bold tracking-wide border border-[#00FFA3]/30 uppercase">v2.2 Architecture</span>
            <button 
              onClick={() => {
                if (showToast) showToast("The system is currently running stably in production.");
                else alert("The system is currently running stably in production.");
              }}
              title="System Status: Stable"
              className="px-4 py-2 bg-gray-800 text-gray-300 rounded-full text-xs font-bold tracking-wide border border-gray-700 uppercase hover:bg-gray-700 hover:text-white transition-colors cursor-pointer"
            >
              Production Ready
            </button>
          </div>
        </div>

        {/* Main Pipeline Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative">
        
        {/* LAYER 1: ENTROPY GENERATION */}
        <div className="relative group">
          <div className="bg-[#050b14]/80 border border-gray-800 rounded-3xl p-6 h-full transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_-10px_rgba(0,255,163,0.15)] hover:border-[#00FFA3]/50 relative z-10">
            <div className="inline-block px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase mb-6 bg-[#00FFA3]/10 text-[#00FFA3] border border-[#00FFA3]/30">
              🔮 Generation Layer
            </div>
            
            {/* Seed Generation */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-[#00FFA3] rounded-full"></div>
                <span className="font-semibold text-white text-sm">Seed Generation</span>
              </div>
              <div className="bg-gray-900/60 p-3 rounded-xl border border-gray-800">
                <span className="text-[10px] uppercase tracking-wider text-gray-500">Initial entropy seed</span>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex-1 py-1.5 bg-[#00FFA3]/10 border border-[#00FFA3]/20 rounded-md flex items-center justify-center text-[10px] font-mono text-[#00FFA3]">{hexSeeds[0]}</div>
                  <div className="flex-1 py-1.5 bg-[#00FFA3]/10 border border-[#00FFA3]/20 rounded-md flex items-center justify-center text-[10px] font-mono text-[#00FFA3]">{hexSeeds[1]}</div>
                  <div className="flex-1 py-1.5 bg-[#00FFA3]/10 border border-[#00FFA3]/20 rounded-md flex items-center justify-center text-[10px] font-mono text-[#00FFA3]">{hexSeeds[2]}</div>
                </div>
              </div>
            </div>
            
            {/* Chaos Engine */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_8px_#a855f7]"></div>
                <span className="font-semibold text-white text-sm">Chaos Engine</span>
                <span className="text-[10px] text-gray-500 ml-auto bg-gray-800 px-2 py-0.5 rounded uppercase">Rössler</span>
              </div>
              <div className="bg-[#0A1929] border border-gray-800 rounded-xl p-3 font-mono text-xs text-gray-300">
                <div className="flex justify-between mb-1"><span className="text-gray-500">dx/dt =</span><span className="text-[#00FFA3]">-y - z</span></div>
                <div className="flex justify-between mb-1"><span className="text-gray-500">dy/dt =</span><span className="text-[#00FFA3]">x + a·y</span></div>
                <div className="flex justify-between"><span className="text-gray-500">dz/dt =</span><span className="text-[#00FFA3]">b + z(x - c)</span></div>
              </div>
              <div className="flex gap-2 mt-3">
              <span className="text-[10px] px-2 py-1 bg-gray-800/80 rounded text-[#00FFA3] border border-gray-700 font-mono transition-colors">a={chaosParams.a}</span>
              <span className="text-[10px] px-2 py-1 bg-gray-800/80 rounded text-[#00FFA3] border border-gray-700 font-mono transition-colors">b={chaosParams.b}</span>
              <span className="text-[10px] px-2 py-1 bg-gray-800/80 rounded text-[#00FFA3] border border-gray-700 font-mono transition-colors">c={chaosParams.c}</span>
              </div>
            </div>
            
            {/* Entropy Extraction */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="font-semibold text-white text-sm">Entropy Extraction</span>
              </div>
              <div className="bg-blue-900/10 p-3 rounded-xl border border-blue-500/20">
                <span className="text-[10px] uppercase tracking-wider text-gray-500">Raw chaos → Entropy bits</span>
                <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                  <span className="text-[10px] font-mono bg-[#0A1929] text-blue-400 px-2 py-1 rounded border border-gray-800">{extractedBits[0]}</span>
                  <span className="text-[10px] font-mono bg-[#0A1929] text-blue-400 px-2 py-1 rounded border border-gray-800">{extractedBits[1]}</span>
                  <span className="text-[10px] font-mono bg-[#0A1929] text-blue-400 px-2 py-1 rounded border border-gray-800">{extractedBits[2]}</span>
                </div>
              </div>
            </div>
          </div>
          {/* Flow Arrow */}
          <div className="hidden lg:flex absolute -right-6 top-1/2 transform -translate-y-1/2 z-0 text-[#00FFA3] opacity-30 text-3xl font-light">→</div>
        </div>

        {/* LAYER 2: CRYPTOGRAPHIC PROCESSING */}
        <div className="relative group">
          <div className="bg-[#050b14]/80 border border-gray-800 rounded-3xl p-6 h-full transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_-10px_rgba(59,130,246,0.15)] hover:border-blue-500/50 relative z-10">
            <div className="inline-block px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase mb-6 bg-blue-500/10 text-blue-400 border border-blue-500/30">
              🔐 Cryptographic Layer
            </div>
            
            {/* Hash Processing */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-orange-500 rounded-full shadow-[0_0_8px_#f97316]"></div>
                <span className="font-semibold text-white text-sm">Hash Processing</span>
              </div>
              <div className="bg-orange-900/10 p-4 rounded-xl border border-orange-500/20">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20">SHA-256</span>
                  <span className="text-[10px] text-gray-400 uppercase">Entropy Mixing</span>
                </div>
                <div className="mt-3 font-mono text-[10px] text-gray-500 break-all bg-[#0A1929] p-2 rounded border border-gray-800">
                  {hashValue}
                </div>
              </div>
            </div>
            
            {/* Kyber-768 Encryption */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_#ef4444]"></div>
                <span className="font-semibold text-white text-sm">Post-Quantum Sec.</span>
                <span className="text-[10px] text-gray-500 ml-auto bg-gray-800 px-2 py-0.5 rounded uppercase">ML-KEM-768</span>
              </div>
              <div className="bg-red-900/10 p-4 rounded-xl border border-red-500/20">
                <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-3">Quantum-resistant encapsulation</span>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-[#0A1929] p-2 rounded-lg border border-gray-800">
                    <span className="text-[8px] text-gray-500 uppercase">Public Key</span>
                    <div className="text-[10px] font-mono text-gray-300 truncate mt-1">{kyberKeys.pub}</div>
                  </div>
                  <div className="bg-[#0A1929] p-2 rounded-lg border border-gray-800">
                    <span className="text-[8px] text-gray-500 uppercase">Ciphertext</span>
                    <div className="text-[10px] font-mono text-gray-300 truncate mt-1">{kyberKeys.cipher}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {/* Flow Arrow */}
          <div className="hidden lg:flex absolute -right-6 top-1/2 transform -translate-y-1/2 z-0 text-blue-500 opacity-30 text-3xl font-light">→</div>
        </div>

        {/* LAYER 3: SECURITY & DISTRIBUTION */}
        <div className="relative group">
          <div className="bg-[#050b14]/80 border border-gray-800 rounded-3xl p-6 h-full transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_-10px_rgba(34,197,94,0.15)] hover:border-green-500/50 relative z-10">
            <div className="inline-block px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase mb-6 bg-green-500/10 text-green-400 border border-green-500/30">
              🔒 Distribution Layer
            </div>
            
            {/* Blockchain Output */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]"></div>
                <span className="font-semibold text-white text-sm">Blockchain Output</span>
              </div>
              <div className="bg-green-900/10 p-4 rounded-xl border border-green-500/20">
                <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-3">Secure entropy stored on-chain</span>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#0A1929] border border-gray-700 rounded-xl flex items-center justify-center text-white text-lg shadow-inner">⛓️</div>
                  <div className="flex-1">
                    <div className="h-1.5 bg-gray-800 rounded-full w-full overflow-hidden mb-1.5">
                      {/* BlockNumber gelene kadar (pending durumunda) %30 genişlik ve animasyon, gelince %100 genişlik */}
                      <div className={`h-1.5 bg-gradient-to-r from-green-500 to-[#00FFA3] rounded-full relative transition-all duration-1000 ${blockNumber ? 'w-full' : 'w-1/3'}`}>
                        {!blockNumber && <div className="absolute inset-0 bg-white/20 animate-pulse"></div>}
                      </div>
                    </div>
                    <span className={`text-[10px] font-mono ${blockNumber ? 'text-green-400' : 'text-gray-500'}`}>
                      {blockNumber 
                        ? `Block #${blockNumber.toLocaleString()} Verified` 
                        : "Waiting for Transaction..."}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 mt-4">
              <div className="bg-[#0A1929] p-3 rounded-xl border border-gray-800 text-center">
                <div className="text-2xl font-bold text-white mb-1">256<span className="text-xs text-gray-500 ml-1">bit</span></div>
                <div className="text-[9px] text-gray-500 uppercase tracking-wider">Security Level</div>
              </div>
              <div className="bg-[#0A1929] p-3 rounded-xl border border-gray-800 text-center">
                <div className="text-2xl font-bold text-[#00FFA3] mb-1">99.9<span className="text-xs text-[#00FFA3]/50 ml-1">%</span></div>
                <div className="text-[9px] text-gray-500 uppercase tracking-wider">Entropy Quality</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Pipeline Steps Indicator (Footer of Card) */}
      <div className="flex flex-wrap justify-center items-center gap-3 mt-10 pt-6 border-t border-gray-800/50">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 bg-[#00FFA3] rounded-full shadow-[0_0_8px_#00FFA3]"></div>
          <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Generation</span>
        </div>
        <span className="text-gray-700 mx-1">—</span>
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full shadow-[0_0_8px_#3b82f6]"></div>
          <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Processing</span>
        </div>
        <span className="text-gray-700 mx-1">—</span>
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]"></div>
          <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Distribution</span>
        </div>
     </div>
      </div>
    </FadeIn>
  );
};

// --- ANA SAYFA BİLEŞENİ ---

export default function EntropyPipeline({ entropyData, blockNumber, showToast }) {
  const steps = [
    {
      number: "01",
      title: "Chaotic Dynamics",
      description: "EntropyHub generates high-quality randomness using a chaotic dynamical system based on the Rossler attractor model.",
      Icon: Icons.Chaos,
      delay: "0ms"
    },
    {
      number: "02",
      title: "Entropy Extraction",
      description: "The chaotic signals are processed to extract entropy bits, which are then mixed using cryptographic hashing (SHA-256).",
      Icon: Icons.Hash,
      delay: "200ms"
    },
    {
      number: "03",
      title: "Post-Quantum Security",
      description: "To ensure long-term security against quantum computers, the system integrates post-quantum encryption using Kyber-768.",
      Icon: Icons.Quantum,
      delay: "400ms"
    },
    {
      number: "04",
      title: "Blockchain Distribution",
      description: "The final secure entropy output can be distributed through blockchain infrastructure or external systems.",
      Icon: Icons.Blockchain,
      delay: "600ms"
    }
  ];

  return (
    <div className="min-h-screen bg-[#050b14] text-slate-200 font-sans selection:bg-[#00FFA3]/30 py-20 px-4 md:px-8 relative overflow-hidden">
      
      {/* Arkaplan Ortam Işıkları (Ambient Lighting) */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#00FFA3]/5 rounded-full blur-[150px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[150px]" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        
        {/* Header Section */}
        <FadeIn>
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h4 className="text-[#00FFA3] font-mono text-sm font-bold tracking-widest uppercase mb-3">
              System Architecture
            </h4>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white mb-6 tracking-tight">
              Entropy Generation <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00FFA3] to-cyan-500">Pipeline</span>
            </h1>
            <p className="text-gray-400 text-lg md:text-xl">
              A comprehensive overview of how EntropyHub transforms mathematical chaos into cryptographically secure, quantum-resistant random numbers.
            </p>
          </div>
        </FadeIn>

        {/* Ana Diyagram Görseli */}
        <InteractivePipelineDiagram entropyData={entropyData} blockNumber={blockNumber} showToast={showToast} />

        {/* Adım Adım Açıklama Kartları */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-24">
          {steps.map((step, index) => (
            <StepCard 
              key={index}
              number={step.number}
              title={step.title}
              description={step.description}
              Icon={step.Icon}
              delay={step.delay}
            />
          ))}
        </div>

        {/* Call to Action (CTA) Bölümü */}
        <FadeIn delay="200ms">
          <div className="relative rounded-3xl p-8 md:p-12 border border-[#00FFA3]/20 bg-gradient-to-br from-[#0A1929] to-[#050b14] overflow-hidden text-center shadow-[0_0_40px_rgba(0,255,163,0.05)]">
            {/* Dekoratif Çizgiler */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#00FFA3]/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            
            <h2 className="text-3xl font-bold text-white mb-4">Ready to secure your protocols?</h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Integrate EntropyHub's post-quantum secure randomness directly into your smart contracts or backend systems with our easy-to-use APIs.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                className="px-8 py-4 bg-[#00FFA3] hover:bg-[#00e090] text-[#0A1929] font-bold rounded-xl transition-all duration-300 transform hover:-translate-y-1 shadow-[0_0_20px_rgba(0,255,163,0.3)] w-full sm:w-auto"
              >
                Explore API
              </button>
              <button 
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="px-8 py-4 bg-transparent border border-gray-600 hover:border-[#00FFA3] text-white font-bold rounded-xl transition-all duration-300 transform hover:-translate-y-1 hover:bg-[#00FFA3]/5 w-full sm:w-auto"
              >
                Read Documentation
              </button>
            </div>
          </div>
        </FadeIn>

      </div>
    </div>
  );
}
