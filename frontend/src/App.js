import React, { useState, useEffect } from 'react';
import { BrowserProvider, Contract } from 'ethers';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';
import EntropyService from './service'; 
import './App.css';
import EntropyPipeline from './EntropyPipeline';

// İkon Bileşenleri
const BoltIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 mr-2" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const CubeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 mr-2" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

const SpinnerIcon = () => (
  <svg className="animate-spin -ml-1 mr-3 h-5 w-5" width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

const Activity = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const Cpu = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
    <rect x="9" y="9" width="6" height="6"></rect>
    <line x1="9" y1="1" x2="9" y2="4"></line>
    <line x1="15" y1="1" x2="15" y2="4"></line>
    <line x1="9" y1="20" x2="9" y2="23"></line>
    <line x1="15" y1="20" x2="15" y2="23"></line>
    <line x1="20" y1="9" x2="23" y2="9"></line>
    <line x1="20" y1="14" x2="23" y2="14"></line>
    <line x1="1" y1="9" x2="4" y2="9"></line>
    <line x1="1" y1="14" x2="4" y2="14"></line>
  </svg>
);

const Wifi = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M5 12.55a11 11 0 0 1 14.08 0"></path>
    <path d="M1.42 9a16 16 0 0 1 21.16 0"></path>
    <path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path>
    <line x1="12" y1="20" x2="12.01" y2="20"></line>
  </svg>
);

const SettingsIcon = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const GithubIcon = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
);

const ChartIcon = ({ size = 24, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  </svg>
);

// 3D Rössler Çekicisi Bileşeni
function RosslerGraph({ animate, entropyData, isDarkMode }) {
  const lineRef = React.useRef();
  const pointsRef = React.useRef([]);
  const stateRef = React.useRef({ x: 0.1, y: 0.1, z: 0.1 });
  const [lineColor, setLineColor] = React.useState(isDarkMode ? '#00FFA3' : '#0A1929'); 

  const paramsRef = React.useRef({ a: 0.2, b: 0.2, c: 5.7 });
  const dt = 0.03;

  React.useEffect(() => {
    if (entropyData && entropyData.length >= 3) {
      paramsRef.current.a = 0.15 + (entropyData[0] / 255) * 0.1;
      paramsRef.current.b = 0.15 + (entropyData[1] / 255) * 0.1;
      paramsRef.current.c = 4.0 + (entropyData[2] / 255) * 6.0;

      let newColor;
      if (isDarkMode) {
        newColor = `rgb(${entropyData[0]}, ${Math.min(255, entropyData[1] + 100)}, ${entropyData[2]})`;
      } else {
        newColor = `rgb(${Math.floor(entropyData[0] * 0.6)}, ${Math.floor(entropyData[1] * 0.4)}, ${Math.floor(entropyData[2] * 0.6)})`;
      }
      setLineColor(newColor);

      pointsRef.current = [];
      stateRef.current = { x: 0.1, y: 0.1, z: 0.1 };
    } else {
      setLineColor(isDarkMode ? '#00FFA3' : '#0A1929');
    }
  }, [entropyData, isDarkMode]);

  useFrame(() => {
    if (!lineRef.current) return;
    
    const iterations = animate ? 20 : 5;
    let { x, y, z } = stateRef.current;
    const { a, b, c } = paramsRef.current;

    for (let i = 0; i < iterations; i++) {
      const dx = (-y - z) * dt;
      const dy = (x + a * y) * dt;
      const dz = (b + z * (x - c)) * dt;

      x += dx;
      y += dy;
      z += dz;

      pointsRef.current.push(x, y, z);
      
      if (pointsRef.current.length > 9000) {
        pointsRef.current.splice(0, 3);
      }
    }
    stateRef.current = { x, y, z };

    const positions = new Float32Array(pointsRef.current);
    lineRef.current.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    lineRef.current.geometry.attributes.position.needsUpdate = true;
    
    lineRef.current.rotation.z += 0.002;
  });

  return (
    <line ref={lineRef}>
      <bufferGeometry />
      <lineBasicMaterial color={lineColor} linewidth={2} transparent opacity={0.8} blending={THREE.AdditiveBlending} />
    </line>
  );
}

// --- TÜM ÇIKTILAR MODALI BİLEŞENİ ---
const AllOutputsModal = ({ isOpen, onClose, entropyData, settings, isDarkMode, accentColor }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in-up">
      <div className={`relative w-full max-w-2xl p-6 rounded-3xl border shadow-2xl flex flex-col max-h-[80vh] ${isDarkMode ? 'bg-[#0A1929] border-[#00FFA3]/30 text-white' : 'bg-white border-gray-200 text-gray-800'}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <CubeIcon />
            All Generated Outputs
          </h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div className="overflow-y-auto pr-2 space-y-2 flex-1">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {entropyData.map((val, idx) => (
              <div key={idx} className={`p-3 rounded-xl border text-center ${isDarkMode ? 'bg-black/20 border-white/5' : 'bg-gray-50 border-gray-200'} hover:border-[#00FFA3]/50 transition-colors`}>
                <span className="block text-[10px] text-gray-500 mb-1 uppercase tracking-wider">Byte {idx + 1}</span>
                <span className={`font-mono font-bold responsive-byte-text ${accentColor}`}>
                  {settings.format === 'hex' ? val.toString(16).toUpperCase().padStart(2, '0') :
                   settings.format === 'bin' ? val.toString(2).padStart(8, '0') :
                   val}
                </span>
              </div>
            ))}
          </div>
        </div>
        <button onClick={onClose} className={`w-full mt-6 py-3 rounded-xl font-bold transition-colors ${isDarkMode ? 'bg-gray-800 hover:bg-gray-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'}`}>
          Close
        </button>
      </div>
    </div>
  );
};

// --- GEÇMİŞ ÇIKTILAR (HISTORY) MODALI BİLEŞENİ ---
const HistoryModal = ({ isOpen, onClose, history, settings, isDarkMode, accentColor }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in-up">
      <div className={`relative w-full max-w-3xl p-6 rounded-3xl border shadow-2xl flex flex-col max-h-[85vh] ${isDarkMode ? 'bg-[#0A1929] border-[#00FFA3]/30 text-white' : 'bg-white border-gray-200 text-gray-800'}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <ChartIcon />
            Generation History
          </h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div className="overflow-y-auto pr-2 space-y-4 flex-1">
          {history.map((session) => (
            <div key={session.id} className={`p-4 rounded-2xl border ${isDarkMode ? 'bg-black/20 border-white/10' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex justify-between items-center mb-3 border-b border-gray-500/30 pb-2">
                <span className={`text-sm font-bold ${accentColor}`}>Generation #{session.id}</span>
                <span className="text-xs text-gray-500 font-mono">{session.timestamp}</span>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {session.data.map((val, idx) => (
                  <div key={idx} className={`p-2 rounded-lg border text-center ${isDarkMode ? 'bg-black/40 border-white/5' : 'bg-white border-gray-200'}`}>
                    <span className="block text-[10px] text-gray-500 mb-0.5">B{idx + 1}</span>
                    <span className={`font-mono font-bold responsive-byte-text ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      {settings.format === 'hex' ? val.toString(16).toUpperCase().padStart(2, '0') :
                       settings.format === 'bin' ? val.toString(2).padStart(8, '0') :
                       val}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <button onClick={onClose} className={`w-full mt-6 py-3 rounded-xl font-bold transition-colors ${isDarkMode ? 'bg-gray-800 hover:bg-gray-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'}`}>
          Close
        </button>
      </div>
    </div>
  );
};

// --- SİSTEM DURUMU MODALI BİLEŞENİ ---
const StatusModal = ({ isOpen, onClose, systemStatus, isDarkMode, lastHealthCheck, errorLogCount }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in-up">
      <div className={`relative w-full max-w-md p-6 rounded-3xl border shadow-2xl ${isDarkMode ? 'bg-[#0A1929] border-[#00FFA3]/30 text-white' : 'bg-white border-gray-200 text-gray-800'}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Activity size={24} className={isDarkMode ? "text-[#00FFA3]" : "text-blue-500"} />
            System Status
          </h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div> 
        <div className="space-y-4">
          <div className={`flex justify-between items-center p-3 rounded-xl ${isDarkMode ? 'bg-black/20 border border-white/5' : 'bg-gray-50 border border-gray-100'}`}>
            <span className={isDarkMode ? "text-gray-400" : "text-gray-500"}>API Health</span>
            <span className={`font-bold font-mono px-2 py-1 rounded-md text-xs ${systemStatus.status === 'healthy' ? 'bg-[#00FFA3]/10 text-[#00FFA3]' : 'bg-red-500/10 text-red-500'}`}>
              {systemStatus.status === 'healthy' ? 'OPERATIONAL' : 'DEGRADED'}
            </span>
          </div>
          <div className={`flex justify-between items-center p-3 rounded-xl ${isDarkMode ? 'bg-black/20 border border-white/5' : 'bg-gray-50 border border-gray-100'}`}>
            <span className={isDarkMode ? "text-gray-400" : "text-gray-500"}>Chaos Engine</span>
            <span className={`font-mono px-2 py-1 rounded-md text-xs ${isDarkMode ? 'text-white bg-gray-800' : 'text-gray-800 bg-gray-200'}`}>{systemStatus.chaos_system || '-'}</span>
          </div>
          <div className={`flex justify-between items-center p-3 rounded-xl ${isDarkMode ? 'bg-black/20 border border-white/5' : 'bg-gray-50 border border-gray-100'}`}>
            <span className={isDarkMode ? "text-gray-400" : "text-gray-500"}>Network</span>
            <span className="font-mono text-blue-400 bg-blue-900/20 px-2 py-1 rounded-md text-xs">Testnet</span>
          </div>
          <div className={`flex justify-between items-center p-3 rounded-xl ${isDarkMode ? 'bg-black/20 border border-white/5' : 'bg-gray-50 border border-gray-100'}`}>
            <span className={isDarkMode ? "text-gray-400" : "text-gray-500"}>Last Sync</span>
            <span className={`font-mono px-2 py-1 rounded-md text-xs ${isDarkMode ? 'text-white bg-gray-800' : 'text-gray-800 bg-gray-200'}`}>{lastHealthCheck || 'Waiting...'}</span>
          </div>
          <div className={`flex justify-between items-center p-3 rounded-xl ${isDarkMode ? 'bg-black/20 border border-white/5' : 'bg-gray-50 border border-gray-100'}`}>
            <span className={isDarkMode ? "text-gray-400" : "text-gray-500"}>Error Count</span>
            <span className={`font-bold font-mono px-2 py-1 rounded-md text-xs ${errorLogCount === 0 ? 'bg-[#00FFA3]/10 text-[#00FFA3]' : 'bg-red-500/10 text-red-500'}`}>{errorLogCount}</span>
          </div>
        </div>
        <button onClick={onClose} className={`w-full mt-6 py-3 rounded-xl font-bold transition-colors ${isDarkMode ? 'bg-gray-800 hover:bg-gray-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'}`}>
          Close
        </button>
      </div>
    </div>
  );
};

const Toast = ({ notification, onClose }) => {
  if (!notification) return null;
  return (
    <div className={`fixed top-24 right-8 z-50 px-6 py-4 rounded-xl shadow-2xl backdrop-blur-md border animate-fade-in-up flex items-center gap-4 transition-all duration-300
      ${notification.type === 'error' 
        ? 'bg-red-900/90 border-red-500/50 text-red-100 shadow-red-900/20' 
        : 'bg-[#0A1929]/90 border-[#00FFA3]/50 text-[#00FFA3] shadow-[#00FFA3]/20'}`}>
      <div className={`p-2 rounded-full ${notification.type === 'error' ? 'bg-red-500/20' : 'bg-[#00FFA3]/20'}`}>
        {notification.type === 'error' ? <BoltIcon /> : <CubeIcon />}
      </div>
      <span className="font-medium tracking-wide">{notification.message}</span>
    </div>
  );
};

function App() {
  const isDarkMode = true;
  const [walletAddress, setWalletAddress] = useState(null);
  const [entropyData, setEntropyData] = useState([]);
  const [entropyHistory, setEntropyHistory] = useState([]);
  const [systemStatus, setSystemStatus] = useState({ status: 'Unknown', chaos_system: '-' });
  const [txHash, setTxHash] = useState(null);
  const [blockNumber, setBlockNumber] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  const [stats, setStats] = useState({ totalBytes: 0, generationCount: 0 });
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({ source: 'os_entropy', format: 'dec', byteCount: 18 });
  const [lastHealthCheck, setLastHealthCheck] = useState(null);
  const [errorLogCount, setErrorLogCount] = useState(0);
  const [rotationSpeed, setRotationSpeed] = useState(0.5);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showAllOutputs, setShowAllOutputs] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const showToast = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const updateStats = (byteCount) => {
    setStats(prev => ({
      totalBytes: prev.totalBytes + byteCount,
      generationCount: prev.generationCount + 1,
    }));
  };

  useEffect(() => {
    if (window.ethereum) {
      const handleAccountsChanged = (accounts) => {
        setWalletAddress(accounts.length > 0 ? accounts[0] : null);
      };
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      return () => window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
    }
  }, []);

  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setWalletAddress(accounts[0]);
        showToast('Wallet connected successfully.');
      } catch (error) {
        console.error("Cüzdan bağlantı hatası:", error);
      }
    } else {
      showToast("Please install MetaMask!", 'error');
    }
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === 'Space' && !loading && !showSettings && walletAddress) {
        e.preventDefault();
        handleGenerateEntropy();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, showSettings, walletAddress]); 

  useEffect(() => {
    const handleScroll = () => {
      const newSpeed = 0.5 + (window.scrollY * 0.005);
      setRotationSpeed(newSpeed);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await EntropyService.getHealth();
        setSystemStatus(healthData);
        setLastHealthCheck(new Date().toLocaleTimeString());
      } catch (error) {
        setSystemStatus({ status: 'error', chaos_system: '-' });
        setErrorLogCount(prev => prev + 1);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerateEntropy = async () => {
    setLoading(true);
    try {
      const result = await EntropyService.generateEntropy(settings.byteCount);

      console.log('Gelen veri:', result);
      
      let newData = [];
      if (result && result.values) {
        newData = result.values;
        updateStats(settings.byteCount);
        showToast(`${result.bytes} bytes of entropy generated`, 'success');
      } else if (Array.isArray(result)) {
        newData = result;
        updateStats(result.length);
        showToast(`${result.length} bytes of entropy generated`, 'success');
      } else {
        console.warn('Unexpected format:', result);
        showToast('Unexpected data format', 'error');
      }
      
      if (newData.length > 0) {
        setEntropyData(newData);
        setEntropyHistory(prev => [
          { id: prev.length + 1, data: newData, timestamp: new Date().toLocaleTimeString() },
          ...prev
        ]);
      }
      
    } catch (error) {
      console.error('Data generation error:', error);
      showToast(`Error: ${error.message}`, 'error');
      setErrorLogCount(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToBlockchain = async () => {
    if (!walletAddress) return showToast("Please connect your wallet first.", 'error');
    if (entropyData.length === 0) return showToast("No data found to save.", 'error');

    try {
      setLoading(true);
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      const contractAddress = "0x0000000000000000000000000000000000000000"; 
      const contractABI = [
        "function recordEntropy(uint8[] memory values) public"
      ];

      const contract = new Contract(contractAddress, contractABI, signer);
      
      const tx = await contract.recordEntropy(entropyData);
      setTxHash(tx.hash);
      setBlockNumber(null);
      
      const receipt = await tx.wait();
      if (receipt && receipt.blockNumber) {
        setBlockNumber(receipt.blockNumber);
      }
      showToast("Data successfully saved to blockchain!");
    } catch (error) {
      console.error("Blockchain kayıt hatası:", error);
      showToast("Transaction failed: " + (error.reason || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const getSaveButtonText = () => {
    if (loading) return "Processing...";
    if (!walletAddress) return "Connect Wallet First";
    if (entropyData.length === 0) return "Generate Data First";
    return "Save to Blockchain";
  };

  const themeContainerClass = isDarkMode
    ? "bg-[#050b14] text-gray-100"
    : "bg-[#f8fafc] text-[#1e293b]";

  const glassCardClass = isDarkMode
    ? "bg-[#0A1929]/60 border-white/10 shadow-[0_0_15px_rgba(0,0,0,0.3)]"
    : "bg-[#ffffff] border-[#e2e8f0] shadow-xl";

  const textColor = isDarkMode ? "text-white" : "text-[#1e293b]";
  const subTextColor = isDarkMode ? "text-gray-400" : "text-slate-500";
  const accentColor = isDarkMode ? "text-[#00FFA3]" : "text-[#0A1929]";
  const accentBorder = isDarkMode ? "border-[#00FFA3]" : "border-[#0A1929]";

  return (
    <div className={`min-h-screen ${themeContainerClass} font-sans selection:bg-[#00FFA3]/30 overflow-x-hidden relative transition-colors duration-500 flex flex-col`}>
      {/* Arkaplan Efektleri */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#00FFA3]/5 rounded-full blur-[150px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[150px]" />
      </div>

      {/* Navbar */}
      <nav className={`relative z-50 flex justify-between items-center px-8 py-5 border-b ${isDarkMode ? 'border-white/5 bg-[#050b14]/80' : 'border-[#e2e8f0] bg-[#ffffff]/80'} backdrop-blur-xl sticky top-0`}>
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 bg-[#00FFA3] rounded-full animate-pulse shadow-[0_0_10px_#00FFA3]"></div>
            <div className="absolute inset-0 w-3 h-3 bg-[#00FFA3] rounded-full animate-ping opacity-20"></div>
          </div>
          <h1 className={`text-xl md:text-2xl font-bold tracking-wider cursor-default font-mono ${textColor}`}>
            ENTROPY<span className={`drop-shadow-[0_0_5px_rgba(0,255,163,0.5)] ${accentColor}`}>HUB</span>
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setShowSettings(!showSettings)} 
            className={`p-2.5 rounded-xl transition-all duration-300 ${showSettings ? 'bg-[#00FFA3]/20 text-[#00FFA3]' : 'hover:bg-white/10'}`}
          >
            <SettingsIcon />
          </button>

          <a 
            href="https://github.com/Ahmetoyann/EntropyHub_A" 
            target="_blank" 
            rel="noopener noreferrer"
            className="p-2.5 rounded-xl transition-all duration-300 hover:bg-white/10 hover:text-[#00FFA3] text-gray-300"
            title="View Source on GitHub"
          >
            <GithubIcon />
          </a>
          
          <button
            onClick={connectWallet}
            className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 border backdrop-blur-sm shadow-lg transform hover:-translate-y-0.5 ${
              walletAddress
                ? `${isDarkMode ? 'bg-[#0A1929] text-[#00FFA3]' : 'bg-[#ffffff] text-[#0A1929]'} ${accentBorder} hover:shadow-[#00FFA3]/20`
                : 'bg-gradient-to-r from-[#00FFA3] to-cyan-500 hover:from-[#00E090] hover:to-cyan-400 border-transparent text-[#0A1929] hover:shadow-[0_0_20px_rgba(0,255,163,0.4)]'
            }`}
          >
            {walletAddress ? (
              <span className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full animate-pulse ${isDarkMode ? 'bg-[#00FFA3]' : 'bg-[#0A1929]'}`}></div>
                {walletAddress.substring(0, 6)}...{walletAddress.substring(38)}
              </span>
            ) : (
              'Connect Wallet'
            )}
          </button>
        </div>
      </nav>

      <Toast notification={notification} onClose={() => setNotification(null)} />
      <StatusModal isOpen={showStatusModal} onClose={() => setShowStatusModal(false)} systemStatus={systemStatus} isDarkMode={isDarkMode} lastHealthCheck={lastHealthCheck} errorLogCount={errorLogCount} />
      <AllOutputsModal isOpen={showAllOutputs} onClose={() => setShowAllOutputs(false)} entropyData={entropyData} settings={settings} isDarkMode={isDarkMode} accentColor={accentColor} />
      <HistoryModal isOpen={showHistoryModal} onClose={() => setShowHistoryModal(false)} history={entropyHistory} settings={settings} isDarkMode={isDarkMode} accentColor={accentColor} />

      {systemStatus.status === 'error' && (
        <div className="bg-red-500/10 border-b border-red-500/30 text-red-400 px-4 py-2.5 text-center text-sm font-medium flex items-center justify-center gap-3 backdrop-blur-md z-40 relative">
          <SpinnerIcon /> API Bağlantısı Bekleniyor (Servise ulaşılamıyor, arka planda yeniden deneniyor)...
        </div>
      )}

      {/* Main Layout */}
      <main className="relative z-10 container mx-auto p-4 lg:p-6 flex flex-col lg:flex-row gap-6 flex-grow">
        
        {/* Sidebar: Kontrol Paneli */}
        <aside className="w-full lg:w-80 flex-shrink-0 space-y-6">
          
          {/* Ayarlar Paneli */}
          {showSettings && (
            <div className={`animate-fade-in-down p-4 rounded-3xl mb-6 border ${isDarkMode ? 'bg-[#0A1929] border-[#00FFA3]/30' : 'bg-[#ffffff] border-[#e2e8f0]'}`}>
              <h3 className={`text-sm font-bold mb-3 ${accentColor} uppercase tracking-wider`}>Settings</h3>
              <div className="space-y-3">
                <div>
                  <label className={`block text-xs mb-1 ${subTextColor}`}>Entropy Source</label>
                  <select className={`w-full p-2 rounded-lg text-sm outline-none border ${isDarkMode ? 'bg-[#050b14] border-gray-700 text-gray-300' : 'bg-[#f8fafc] border-[#e2e8f0] text-[#1e293b]'}`} 
                          value={settings.source} onChange={(e) => setSettings({...settings, source: e.target.value})}>
                    <option value="os_entropy">System Noise (OS)</option>
                    <option value="atmospheric">Atmospheric Sensor</option>
                    <option value="quantum">Quantum RNG (Simulated)</option>
                  </select>
                </div>
                <div>
                  <label className={`block text-xs mb-1 mt-2 ${subTextColor}`}>Byte Count</label>
                  <input 
                    type="number" min="1" max="1024"
                    className={`w-full p-2 rounded-lg text-sm outline-none border ${isDarkMode ? 'bg-[#050b14] border-gray-700 text-gray-300' : 'bg-[#f8fafc] border-[#e2e8f0] text-[#1e293b]'}`}
                    value={settings.byteCount} 
                    onChange={(e) => setSettings({...settings, byteCount: parseInt(e.target.value) || 1})}
                  />
                </div>
                <div className="mt-2">
                  <label className={`block text-xs mb-1 ${subTextColor}`}>Output Format</label>
                  <div className="flex gap-2">
                    {['hex', 'dec', 'bin'].map(fmt => (
                      <button key={fmt} onClick={() => setSettings({...settings, format: fmt})}
                        className={`flex-1 py-1.5 rounded text-xs font-bold transition-all ${settings.format === fmt ? 'bg-[#00FFA3] text-[#0A1929]' : (isDarkMode ? 'bg-gray-700/50 text-gray-400' : 'bg-gray-200 text-gray-500')}`}>
                        {fmt.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Kontrol Kartı */}
          <div className={`glass-card ${glassCardClass} backdrop-blur-xl p-6 rounded-3xl shadow-2xl relative overflow-hidden transition-colors duration-500`}>
            <h2 className={`text-lg font-bold mb-6 ${textColor} flex items-center gap-2`}>
              <span className={`w-1 h-5 rounded-full ${isDarkMode ? 'bg-[#00FFA3] shadow-[0_0_10px_#00FFA3]' : 'bg-[#0A1929]'}`}></span>
              Control Panel
            </h2>
            
            <div className="space-y-4">
              <button 
                onClick={handleGenerateEntropy}
                disabled={loading}
                className={`w-full py-4 px-4 rounded-2xl font-bold shadow-lg transition-all duration-300 transform hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-2
                          bg-[#00FFA3] hover:bg-[#00E090] text-[#0A1929] hover:shadow-[0_0_20px_rgba(0,255,163,0.3)] 
                          disabled:bg-[#666666] disabled:text-gray-400 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none`}
              >
                {loading ? <><SpinnerIcon /> Processing...</> : <><BoltIcon /> Generate Data</>}
              </button>
              
              <div className="text-center text-[10px] text-gray-500 font-mono mt-[-10px] mb-2 opacity-70">
                (Press Space for quick generation)
              </div>

              {!walletAddress && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 px-3 py-2 rounded-xl text-xs font-bold text-center mb-2 animate-pulse">
                  ⚠️ Connect Wallet First
                </div>
              )}

              <button 
                onClick={handleSaveToBlockchain}
                disabled={loading || !walletAddress || entropyData.length === 0}
                className="w-full py-4 px-4 rounded-2xl font-bold shadow-lg transition-all duration-300 transform hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-2
                          bg-transparent border border-gray-700 hover:border-[#00FFA3]/50 text-current
                          disabled:border-gray-800 disabled:text-[#666666] disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading && getSaveButtonText() === "Processing..." ? <SpinnerIcon /> : <CubeIcon />}
                {getSaveButtonText()}
              </button>
            </div>

            {txHash && (
              <div className="mt-6 p-4 bg-[#00FFA3]/5 rounded-2xl border border-[#00FFA3]/20 text-xs break-all animate-fade-in-up shadow-inner">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-[#00FFA3] rounded-full animate-pulse"></div>
                  <span className="text-[#00FFA3] font-bold uppercase tracking-wider">Transaction Successful</span>
                </div>
                <span className="text-gray-400 font-mono opacity-80">{txHash}</span>
              </div>
            )}
          </div>
          
          {/* Sistem Durumu Kartları */}
          <div className="grid grid-cols-3 gap-2">
            <div className={`flex flex-col items-center justify-center p-2 ${isDarkMode ? 'bg-[#0A1929]/50 border-gray-800' : 'bg-[#ffffff] border-[#e2e8f0]'} rounded-2xl border hover:border-[#00FFA3]/30 transition-all duration-300 hover:-translate-y-1`}>
              <div className="flex items-center gap-2 mb-2">
                <div className="relative">
                   <div className={`w-2.5 h-2.5 rounded-full ${systemStatus.status === 'healthy' ? 'bg-[#00FFA3] shadow-[0_0_8px_#00FFA3]' : 'bg-red-500'}`}></div>
                   {systemStatus.status === 'healthy' && <div className="absolute inset-0 w-2.5 h-2.5 bg-[#00FFA3] rounded-full animate-ping opacity-75"></div>}
                </div>
                <Activity size={18} className={accentColor} />
              </div>
              <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded-full ${systemStatus.status === 'healthy' ? 'text-[#00FFA3] bg-[#00FFA3]/10' : 'text-red-400 bg-red-500/10'}`}>
                {systemStatus.status === 'healthy' ? 'ACTIVE' : 'INACTIVE'}
              </span>
              <span className={`text-xs mt-1 font-medium ${subTextColor}`}>System</span>
            </div>

            <div className={`flex flex-col items-center justify-center p-2 ${isDarkMode ? 'bg-[#0A1929]/50 border-gray-800' : 'bg-[#ffffff] border-[#e2e8f0]'} rounded-2xl border hover:border-purple-500/30 transition-all duration-300 hover:-translate-y-1`}>
              <div className="mb-2">
                 <Cpu size={20} className="text-purple-400" />
              </div>
              <span className={`text-[10px] font-bold font-mono ${isDarkMode ? 'text-gray-300 bg-gray-800' : 'text-gray-600 bg-gray-100'} px-2 py-0.5 rounded-full`}>
                {systemStatus.chaos_system !== '-' ? systemStatus.chaos_system : 'Rössler'}
              </span>
              <span className={`text-xs mt-1 font-medium ${subTextColor}`}>Algo</span>
            </div>

            <div className={`flex flex-col items-center justify-center p-2 ${isDarkMode ? 'bg-[#0A1929]/50 border-gray-800' : 'bg-[#ffffff] border-[#e2e8f0]'} rounded-2xl border hover:border-blue-500/30 transition-all duration-300 hover:-translate-y-1`}>
              <div className="mb-2">
                 <Wifi size={20} className="text-blue-400" />
              </div>
              <span className="text-[10px] font-bold font-mono text-blue-300 bg-blue-500/10 px-2 py-0.5 rounded-full">
                Testnet
              </span>
              <span className={`text-xs mt-1 font-medium ${subTextColor}`}>Network</span>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
          
          {/* 3D Simülasyon Alanı */}
          <div className="w-full flex flex-col gap-6">
            <div className={`${glassCardClass} backdrop-blur-xl rounded-3xl min-h-[400px] lg:min-h-[500px] relative flex flex-col shadow-2xl overflow-hidden group transition-colors duration-500`}>
              <div className="absolute top-6 left-6 z-10 flex justify-between items-start w-[calc(100%-3rem)] pointer-events-none">
                <div className={`backdrop-blur-md px-5 py-2.5 rounded-xl border shadow-lg ${isDarkMode ? 'bg-[#0A1929]/80 border-white/10' : 'bg-[#ffffff]/80 border-[#e2e8f0]'}`}>
                  <h3 className={`text-sm font-bold uppercase tracking-wide ${textColor}`}>3D Chaos Simulation</h3>
                </div>
                <span className={`text-[10px] font-mono ${accentColor} ${isDarkMode ? 'bg-black/20' : 'bg-white/50'} px-3 py-1.5 rounded-full border ${accentBorder} shadow-[0_0_15px_rgba(0,255,163,0.15)] backdrop-blur-sm`}>
                  Rössler Attractor
                </span>
              </div>
              
              <div className="absolute inset-0">
                <Canvas camera={{ position: [0, -40, 20], fov: 60 }} className={isDarkMode ? '' : 'bg-[#f1f5f9]'}>
                  {isDarkMode && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
                  <ambientLight intensity={isDarkMode ? 0.5 : 1} />
                  <RosslerGraph animate={loading} entropyData={entropyData} isDarkMode={isDarkMode} />
                  <OrbitControls makeDefault autoRotate autoRotateSpeed={rotationSpeed} enableZoom={true} />
                </Canvas>
              </div>
            </div>
          </div>

          {/* ===== YENİ: İstatistikler ve Çıktı YAN YANA ===== */}
          <div className="stats-output-row">
            
            {/* İstatistikler Kartı */}
            <div className={`glass-card ${glassCardClass} backdrop-blur-xl rounded-2xl p-5 border ${isDarkMode ? 'border-white/10' : 'border-[#e2e8f0]'} flex flex-col`}>
              <h3 className={`text-sm font-bold mb-4 flex items-center gap-2 ${textColor}`}>
                <span className={`w-1.5 h-6 rounded-full ${isDarkMode ? 'bg-[#00FFA3] shadow-[0_0_10px_#00FFA3]' : 'bg-[#0A1929]'}`}></span>
                Statistics
              </h3>
              
              {/* stats-inner-grid ile 2 sütunlu iç grid */}
              <div className="stats-inner-grid flex-1">
                <div className={`${isDarkMode ? 'bg-black/20' : 'bg-[#f8fafc]'} p-4 rounded-xl border ${isDarkMode ? 'border-white/5' : 'border-[#e2e8f0]'} text-center`}>
                  <span className={`block text-xs ${subTextColor} mb-1 uppercase tracking-wider`}>Total Output</span>
                  <span className={`text-2xl font-mono font-bold ${textColor}`}>{stats.totalBytes} <span className="text-xs font-normal text-gray-500">B</span></span>
                </div>
                <div className={`${isDarkMode ? 'bg-black/20' : 'bg-[#f8fafc]'} p-4 rounded-xl border ${isDarkMode ? 'border-white/5' : 'border-[#e2e8f0]'} text-center`}>
                  <span className={`block text-xs ${subTextColor} mb-1 uppercase tracking-wider`}>Generation</span>
                  <span className={`text-2xl font-mono font-bold ${textColor}`}>{stats.generationCount}</span>
                </div>
              </div>
              
              {entropyHistory.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-800/50 text-center">
                  <button 
                    onClick={() => setShowHistoryModal(true)}
                    className={`w-full text-xs font-bold px-5 py-3 rounded-xl transition-all border shadow-sm ${isDarkMode ? 'bg-gray-800/80 hover:bg-gray-700 border-gray-700 text-gray-300 hover:text-[#00FFA3] hover:border-[#00FFA3]/50' : 'bg-gray-100 hover:bg-gray-200 border-gray-200 text-gray-600 hover:text-[#0A1929]'}`}
                  >
                    View All Outputs
                  </button>
                </div>
              )}
            </div>

            {/* Çıktı Kartı */}
            <div className={`glass-card ${glassCardClass} backdrop-blur-xl rounded-2xl p-5 border ${isDarkMode ? 'border-white/10' : 'border-[#e2e8f0]'}`}>
              <h3 className={`text-sm font-bold mb-4 flex items-center gap-2 ${textColor}`}>
                <span className={`w-1.5 h-6 rounded-full ${isDarkMode ? 'bg-[#00FFA3] shadow-[0_0_10px_#00FFA3]' : 'bg-[#0A1929]'}`}></span>
                Output (Byte Stream)
              </h3>
              
              {/* output-bytes-grid ile 4 sütunlu byte grid */}
              <div className="output-bytes-grid">
                {entropyData.length > 0 ? (
                  entropyData.slice(0, 8).map((val, idx) => (
                    <div key={idx} className={`${isDarkMode ? 'bg-black/20' : 'bg-[#f8fafc]'} p-2 rounded-lg text-center border ${isDarkMode ? 'border-white/5' : 'border-[#e2e8f0]'} hover:border-[#00FFA3]/50 transition-all`}>
                      <span className="block text-[10px] text-gray-500 mb-1">B{idx+1}</span>
                      <span className={`font-mono ${accentColor} font-bold responsive-byte-text`}>
                        {settings.format === 'hex' ? val.toString(16).toUpperCase().padStart(2, '0') :
                         settings.format === 'bin' ? val.toString(2).padStart(8, '0').substring(0,4) + '..' :
                         val}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="col-span-4 text-center py-6 text-gray-500 text-xs">
                    Waiting for data...
                  </div>
                )}
              </div>
              
              {entropyData.length > 8 && (
                <div className="mt-4 text-center flex flex-col items-center gap-3">
                  <span className="text-[10px] text-gray-500">+{entropyData.length - 8} more bytes</span>
                  <button 
                    onClick={() => setShowAllOutputs(true)}
                    className={`text-xs font-bold px-5 py-2.5 rounded-xl transition-all border shadow-sm ${isDarkMode ? 'bg-gray-800/80 hover:bg-gray-700 border-gray-700 text-gray-300 hover:text-[#00FFA3] hover:border-[#00FFA3]/50' : 'bg-gray-100 hover:bg-gray-200 border-gray-200 text-gray-600 hover:text-[#0A1929]'}`}
                  >
                    View Outputs
                  </button>
                </div>
              )}
            </div>
            
          </div>
        </div>

      </main>

      {/* Pipeline Section */}
      <EntropyPipeline entropyData={entropyData} blockNumber={blockNumber} showToast={showToast} />

      {/* Footer */}
      <footer className={`relative z-10 py-6 border-t mt-auto ${isDarkMode ? 'border-white/5 text-gray-400' : 'border-[#e2e8f0] text-gray-500'}`}>
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-medium">
          <p className="text-center md:text-left leading-relaxed">
            &copy; {new Date().getFullYear()} <span className={isDarkMode ? 'text-white' : 'text-gray-900'}>EntropyHub</span>. Decentralized Randomness Beacon.
          </p>
          <div className="flex flex-wrap justify-center gap-5 md:gap-6 mt-2 md:mt-0">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-[#00FFA3] transition-colors">Docs</a>
            <a href="https://github.com/Ahmetoyann/EntropyHub_A" target="_blank" rel="noopener noreferrer" className="hover:text-[#00FFA3] transition-colors">GitHub</a>
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setShowStatusModal(true); }} 
              className="hover:text-[#00FFA3] transition-colors"
            >
              Status
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
 
export default App;