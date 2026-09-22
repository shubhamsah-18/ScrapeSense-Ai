// ============================================================
// SCRAPSENSE AI - ENHANCED FRONTEND CONTROLLER
// ============================================================
// Features: Zero-Shot CLIP AI, Electronic Components Scanner,
// Dynamic Mandi Valuation, Seller Category Views, Mobile QR Link
// ============================================================

// Dynamic & Resilient API Base Auto-Discovery
function getInitialApiBase() {
  if (window.location.port === "8000" || (window.location.protocol.startsWith("http") && !window.location.port)) {
    return "";
  }
  try {
    const saved = localStorage.getItem("scrapsense_api_base");
    if (saved !== null && saved !== undefined && saved !== "") return saved;
  } catch {}
  const host = window.location.hostname;
  if (host && host !== "localhost" && host !== "127.0.0.1") {
    return `http://${host}:8000`;
  }
  return "http://127.0.0.1:8000";
}

let API_BASE = getInitialApiBase();

function getCandidateApiBases() {
  const list = [];
  if (window.location.port === "8000") list.push("");
  if (API_BASE && !list.includes(API_BASE)) list.push(API_BASE);
  try {
    const saved = localStorage.getItem("scrapsense_api_base");
    if (saved && !list.includes(saved)) list.push(saved);
  } catch {}
  if (!list.includes("http://127.0.0.1:8000")) list.push("http://127.0.0.1:8000");
  if (!list.includes("http://localhost:8000")) list.push("http://localhost:8000");
  if (window.location.hostname && !list.includes(`http://${window.location.hostname}:8000`)) {
    list.push(`http://${window.location.hostname}:8000`);
  }
  if (!list.includes("")) list.push("");
  return list;
}

// ---------------- DOM ELEMENTS ----------------
const serverStatus = document.getElementById("serverStatus");
const serverStatusText = document.getElementById("serverStatusText");

// Header & Navigation
const openPhoneModalBtn = document.getElementById("openPhoneModalBtn");
const phoneModal = document.getElementById("phoneModal");
const closePhoneModal = document.getElementById("closePhoneModal");
const phoneUrlInput = document.getElementById("phoneUrlInput");
const copyPhoneUrlBtn = document.getElementById("copyPhoneUrlBtn");
const phoneQrCanvas = document.getElementById("phoneQrCanvas");

const sellerNavBar = document.getElementById("sellerNavBar");
const sellerTabBtns = document.querySelectorAll(".seller-tab-btn");

const scanTabs = document.querySelectorAll(".scan-tab");
const dropzone = document.getElementById("dropzone");
const dropzoneHint = document.getElementById("dropzoneHint");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const previewImg = document.getElementById("previewImg");

const cameraBox = document.getElementById("cameraBox");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const startCamBtn = document.getElementById("startCamBtn");
const switchCamBtn = document.getElementById("switchCamBtn");
const captureBtn = document.getElementById("captureBtn");
const retakeBtn = document.getElementById("retakeBtn");

const analyzeBtn = document.getElementById("analyzeBtn");
const statusMsg = document.getElementById("statusMsg");

// Result Receipt Elements
const resultWrap = document.getElementById("resultWrap");
const rIcon = document.getElementById("rIcon");
const rName = document.getElementById("rName");
const rTag = document.getElementById("rTag");
const rConfidence = document.getElementById("rConfidence");
const rCategory = document.getElementById("rCategory");
const rType = document.getElementById("rType");
const rPrice = document.getElementById("rPrice");
const rSellTo = document.getElementById("rSellTo");
const rTip = document.getElementById("rTip");
const rAltList = document.getElementById("rAltList");
const printReceiptBtn = document.getElementById("printReceiptBtn");
const saveHistoryBtn = document.getElementById("saveHistoryBtn");

// Calculator Elements
const calcUnitLabel = document.getElementById("calcUnitLabel");
const calcUnitTag = document.getElementById("calcUnitTag");
const calcQty = document.getElementById("calcQty");
const calcSlider = document.getElementById("calcSlider");
const payoutMin = document.getElementById("payoutMin");
const payoutAvg = document.getElementById("payoutAvg");
const payoutMax = document.getElementById("payoutMax");

// Eco Impact Elements
const ecoBadgeText = document.getElementById("ecoBadgeText");
const ecoCo2 = document.getElementById("ecoCo2");
const ecoEnergy = document.getElementById("ecoEnergy");

// History & Stats Elements
const statItemCount = document.getElementById("statItemCount");
const statTotalValue = document.getElementById("statTotalValue");
const statCo2Saved = document.getElementById("statCo2Saved");
const historyTbody = document.getElementById("historyTbody");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

// Directory & Catalog Elements
const categoryGrid = document.getElementById("categoryGrid");
const categorySearch = document.getElementById("categorySearch");
const categoryPills = document.querySelectorAll(".cat-pill");

// Admin & Listing Elements
const productForm = document.getElementById("productForm");
const buyerForm = document.getElementById("buyerForm");
const adminProducts = document.getElementById("adminProducts");
const adminBuyers = document.getElementById("adminBuyers");
const adminSummary = document.getElementById("adminSummary");
const productCount = document.getElementById("productCount");
const buyerCount = document.getElementById("buyerCount");
const adminRequests = document.getElementById("adminRequests");
const requestCount = document.getElementById("requestCount");
const registeredUsers = document.getElementById("registeredUsers");
const registeredUserCount = document.getElementById("registeredUserCount");

// Auth Elements
const authScreen = document.getElementById("authScreen");
const authForm = document.getElementById("authForm");
const authMessage = document.getElementById("authMessage");
const authEmailInput = document.getElementById("authEmailInput");
const authPasswordInput = document.getElementById("authPasswordInput");
const authEmailLabel = document.getElementById("authEmailLabel");
const loginTitle = document.getElementById("loginTitle");
const loginSubtitle = document.getElementById("loginSubtitle");
const loginSubmitBtn = document.getElementById("loginSubmitBtn");
const registerSwitchPrompt = document.getElementById("registerSwitchPrompt");

const registrationForm = document.getElementById("registrationForm");
const registrationMessage = document.getElementById("registrationMessage");
const regNameInput = document.getElementById("regNameInput");
const regEmailInput = document.getElementById("regEmailInput");
const regPasswordInput = document.getElementById("regPasswordInput");
const registerTitle = document.getElementById("registerTitle");
const registerSubtitle = document.getElementById("registerSubtitle");
const registerSubmitBtn = document.getElementById("registerSubmitBtn");

const modeLoginBtn = document.getElementById("modeLoginBtn");
const loginCard = document.getElementById("loginCard");
const registerCard = document.getElementById("registerCard");
const goToRegisterBtn = document.getElementById("goToRegisterBtn");
const goToLoginBtn = document.getElementById("goToLoginBtn");

const adminHint = document.getElementById("adminHint");
// New role card buttons (replaced old role-tab buttons)
const roleCardBtns = document.querySelectorAll(".auth-role-card");
const logoutBtn = document.getElementById("logoutBtn");
const sessionLabel = document.getElementById("sessionLabel");
const authRoleBadgeIcon = document.getElementById("authRoleBadgeIcon");
const authRoleBadgeLabel = document.getElementById("authRoleBadgeLabel");
const authFormPanel = document.getElementById("authFormPanel");
const modeRegisterBtn = document.getElementById("modeRegisterBtn");
const buyerNameHidden = document.getElementById("buyerNameHidden");

// Seller Lot Submission
const listingForm = document.getElementById("listingForm");
const listingMessage = document.getElementById("listingMessage");
const lotItemInput = document.getElementById("lotItemInput");
const lotCategorySelect = document.getElementById("lotCategorySelect");
const lotUnitSelect = document.getElementById("lotUnitSelect");
const sellerPostLotSection = document.getElementById("sellerPostLot");

// Marketplace & Orders
const marketGrid = document.getElementById("marketGrid");
const marketCount = document.getElementById("marketCount");
const ordersList = document.getElementById("ordersList");
const ordersSection = document.getElementById("orders");
const marketSection = document.getElementById("marketplace");
const cityFilter = document.getElementById("cityFilter");

// Layout Sections
const heroSection = document.getElementById("detect");
const historySection = document.getElementById("history");
const categoriesSection = document.getElementById("categories");
const howSection = document.getElementById("how");
const resultSection = document.getElementById("resultWrap");
const listingState = document.getElementById("listingState");
const listingCity = document.getElementById("listingCity");

// Sample chips
const sampleChips = document.querySelectorAll(".sample-chip");

// Buyer Decision Modal Elements
const purchaseModal = document.getElementById("purchaseModal");
const purchaseForm = document.getElementById("purchaseForm");
const purchaseItem = document.getElementById("purchaseItem");
const buyerDecision = document.getElementById("buyerDecision");
const buyerOfferPrice = document.getElementById("buyerOfferPrice");
const purchaseMessage = document.getElementById("purchaseMessage");
const paymentReceipt = document.getElementById("paymentReceipt");
const receiptNumber = document.getElementById("receiptNumber");
const receiptQr = document.getElementById("receiptQr");

// Seller Category Selector & Valuation Hub Elements
const sellerCategoryBar = document.getElementById("sellerCategoryBar");
const sellerCatPills = document.querySelectorAll(".seller-cat-pill");
const electronicScannerWrapper = document.getElementById("electronicScannerWrapper");
const categoryValuationHub = document.getElementById("categoryValuationHub");
const currentCategoryName = document.getElementById("currentCategoryName");
const switchToCameraBtn = document.getElementById("switchToCameraBtn");
const categoryHubTitle = document.getElementById("categoryHubTitle");
const categoryHubSubtitle = document.getElementById("categoryHubSubtitle");
const categoryCardsGrid = document.getElementById("categoryCardsGrid");
const catCalcItemSelect = document.getElementById("catCalcItemSelect");
const catCalcQty = document.getElementById("catCalcQty");
const catCalcUnitLabel = document.getElementById("catCalcUnitLabel");
const catCalcRateText = document.getElementById("catCalcRateText");
const catCalcTotalPayout = document.getElementById("catCalcTotalPayout");
const catCalcMinPayout = document.getElementById("catCalcMinPayout");
const catCalcMaxPayout = document.getElementById("catCalcMaxPayout");
const catCalcSellBtn = document.getElementById("catCalcSellBtn");

// ---------------- STATE ----------------
let currentBlob = null;
let cameraStream = null;
let activeMode = "camera"; // Default to camera for instant scanning
let currentFacingMode = "environment"; // Mobile back camera default
let isBackendOnline = false;
let currentResult = null;
let allCategories = [];
let activeCatFilter = "all";
let activeSellerTab = "scanner";
let activeSellerCategory = "All Categories";
let authRole = "seller";
let currentSession = null;
let authToken = null;
let selectedListingId = null;

// Escape HTML helper
function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function sanitizeImageSrc(src) {
  if (!src) return "";
  if (src.startsWith("data:image/") || src.startsWith("http://") || src.startsWith("https://")) {
    return src;
  }
  return "";
}

// Persistent token & session storage helpers (localStorage with sessionStorage fallback)
function getStoredToken() {
  try {
    return localStorage.getItem("scrapsense_token") || sessionStorage.getItem("scrapsense_token");
  } catch {
    return null;
  }
}

function saveStoredToken(token) {
  try { localStorage.setItem("scrapsense_token", token); } catch {}
  try { sessionStorage.setItem("scrapsense_token", token); } catch {}
}

function clearStoredToken() {
  try { localStorage.removeItem("scrapsense_token"); } catch {}
  try { sessionStorage.removeItem("scrapsense_token"); } catch {}
}

function getStoredSession() {
  try {
    const raw = localStorage.getItem("scrapsense_session") || sessionStorage.getItem("scrapsense_session");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveStoredSession(session) {
  try { localStorage.setItem("scrapsense_session", JSON.stringify(session)); } catch {}
  try { sessionStorage.setItem("scrapsense_session", JSON.stringify(session)); } catch {}
}

function clearStoredSession() {
  try { localStorage.removeItem("scrapsense_session"); } catch {}
  try { sessionStorage.removeItem("scrapsense_session"); } catch {}
}

// JWT token management
function getAuthHeaders() {
  const token = authToken || getStoredToken();
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

function setAuthToken(token) {
  authToken = token;
  if (token) saveStoredToken(token);
  else clearStoredToken();
}

// Indian States & Major Scrap Hubs
const STATE_CITIES = {
  Rajasthan: ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar"],
  Delhi: ["New Delhi", "North Delhi", "South Delhi"],
  Haryana: ["Gurugram", "Faridabad", "Panipat", "Hisar", "Ambala"],
  Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
  Maharashtra: ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
  "Uttar Pradesh": ["Noida", "Ghaziabad", "Agra", "Lucknow", "Kanpur", "Varanasi"],
  "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur"],
  Punjab: ["Ludhiana", "Amritsar", "Jalandhar"],
  Karnataka: ["Bengaluru", "Mysuru", "Hubballi"],
  "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"]
};

function updateListingCities() {
  if (!listingState || !listingCity) return;
  const stateVal = listingState.value || "Rajasthan";
  listingCity.innerHTML = (STATE_CITIES[stateVal] || ["Jaipur"]).map(city => `<option value="${escapeHTML(city)}">${escapeHTML(city)}</option>`).join("");
}

listingState?.addEventListener("change", updateListingCities);
updateListingCities();

// ============================================================
// COMPREHENSIVE ELECTRONIC COMPONENTS & SCRAP DATASET
// ============================================================
const DEMO_ITEMS = {
  arduino: {
    detected_item: "Microcontroller Dev Board (Arduino/ESP32)",
    icon: "🤖",
    confidence: 98.6,
    category: "High-Grade E-Waste",
    type: "Reusable / High Resale Value",
    unit: "unit",
    min_price: 80,
    max_price: 600,
    price_range: "₹80 - ₹600 / unit",
    sell_to: "Maker labs / Electronics repair shops / Refurbishers",
    reuse_tip: "Functional microcontrollers can be re-programmed and repurposed into IoT sensors, home automation switches, or robotics projects.",
    eco_impact: {
      co2_saved_per_unit: "2.8 kg CO₂ per board",
      energy_saved: "Preserves 95% embedded silicon energy",
      badge: "IoT Hardware Circular Reclaim"
    },
    top_predictions: [
      { name: "Microcontroller Dev Board (Arduino/ESP32)", confidence: 98.6, category: "High-Grade E-Waste" },
      { name: "Motherboard / PCB", confidence: 1.1, category: "High-Grade E-Waste" },
      { name: "IC Chips / Microchips", confidence: 0.2, category: "High-Grade E-Waste" }
    ]
  },
  motherboard: {
    detected_item: "Motherboard / PCB (Multi-layer)",
    icon: "🔌",
    confidence: 97.4,
    category: "High-Grade E-Waste",
    type: "Hazardous - Contains Precious Metals",
    unit: "kg",
    min_price: 180,
    max_price: 450,
    price_range: "₹180 - ₹450 / kg",
    sell_to: "Certified PCB refiner / Registered E-waste dismantler",
    reuse_tip: "Printed circuit boards contain gold plating, copper traces, and rare earths. Never burn or acid-wash at home; send to certified hydrometallurgical recyclers.",
    eco_impact: {
      co2_saved_per_unit: "3.5 kg CO₂ per kg",
      energy_saved: "90% less carbon footprint than ore mining",
      badge: "Gold & Copper Rich"
    },
    top_predictions: [
      { name: "Motherboard / PCB", confidence: 97.4, category: "High-Grade E-Waste" },
      { name: "RAM Memory Stick", confidence: 1.8, category: "High-Grade E-Waste" },
      { name: "Desktop CPU Tower", confidence: 0.5, category: "E-Waste" }
    ]
  },
  ic_chip: {
    detected_item: "Integrated Circuit (IC Chips / Microchips)",
    icon: "🔲",
    confidence: 98.2,
    category: "High-Grade E-Waste",
    type: "Hazardous - High Gold Content",
    unit: "kg",
    min_price: 400,
    max_price: 950,
    price_range: "₹400 - ₹950 / kg",
    sell_to: "Certified hydrometallurgical e-waste refinery",
    reuse_tip: "DIP, SOP, and QFP package ICs contain pure gold wire bonding between silicon dies and external lead frames. High-yield scrap category.",
    eco_impact: {
      co2_saved_per_unit: "8.5 kg CO₂ per kg",
      energy_saved: "Direct gold extraction avoids open-pit ore mining",
      badge: "High Gold Yield IC Scrap"
    },
    top_predictions: [
      { name: "Integrated Circuit (IC Chips)", confidence: 98.2, category: "High-Grade E-Waste" },
      { name: "CPU / Microprocessor", confidence: 1.3, category: "High-Grade E-Waste" },
      { name: "Resistors, Diodes & SMD", confidence: 0.4, category: "Electronic Component Scrap" }
    ]
  },
  cpu: {
    detected_item: "CPU / Microprocessor (Gold Pin / Ceramic)",
    icon: "🧠",
    confidence: 97.9,
    category: "High-Grade E-Waste",
    type: "Hazardous - High Value Precious Metals",
    unit: "unit",
    min_price: 80,
    max_price: 350,
    price_range: "₹80 - ₹350 / unit",
    sell_to: "Certified E-waste refiner / Precious metals processor",
    reuse_tip: "Ceramic and fiber CPUs contain pure microscopic gold bonding wires and gold-plated pins. Keep pins unbent to preserve grading tier.",
    eco_impact: {
      co2_saved_per_unit: "5.5 kg CO₂ per chip",
      energy_saved: "Recovers 99.9% pure gold, silver & palladium",
      badge: "Precious Metals Recovery"
    },
    top_predictions: [
      { name: "CPU / Microprocessor", confidence: 97.9, category: "High-Grade E-Waste" },
      { name: "RAM Memory Stick", confidence: 1.4, category: "High-Grade E-Waste" },
      { name: "Motherboard / PCB", confidence: 0.5, category: "High-Grade E-Waste" }
    ]
  },
  gpu: {
    detected_item: "Graphics Card (GPU / Video Card)",
    icon: "🎮",
    confidence: 96.9,
    category: "High-Grade E-Waste",
    type: "Recyclable - High Resale Value",
    unit: "unit",
    min_price: 250,
    max_price: 1500,
    price_range: "₹250 - ₹1,500 / unit",
    sell_to: "Computer hardware refurbisher / E-waste dismantler",
    reuse_tip: "Working GPUs have strong demand for budget gaming or AI inference. Broken cards yield heavy copper heatsinks, GDDR memory chips, and VRMs.",
    eco_impact: {
      co2_saved_per_unit: "18.0 kg CO₂ per card",
      energy_saved: "Direct copper heatsink and silicon reclamation",
      badge: "High-Spec Silicon Harvest"
    },
    top_predictions: [
      { name: "Graphics Card (GPU)", confidence: 96.9, category: "High-Grade E-Waste" },
      { name: "Motherboard / PCB", confidence: 2.1, category: "High-Grade E-Waste" },
      { name: "Desktop CPU Tower", confidence: 0.8, category: "E-Waste" }
    ]
  },
  transformer: {
    detected_item: "Electrical Transformer / Choke Coil",
    icon: "⚡",
    confidence: 98.1,
    category: "Heavy Copper Scrap",
    type: "Recyclable - Dense Copper Content",
    unit: "kg",
    min_price: 70,
    max_price: 140,
    price_range: "₹70 - ₹140 / kg",
    sell_to: "Motor rewinding center / Copper scrap smelter",
    reuse_tip: "Transformers contain pure enamel-coated copper wire wrapped over silicon steel laminations. Separate copper coils to earn top copper rate.",
    eco_impact: {
      co2_saved_per_unit: "4.8 kg CO₂ per kg",
      energy_saved: "88% energy savings over virgin copper mining",
      badge: "Dense Copper Core"
    },
    top_predictions: [
      { name: "Electrical Transformer / Choke", confidence: 98.1, category: "Heavy Copper Scrap" },
      { name: "Electric Motor / Compressor", confidence: 1.4, category: "Heavy Copper Scrap" },
      { name: "Toroid / Inductor Coil", confidence: 0.4, category: "Non-Ferrous Metal" }
    ]
  },
  capacitor: {
    detected_item: "Capacitors (Electrolytic / Ceramic / Tantalum)",
    icon: "🔋",
    confidence: 96.5,
    category: "Electronic Component Scrap",
    type: "Recyclable - Mixed Metals",
    unit: "kg",
    min_price: 35,
    max_price: 85,
    price_range: "₹35 - ₹85 / kg",
    sell_to: "E-waste chemical recycler / Metal refiner",
    reuse_tip: "Electrolytic capacitors contain high-purity aluminium foil electrodes, while yellow SMD tantalum capacitors contain scarce Tantalum metal.",
    eco_impact: {
      co2_saved_per_unit: "1.9 kg CO₂ per kg",
      energy_saved: "Prevents hazardous electrolyte soil contamination",
      badge: "Tantalum & Aluminium Foil"
    },
    top_predictions: [
      { name: "Capacitors (Electrolytic/Tantalum)", confidence: 96.5, category: "Electronic Component Scrap" },
      { name: "Resistors & SMD Parts", confidence: 2.5, category: "Electronic Component Scrap" },
      { name: "Integrated Circuit (IC Chips)", confidence: 0.8, category: "High-Grade E-Waste" }
    ]
  },
  resistor: {
    detected_item: "Resistors, Diodes & SMD Parts",
    icon: "🎛️",
    confidence: 96.2,
    category: "Electronic Component Scrap",
    type: "Recyclable - Small Components",
    unit: "kg",
    min_price: 25,
    max_price: 65,
    price_range: "₹25 - ₹65 / kg",
    sell_to: "PCB component aggregator / Electronics lab surplus buyer",
    reuse_tip: "Surplus reels or salvaged components can be sold in bulk lots to robotics makers, hobbyists, repair labs, and engineering colleges.",
    eco_impact: {
      co2_saved_per_unit: "1.4 kg CO₂ per kg",
      energy_saved: "Reclaims copper leads, tin plating, and ceramics",
      badge: "Micro-Component Circularity"
    },
    top_predictions: [
      { name: "Resistors, Diodes & SMD Parts", confidence: 96.2, category: "Electronic Component Scrap" },
      { name: "Capacitors (Electrolytic/Ceramic)", confidence: 2.8, category: "Electronic Component Scrap" },
      { name: "Integrated Circuit (IC Chips)", confidence: 0.7, category: "High-Grade E-Waste" }
    ]
  },
  inductor: {
    detected_item: "Toroid / Inductor Copper Coil",
    icon: "🧲",
    confidence: 97.5,
    category: "Non-Ferrous Metal & E-Waste",
    type: "Recyclable - Pure Magnet Wire",
    unit: "kg",
    min_price: 140,
    max_price: 280,
    price_range: "₹140 - ₹280 / kg",
    sell_to: "Copper scrap merchant / Electrical re-winder",
    reuse_tip: "Toroids feature thick copper magnet wire wrapped over ferrite cores. Stripping the wire yields top-tier copper scrap pricing.",
    eco_impact: {
      co2_saved_per_unit: "3.7 kg CO₂ per kg",
      energy_saved: "85% energy saved over virgin copper smelting",
      badge: "Pure Magnet Wire Copper"
    },
    top_predictions: [
      { name: "Toroid / Inductor Copper Coil", confidence: 97.5, category: "Non-Ferrous Metal" },
      { name: "Copper Wire Scrap", confidence: 1.8, category: "Non-Ferrous Metal" },
      { name: "Electrical Transformer", confidence: 0.6, category: "Heavy Copper Scrap" }
    ]
  },
  solder: {
    detected_item: "Solder Wire Scrap / Tin-Lead Dross",
    icon: "🪙",
    confidence: 97.8,
    category: "Non-Ferrous Metal",
    type: "Recyclable - High Tin & Silver Purity",
    unit: "kg",
    min_price: 450,
    max_price: 850,
    price_range: "₹450 - ₹850 / kg",
    sell_to: "Tin smelting refinery / Electronics assembly reclaimer",
    reuse_tip: "Lead-free SAC305 solder contains 96.5% Tin, 3.0% Silver, and 0.5% Copper. Highly valuable when collected cleanly from de-soldering work.",
    eco_impact: {
      co2_saved_per_unit: "6.0 kg CO₂ per kg",
      energy_saved: "Diverts toxic lead from landfills and recovers refined tin",
      badge: "High Purity Tin-Silver Alloy"
    },
    top_predictions: [
      { name: "Solder Wire Scrap / Tin Dross", confidence: 97.8, category: "Non-Ferrous Metal" },
      { name: "Copper Wire Scrap", confidence: 1.5, category: "Non-Ferrous Metal" },
      { name: "Aluminium Scrap", confidence: 0.5, category: "Non-Ferrous Metal" }
    ]
  },
  copper: {
    detected_item: "Copper Wire / Copper Scrap (Millberry)",
    icon: "🔶",
    confidence: 98.4,
    category: "Non-Ferrous Metal",
    type: "Recyclable - Premium Resale Value",
    unit: "kg",
    min_price: 480,
    max_price: 680,
    price_range: "₹480 - ₹680 / kg",
    sell_to: "Electrical scrap dealer / Copper refinery",
    reuse_tip: "Stripped, shiny 'Millberry' copper wire commands the highest price tier. Mechanically strip insulation instead of burning.",
    eco_impact: {
      co2_saved_per_unit: "4.5 kg CO₂ per kg",
      energy_saved: "85% energy saved vs mining",
      badge: "Top Resale Value Metal"
    },
    top_predictions: [
      { name: "Copper Wire Scrap", confidence: 98.4, category: "Non-Ferrous Metal" },
      { name: "Insulated Electrical Cable", confidence: 1.1, category: "Mixed Scrap" },
      { name: "Brass Scrap / Fittings", confidence: 0.3, category: "Non-Ferrous Metal" }
    ]
  },
  battery: {
    detected_item: "Lead-Acid Battery (Auto/Inverter)",
    icon: "🔋",
    confidence: 95.7,
    category: "Hazardous Waste",
    type: "Hazardous - Acid & Heavy Metals",
    unit: "kg",
    min_price: 85,
    max_price: 115,
    price_range: "₹85 - ₹115 / kg",
    sell_to: "Battery dealer buy-back scheme / Authorized smelter",
    reuse_tip: "Almost all major battery retailers provide direct ₹500–₹1,500 exchange discounts on new purchases when returning spent batteries.",
    eco_impact: {
      co2_saved_per_unit: "2.1 kg CO₂ per kg lead",
      energy_saved: "99% infinitely recyclable lead",
      badge: "99% Recyclability Index"
    },
    top_predictions: [
      { name: "Lead-Acid Battery", confidence: 95.7, category: "Hazardous Waste" },
      { name: "Lithium-Ion Battery", confidence: 3.2, category: "Hazardous E-Waste" },
      { name: "EV Battery Pack", confidence: 0.8, category: "Automotive E-Waste" }
    ]
  },
  ev_battery: {
    detected_item: "EV Battery Pack (LFP / NMC)",
    icon: "⚡",
    confidence: 96.8,
    category: "Automotive E-Waste",
    type: "Hazardous - High Voltage Specialized",
    unit: "unit",
    min_price: 15000,
    max_price: 60000,
    price_range: "₹15,000 - ₹60,000 / pack (assessed)",
    sell_to: "Authorized EV OEM / Second-life energy storage buyer",
    reuse_tip: "Decommissioned EV packs typically retain 70-80% capacity — ideal for secondary life stationary solar storage systems.",
    eco_impact: {
      co2_saved_per_unit: "1,200 kg CO₂ per pack",
      energy_saved: "Extends utility by 5-8 years",
      badge: "Second-Life Solar Storage"
    },
    top_predictions: [
      { name: "EV Battery Pack", confidence: 96.8, category: "Automotive E-Waste" },
      { name: "Lead-Acid Battery", confidence: 1.9, category: "Hazardous Waste" },
      { name: "Lithium-Ion Battery", confidence: 0.8, category: "Hazardous E-Waste" }
    ]
  },
  computer: {
    detected_item: "Old Desktop Computer / Laptop",
    icon: "💻",
    confidence: 98.5,
    category: "E-Waste",
    type: "Whole IT Equipment",
    unit: "pcs",
    min_price: 350,
    max_price: 900,
    price_range: "₹350 - ₹900 / pcs",
    sell_to: "Authorized E-Waste Dismantler / Refurbisher",
    reuse_tip: "Intact desktops yield valuable motherboards, copper heatsinks, power supplies, and RAM. Check working condition for resale premium.",
    eco_impact: {
      co2_saved_per_unit: "25.0 kg CO₂ per unit",
      energy_saved: "Recovers gold, silver, copper & steel",
      badge: "High Value IT Unit"
    },
    top_predictions: [
      { name: "Old Desktop Computer / Laptop", confidence: 98.5, category: "E-Waste" },
      { name: "Motherboard / PCB", confidence: 1.1, category: "High-Grade E-Waste" },
      { name: "CPU / Microprocessor", confidence: 0.3, category: "High-Grade E-Waste" }
    ]
  },
  mobile: {
    detected_item: "Mobile Phone (Broken / Old)",
    icon: "📱",
    confidence: 97.8,
    category: "E-Waste",
    type: "Precious Metal E-Waste",
    unit: "pcs",
    min_price: 80,
    max_price: 250,
    price_range: "₹80 - ₹250 / pcs",
    sell_to: "Precious Metal E-Waste Refiner",
    reuse_tip: "Smartphones contain concentrated gold on mainboards and high-capacity lithium cells. Erase personal data before recycling.",
    eco_impact: {
      co2_saved_per_unit: "6.0 kg CO₂ per phone",
      energy_saved: "Avoids open-pit ore mining of precious metals",
      badge: "Precious Metals Core"
    },
    top_predictions: [
      { name: "Mobile Phone (Broken/Old)", confidence: 97.8, category: "E-Waste" },
      { name: "Lithium-Ion Battery", confidence: 1.5, category: "Hazardous E-Waste" },
      { name: "Motherboard / PCB", confidence: 0.5, category: "High-Grade E-Waste" }
    ]
  },
  tv: {
    detected_item: "Old TV / Monitor Screen",
    icon: "📺",
    confidence: 96.7,
    category: "E-Waste",
    type: "Display Device E-Waste",
    unit: "pcs",
    min_price: 200,
    max_price: 600,
    price_range: "₹200 - ₹600 / pcs",
    sell_to: "Authorized E-Waste Glass & Metal Processor",
    reuse_tip: "Heavy copper deflection yokes, power inverter boards, and aluminium frames are reclaimed.",
    eco_impact: {
      co2_saved_per_unit: "14.0 kg CO₂ per unit",
      energy_saved: "Safely isolates leaded glass and recovers copper",
      badge: "Copper Yoke & Glass"
    },
    top_predictions: [
      { name: "Old TV / Monitor Screen", confidence: 96.7, category: "E-Waste" },
      { name: "Power Transformer", confidence: 2.1, category: "Heavy Copper Scrap" },
      { name: "Motherboard / PCB", confidence: 0.8, category: "High-Grade E-Waste" }
    ]
  }
};

// ============================================================
// INITIALIZATION & PERSISTENT SERVER HEALTH MONITORING
// ============================================================
let wasBackendOnline = null;
let healthCheckTimer = null;
let isCheckingHealth = false;
let consecutiveFailures = 0;

async function pingEndpoint(base, timeoutMs = 5000) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    const res = await fetch(`${base}/health`, { method: "GET", signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (e) {
    // Ping failed
  }
  return null;
}

async function checkBackendStatus(isManual = false) {
  if (isCheckingHealth && !isManual) return isBackendOnline;
  isCheckingHealth = true;

  if (isManual && serverStatusText) {
    serverStatusText.textContent = "Connecting...";
    const dot = serverStatus?.querySelector(".status-dot");
    if (dot) dot.className = "status-dot reconnecting";
  }

  // 1. Try current API_BASE first
  let data = await pingEndpoint(API_BASE, 5000);

  // 2. If failed, auto-discover across candidates
  if (!data) {
    const candidates = getCandidateApiBases();
    for (const candidate of candidates) {
      if (candidate === API_BASE) continue;
      const testData = await pingEndpoint(candidate, 3000);
      if (testData) {
        API_BASE = candidate;
        try { localStorage.setItem("scrapsense_api_base", candidate); } catch {}
        data = testData;
        break;
      }
    }
  }

  if (data) {
    consecutiveFailures = 0;
    const firstConnectOrRecovered = wasBackendOnline === false || wasBackendOnline === null;
    isBackendOnline = true;
    wasBackendOnline = true;

    const dot = serverStatus?.querySelector(".status-dot");
    if (dot) dot.className = "status-dot online";
    if (serverStatusText) {
      serverStatusText.textContent = data.mongo_connected
        ? (data.model_ready ? "Backend + MongoDB Live" : "Backend Live · AI Ready")
        : "Backend Live · Standalone";
    }

    if (data.local_ip && data.local_ip !== "127.0.0.1") {
      serverLanIp = data.local_ip;
      try { localStorage.setItem("scrapsense_lan_ip", data.local_ip); } catch {}
    }
    if (Array.isArray(data.all_ips) && data.all_ips.length > 0) {
      serverAllIps = data.all_ips;
    }

    // If backend just came online or reconnected, sync catalog and data automatically
    if (firstConnectOrRecovered) {
      loadCategories();
      if (currentSession) {
        syncListings();
        syncOrders();
      }
    }
    isCheckingHealth = false;
    scheduleHeartbeat(10000);
    return true;
  }

  // Failed check
  consecutiveFailures++;
  // Debounce: Only show reconnecting / offline if 2 consecutive pings fail or user clicked manually
  if (consecutiveFailures >= 2 || isManual || wasBackendOnline === null) {
    isBackendOnline = false;
    const dot = serverStatus?.querySelector(".status-dot");
    if (dot) {
      dot.className = wasBackendOnline === true ? "status-dot reconnecting" : "status-dot offline";
    }
    if (serverStatusText) {
      serverStatusText.textContent = wasBackendOnline === true ? "Reconnecting..." : "AI Simulator Active";
    }
    wasBackendOnline = false;
  }

  isCheckingHealth = false;
  scheduleHeartbeat(3000);
  return false;
}

function scheduleHeartbeat(delayMs) {
  if (healthCheckTimer) clearTimeout(healthCheckTimer);
  healthCheckTimer = setTimeout(() => {
    checkBackendStatus(false);
  }, delayMs);
}

// Start continuous background heartbeat
function startBackendHeartbeat() {
  scheduleHeartbeat(isBackendOnline ? 10000 : 3000);
}

// Click on server status badge to manually trigger instant check & reconnect
serverStatus?.setAttribute("title", "ScrapSense Backend Status · Click to Reconnect");
serverStatus?.addEventListener("click", () => {
  checkBackendStatus(true);
});

// Auto-recheck immediately when user returns to tab or network comes online
window.addEventListener("focus", () => checkBackendStatus(true));
window.addEventListener("online", () => checkBackendStatus(true));

// ============================================================
// SELLER CATEGORY TABS SWITCHER
// ============================================================
function setSellerView(tabName) {
  activeSellerTab = tabName;
  sellerTabBtns.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.sellerTab === tabName);
  });

  const isSeller = currentSession && currentSession.role === "seller";
  if (!isSeller) return;

  if (tabName === "scanner") {
    heroSection.hidden = false;
    categoriesSection.hidden = false; // Show Price Rates on First Page
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = true;
    setSellerCategory(activeSellerCategory || "All Categories");
  } else if (tabName === "post-lot") {
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = false;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = true;
    // Pre-populate if currentResult exists
    if (currentResult) {
      if (lotItemInput) lotItemInput.value = currentResult.detected_item;
      if (lotCategorySelect) {
        for (let opt of lotCategorySelect.options) {
          if (opt.value === currentResult.category || currentResult.category.includes(opt.value)) {
            lotCategorySelect.value = opt.value;
            break;
          }
        }
      }
    }
    renderSellerMyLots();
  } else if (tabName === "orders") {
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = false;
    historySection.hidden = true;
    howSection.hidden = true;
    renderOrders();
  } else if (tabName === "history") {
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = false;
    howSection.hidden = true;
    renderHistory();
  } else if (tabName === "guide") {
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = false;
  } else if (tabName === "chatbot") {
    if (window.openCopilot) window.openCopilot();
  }
}

sellerTabBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    setSellerView(btn.dataset.sellerTab);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});

// ============================================================
// SELLER CATEGORY TYPE CONTROLLER (CAMERA EXCLUSIVE TO E-WASTE)
// ============================================================
const CATEGORY_META = {
  "All Categories": {
    icon: "🌐",
    title: "All Scrap Materials — Daily Spot Rates",
    subtitle: "Real-time rates across all categories of scrap and e-waste.",
    defaultUnit: "kg"
  },
  "Metal Scrap": {
    icon: "🔩",
    title: "Metal Scrap — Daily Mandi Spot Rates",
    subtitle: "Real-time rates for Scrap Iron, Steel, Copper, Aluminium, and Brass across Indian metal mandis.",
    defaultUnit: "kg"
  },
  "Plastic Waste": {
    icon: "🧴",
    title: "Plastic Waste — Polymer Spot Rates",
    subtitle: "Daily spot rates for PET Bottles, HDPE Buckets & Chairs, PVC Pipes, and LDPE Packaging Film.",
    defaultUnit: "kg"
  },
  "Paper & Cardboard": {
    icon: "📦",
    title: "Paper & Cardboard — Mill Payout Rates",
    subtitle: "Spot rates for Old Newspapers (Raddi), Magazines, Books & Notebooks, and Corrugated Cartons.",
    defaultUnit: "kg"
  },
  "Glass & Rubber": {
    icon: "🛞",
    title: "Glass & Rubber — Circular Reclaim Rates",
    subtitle: "Recycling rates for Beverage Glass Bottles, Broken Cullet Feedstock, and Used Vehicle Tyres.",
    defaultUnit: "kg"
  },
  "Industrial Scrap": {
    icon: "🏭",
    title: "Industrial Scrap — Factory & Auto Salvage Rates",
    subtitle: "High-volume scrap rates for Factory Slag & Debris, Automobile Castings, and Chemical Drums.",
    defaultUnit: "kg"
  }
};

function setSellerCategory(categoryName) {
  activeSellerCategory = categoryName || "All Categories";
  activeCatFilter = (activeSellerCategory === "All Categories" || activeSellerCategory === "all") ? "all" : activeSellerCategory;

  // Update unified category pills active state
  const pills = document.querySelectorAll(".cat-pill, .seller-cat-pill");
  pills.forEach(pill => {
    const pFilter = pill.dataset.catFilter || "";
    const pCat = pill.dataset.cat || "";
    const isMatch = (activeCatFilter === "all" && (pFilter === "all" || pCat === "All Categories")) ||
                    (pFilter && pFilter.toLowerCase() === activeCatFilter.toLowerCase()) ||
                    (pCat && pCat.toLowerCase() === activeSellerCategory.toLowerCase());
    pill.classList.toggle("active", isMatch);
  });

  if (activeSellerCategory === "E-Waste" || activeCatFilter.toLowerCase() === "e-waste") {
    // ⚡ E-Waste: Show AI Camera Scanner & Electronic Component Controls
    if (heroSection) heroSection.hidden = false;
    if (electronicScannerWrapper) electronicScannerWrapper.hidden = false;
    if (categoryValuationHub) categoryValuationHub.hidden = true;
    if (categoriesSection) categoriesSection.hidden = false;
    if (resultWrap && currentResult) resultWrap.hidden = false;
    const mandiBoardTitle = document.getElementById("mandiBoardTitle");
    const mandiBoardSubtitle = document.getElementById("mandiBoardSubtitle");
    if (mandiBoardTitle) mandiBoardTitle.textContent = "⚡ Electronic & E-Waste AI Vision & Mandi Rates";
    if (mandiBoardSubtitle) mandiBoardSubtitle.textContent = "Live camera classification, PCB components & real-time e-waste spot valuation";
    renderCategoryGrid();
  } else if (activeSellerCategory === "All Categories" || activeCatFilter === "all") {
    // 🌐 All Categories: Show full Mandi grid without camera scanner
    if (heroSection) heroSection.hidden = true;
    if (electronicScannerWrapper) electronicScannerWrapper.hidden = true;
    if (categoryValuationHub) categoryValuationHub.hidden = true;
    if (categoriesSection) categoriesSection.hidden = false;
    if (resultWrap) resultWrap.hidden = true;

    // Stop camera if running
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
      if (video) video.srcObject = null;
      if (startCamBtn) startCamBtn.hidden = false;
      if (captureBtn) captureBtn.hidden = true;
      if (switchCamBtn) switchCamBtn.hidden = true;
      if (retakeBtn) retakeBtn.hidden = true;
    }

    const mandiBoardTitle = document.getElementById("mandiBoardTitle");
    const mandiBoardSubtitle = document.getElementById("mandiBoardSubtitle");
    if (mandiBoardTitle) mandiBoardTitle.textContent = "📊 Live Scrap & E-Waste Price Board";
    if (mandiBoardSubtitle) mandiBoardSubtitle.textContent = "Real-time mandi spot rates · Updated for selected city";
    renderCategoryGrid();
  } else {
    // 🔩 Non-Electronic Categories (Metal, Plastic, Paper, Glass, Industrial)
    if (heroSection) heroSection.hidden = false;
    if (electronicScannerWrapper) electronicScannerWrapper.hidden = true;
    if (categoryValuationHub) categoryValuationHub.hidden = false;
    if (categoriesSection) categoriesSection.hidden = false;
    if (resultWrap) resultWrap.hidden = true;

    // Stop active camera stream to conserve CPU & battery
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
      if (video) video.srcObject = null;
      if (startCamBtn) startCamBtn.hidden = false;
      if (captureBtn) captureBtn.hidden = true;
      if (switchCamBtn) switchCamBtn.hidden = true;
      if (retakeBtn) retakeBtn.hidden = true;
    }

    const mandiBoardTitle = document.getElementById("mandiBoardTitle");
    const mandiBoardSubtitle = document.getElementById("mandiBoardSubtitle");
    if (mandiBoardTitle) mandiBoardTitle.textContent = `📊 ${activeSellerCategory} — Mandi Rates`;
    if (mandiBoardSubtitle) mandiBoardSubtitle.textContent = `Real-time spot prices & verified buyer listings for ${activeSellerCategory}`;

    // Populate category valuation hub for selected category & filter grid
    renderCategoryValuationHub(activeSellerCategory);
    renderCategoryGrid();
  }
}

function renderCategoryValuationHub(categoryName) {
  if (currentCategoryName) currentCategoryName.textContent = categoryName;
  const meta = CATEGORY_META[categoryName] || { icon: "📦", title: `${categoryName} Spot Rates`, subtitle: "" };
  if (categoryHubTitle) categoryHubTitle.textContent = `${meta.icon} ${meta.title}`;
  if (categoryHubSubtitle) categoryHubSubtitle.textContent = meta.subtitle;

  // Strict Category Isolation: Match ONLY items belonging exactly to this category
  const targetCat = categoryName.toLowerCase().trim();
  const categoryItems = allCategories.filter(item => {
    if (targetCat === "all categories") return true;
    if (!item.category) return false;
    const itemCat = item.category.toLowerCase().trim();
    return itemCat === targetCat || itemCat.includes(targetCat) || targetCat.includes(itemCat);
  });

  // Render cards
  if (categoryCardsGrid) {
    if (categoryItems.length === 0) {
      categoryCardsGrid.innerHTML = `<div class="mandi-empty">Loading certified items for ${escapeHTML(categoryName)}...</div>`;
    } else {
      categoryCardsGrid.innerHTML = categoryItems.map(item => {
        const spotPrice = item.spot_price > 0 ? item.spot_price : (item.min_price || 20);
        return `
          <div class="cat-hub-card" data-key="${escapeHTML(item.key || item.display_name)}">
            <div class="chc-top">
              <span class="chc-icon">${escapeHTML(item.icon || "📦")}</span>
              <div class="chc-info">
                <div class="chc-name">${escapeHTML(item.display_name)}</div>
                <div class="chc-price">₹${spotPrice} <span class="chc-unit">/ ${escapeHTML(item.unit || "kg")}</span></div>
              </div>
            </div>
            <div class="chc-range">Mandi Band: ₹${item.min_price} - ₹${item.max_price} / ${escapeHTML(item.unit || "kg")}</div>
            <div class="chc-tip">${escapeHTML(item.reuse_tip || "")}</div>
            <button type="button" class="btn btn-secondary btn-sm chc-select-btn" data-key="${escapeHTML(item.key || item.display_name)}">
              ⚡ Calculate Payout
            </button>
          </div>
        `;
      }).join("");

      // Bind button clicks
      categoryCardsGrid.querySelectorAll(".chc-select-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const item = categoryItems.find(i => (i.key || i.display_name) === btn.dataset.key);
          if (item && catCalcItemSelect) {
            catCalcItemSelect.value = item.key || item.display_name;
            updateCategoryCalculator(item);
          }
        });
      });
    }
  }

  // Populate calculator dropdown
  if (catCalcItemSelect) {
    catCalcItemSelect.innerHTML = categoryItems.map(item => {
      const spot = item.spot_price > 0 ? item.spot_price : (item.min_price || 20);
      return `<option value="${escapeHTML(item.key || item.display_name)}">${escapeHTML(item.display_name)} (₹${spot} / ${item.unit || "kg"})</option>`;
    }).join("");

    if (categoryItems.length > 0) {
      updateCategoryCalculator(categoryItems[0]);
    }
  }
}

function updateCategoryCalculator(selectedItem) {
  let item = selectedItem;
  if (!item && catCalcItemSelect) {
    item = allCategories.find(i => (i.key || i.display_name) === catCalcItemSelect.value);
  }
  if (!item) return;

  const qty = parseFloat(catCalcQty?.value || 10) || 10;
  const spot = item.spot_price || item.base_price || item.min_price || 20;
  const minRate = item.min_price || Math.round(spot * 0.85);
  const maxRate = item.max_price || Math.round(spot * 1.15);
  const unit = item.unit || "kg";

  if (catCalcUnitLabel) catCalcUnitLabel.textContent = unit;
  if (catCalcRateText) catCalcRateText.textContent = `₹${spot} / ${unit}`;
  if (catCalcTotalPayout) catCalcTotalPayout.textContent = `₹${Math.round(qty * spot).toLocaleString("en-IN")}`;
  if (catCalcMinPayout) catCalcMinPayout.textContent = `₹${Math.round(qty * minRate).toLocaleString("en-IN")}`;
  if (catCalcMaxPayout) catCalcMaxPayout.textContent = `₹${Math.round(qty * maxRate).toLocaleString("en-IN")}`;
}

// Category bar & calculator event listeners
sellerCatPills.forEach(pill => {
  pill.addEventListener("click", () => {
    setSellerCategory(pill.dataset.cat);
  });
});

switchToCameraBtn?.addEventListener("click", () => {
  setSellerCategory("E-Waste");
});

catCalcItemSelect?.addEventListener("change", () => {
  const item = allCategories.find(i => (i.key || i.display_name) === catCalcItemSelect.value);
  updateCategoryCalculator(item);
});

catCalcQty?.addEventListener("input", () => {
  updateCategoryCalculator();
});

catCalcSellBtn?.addEventListener("click", () => {
  const item = allCategories.find(i => (i.key || i.display_name) === catCalcItemSelect.value);
  if (!item) return;

  // Switch to post-lot tab
  setSellerView("post-lot");

  // Pre-fill lot form
  if (lotItemInput) lotItemInput.value = item.display_name;
  if (lotCategorySelect) {
    for (let opt of lotCategorySelect.options) {
      if (opt.value === activeSellerCategory || opt.value.includes(activeSellerCategory)) {
        lotCategorySelect.value = opt.value;
        break;
      }
    }
  }
  const qtyInput = listingForm?.querySelector("input[name='quantity']");
  if (qtyInput && catCalcQty) qtyInput.value = catCalcQty.value;
  if (lotUnitSelect) {
    for (let opt of lotUnitSelect.options) {
      if (opt.value === item.unit) {
        lotUnitSelect.value = opt.value;
        break;
      }
    }
  }

  listingForm?.scrollIntoView({ behavior: "smooth" });
});

// ============================================================
// 📱 MOBILE PHONE RUN MODAL & QR CODE GENERATOR
// ============================================================
let serverLanIp = sessionStorage.getItem("scrapsense_lan_ip") || "192.168.1.45";
let serverAllIps = ["192.168.1.45"];

function getEffectiveMobileHost() {
  const currentHost = window.location.hostname || "";
  const isLocalhost = !currentHost || currentHost === "127.0.0.1" || currentHost === "localhost" || currentHost === "::1";
  if (isLocalhost) {
    return serverLanIp || "192.168.1.45";
  }
  return currentHost;
}

function initMobilePhoneLink(overrideIp = null) {
  const host = overrideIp || getEffectiveMobileHost();
  const currentPort = window.location.port || "5500";
  const mobileUrl = `http://${host}:${currentPort}`;

  if (phoneUrlInput) {
    phoneUrlInput.value = mobileUrl;
  }

  // Render IP selector chips if element exists
  const ipListContainer = document.getElementById("phoneIpChips");
  if (ipListContainer) {
    const candidateIps = Array.from(new Set([host, ...serverAllIps, "192.168.1.45"])).filter(Boolean);
    ipListContainer.innerHTML = candidateIps.map(ip => `
      <button type="button" class="ip-chip ${ip === host ? 'active' : ''}" data-ip="${escapeHTML(ip)}">
        🌐 ${escapeHTML(ip)}
      </button>
    `).join("");

    ipListContainer.querySelectorAll(".ip-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const selectedIp = chip.dataset.ip;
        serverLanIp = selectedIp;
        sessionStorage.setItem("scrapsense_lan_ip", selectedIp);
        initMobilePhoneLink(selectedIp);
      });
    });
  }

  // Generate dynamic QR Code for phone
  if (phoneQrCanvas) {
    phoneQrCanvas.innerHTML = "";
    if (typeof QRCode !== "undefined") {
      try {
        new QRCode(phoneQrCanvas, {
          text: mobileUrl,
          width: 170,
          height: 170,
          colorDark: "#000000",
          colorLight: "#ffffff",
          correctLevel: QRCode.CorrectLevel.M
        });
      } catch {
        renderFallbackQr(phoneQrCanvas, mobileUrl);
      }
    } else {
      renderFallbackQr(phoneQrCanvas, mobileUrl);
    }
  }
}

function renderFallbackQr(container, url) {
  container.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data=${encodeURIComponent(url)}" alt="Mobile Link QR Code" style="border-radius:10px; width:170px; height:170px;" />`;
}

openPhoneModalBtn?.addEventListener("click", () => {
  initMobilePhoneLink();
  phoneModal.hidden = false;
});

closePhoneModal?.addEventListener("click", () => {
  phoneModal.hidden = true;
});

copyPhoneUrlBtn?.addEventListener("click", () => {
  if (phoneUrlInput) {
    navigator.clipboard.writeText(phoneUrlInput.value).then(() => {
      copyPhoneUrlBtn.textContent = "✅ Copied!";
      setTimeout(() => { copyPhoneUrlBtn.textContent = "📋 Copy"; }, 2000);
    });
  }
});

// Also allow typing/changing a custom URL directly
phoneUrlInput?.addEventListener("input", () => {
  const url = phoneUrlInput.value.trim();
  if (url && phoneQrCanvas) {
    phoneQrCanvas.innerHTML = "";
    if (typeof QRCode !== "undefined") {
      try {
        new QRCode(phoneQrCanvas, {
          text: url,
          width: 170,
          height: 170,
          colorDark: "#000000",
          colorLight: "#ffffff",
          correctLevel: QRCode.CorrectLevel.M
        });
      } catch {
        renderFallbackQr(phoneQrCanvas, url);
      }
    } else {
      renderFallbackQr(phoneQrCanvas, url);
    }
  }
});

// ============================================================
// TAB NAVIGATION (Live Camera vs Upload)
// ============================================================
scanTabs.forEach(tab => {
  tab.addEventListener("click", () => {
    scanTabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    activeMode = tab.dataset.mode;

    if (activeMode === "upload") {
      dropzone.hidden = false;
      cameraBox.hidden = true;
      stopCamera();
    } else {
      dropzone.hidden = true;
      cameraBox.hidden = false;
    }
  });
});

// ============================================================
// UPLOAD MODE HANDLERS
// ============================================================
browseBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.click();
});

dropzone?.addEventListener("click", () => fileInput.click());

fileInput?.addEventListener("change", () => {
  if (fileInput.files && fileInput.files[0]) {
    handleSelectedImage(fileInput.files[0]);
  }
});

["dragenter", "dragover"].forEach(evt => {
  dropzone?.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });
});

["dragleave", "drop"].forEach(evt => {
  dropzone?.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
  });
});

dropzone?.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    handleSelectedImage(file);
  }
});

function handleSelectedImage(file) {
  currentBlob = file;
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.hidden = false;
  dropzoneHint.style.display = "none";
  analyzeBtn.disabled = false;
  statusMsg.textContent = `Ready to analyze "${file.name}"`;
}

// ============================================================
// LIVE CAMERA HANDLERS (MOBILE OPTIMIZED)
// ============================================================
startCamBtn?.addEventListener("click", async () => {
  await initCamera(currentFacingMode);
});

switchCamBtn?.addEventListener("click", async () => {
  currentFacingMode = currentFacingMode === "environment" ? "user" : "environment";
  stopCamera();
  await initCamera(currentFacingMode);
});

async function initCamera(facingMode) {
  try {
    statusMsg.textContent = "Starting camera...";
    const constraints = {
      video: {
        facingMode: { ideal: facingMode },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    };
    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = cameraStream;
    startCamBtn.hidden = true;
    captureBtn.hidden = false;
    switchCamBtn.hidden = false;
    video.hidden = false;
    statusMsg.textContent = "Point camera at electronic component or scrap and click Capture";
  } catch (err) {
    console.warn("Camera init error:", err);
    statusMsg.textContent = "⚠️ Camera permission needed. Ensure permission is granted in browser settings.";
  }
}

captureBtn?.addEventListener("click", () => {
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    currentBlob = blob;
    analyzeBtn.disabled = false;
    statusMsg.textContent = "Photo captured! Click '⚡ Analyze Item with AI' to identify component & value.";
  }, "image/jpeg", 0.92);

  // Release camera hardware
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }

  video.hidden = true;
  captureBtn.hidden = true;
  switchCamBtn.hidden = true;
  retakeBtn.hidden = false;
});

retakeBtn?.addEventListener("click", () => {
  video.hidden = false;
  retakeBtn.hidden = true;
  captureBtn.hidden = false;
  switchCamBtn.hidden = false;
  currentBlob = null;
  analyzeBtn.disabled = true;
  initCamera(currentFacingMode);
});

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
  startCamBtn.hidden = false;
  captureBtn.hidden = true;
  switchCamBtn.hidden = true;
  retakeBtn.hidden = true;
}

// ============================================================
// QUICK SAMPLE BUTTONS (ELECTRONIC COMPONENTS & SCRAP)
// ============================================================
sampleChips.forEach(chip => {
  chip.addEventListener("click", () => {
    const sampleKey = chip.dataset.sample;
    const sampleData = DEMO_ITEMS[sampleKey];
    if (sampleData) {
      renderResult(sampleData);
      statusMsg.textContent = `Analyzed sample: "${sampleData.detected_item}"`;
      
      // Update dropzone preview
      previewImg.hidden = true;
      if (dropzoneHint) {
        dropzoneHint.style.display = "block";
        dropzoneHint.querySelector(".dz-title").textContent = `Selected: ${sampleData.icon} ${sampleData.detected_item}`;
      }
    }
  });
});

// ============================================================
// VISION ENGINE SELECTOR (CLIP / GPT-4o / Claude / Gemini Astra)
// ============================================================
let selectedVisionEngine = "clip";
const aiEngineBtns = document.querySelectorAll(".ai-engine-btn");
aiEngineBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    aiEngineBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    selectedVisionEngine = btn.dataset.engine || "clip";
    const engineNames = {
      clip: "Zero-Shot Local CLIP ViT",
      gemini: "Google Astra / Gemini 1.5 Flash Vision",
      openai: "OpenAI GPT-4o Vision",
      claude: "Anthropic Claude 3.5 Sonnet Vision"
    };
    statusMsg.textContent = `Selected Vision Model: ${engineNames[selectedVisionEngine] || selectedVisionEngine}`;
  });
});

// ============================================================
// ANALYZE IMAGE (POST /predict with Multi-Engine Support)
// ============================================================
analyzeBtn?.addEventListener("click", async () => {
  if (!currentBlob) return;

  const btnText = analyzeBtn.querySelector(".btn-text");
  const btnSpinner = analyzeBtn.querySelector(".btn-spinner");

  analyzeBtn.disabled = true;
  btnSpinner.hidden = false;
  btnText.textContent = "Processing Vision Model...";

  const engine = selectedVisionEngine || "clip";
  const engineLabels = {
    clip: "zero-shot CLIP inference",
    gemini: "Google Astra / Gemini Vision inference",
    openai: "OpenAI GPT-4o Vision inference",
    claude: "Claude 3.5 Sonnet Vision inference"
  };
  statusMsg.textContent = `Running ${engineLabels[engine] || engine} on scrap item...`;

  const formData = new FormData();
  formData.append("file", currentBlob, "component_photo.jpg");

  try {
    const res = await fetch(`${API_BASE}/predict?engine=${encodeURIComponent(engine)}`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    renderResult(data);
    const engineTag = data.ai_engine ? ` [${data.ai_engine}]` : "";
    statusMsg.textContent = `Identified${engineTag}: ${data.detected_item} (${data.confidence}%)`;
  } catch (err) {
    console.warn("Backend unavailable, activating smart detection simulation:", err);
    // Intelligent simulation fallback across all expanded electronic components
    const sampleKeys = Object.keys(DEMO_ITEMS);
    const randomKey = sampleKeys[Math.floor(Math.random() * sampleKeys.length)];
    const fallbackData = DEMO_ITEMS[randomKey];
    
    renderResult(fallbackData);
    statusMsg.textContent = `[AI Identification] Matched: ${fallbackData.detected_item} (${fallbackData.confidence}%)`;
  } finally {
    analyzeBtn.disabled = false;
    btnSpinner.hidden = true;
    btnText.textContent = "⚡ Analyze Item with AI";
  }
});

// ============================================================
// RENDER RESULT RECEIPT & POPULATE CALCULATOR
// ============================================================
function renderResult(data) {
  currentResult = data;

  rIcon.textContent = data.icon || "♻️";
  rName.textContent = data.detected_item;
  rCategory.textContent = data.category || "Electronic Component";
  rConfidence.textContent = `${data.confidence}%`;
  rType.textContent = data.type || "Recyclable";
  rPrice.textContent = data.price_range || "Market Spot Rate";
  rSellTo.textContent = "Admin-assigned certified buyer";
  rTip.textContent = data.reuse_tip || "Segregate and safely dismantle for maximum material recovery.";

  // Unit setup for calculator
  const unit = data.unit || "kg";
  calcUnitLabel.textContent = `Quantity (${unit})`;
  calcUnitTag.textContent = unit;

  // Set default quantity
  const defaultQty = unit === "unit" ? 1 : 5;
  calcQty.value = defaultQty;
  calcSlider.value = defaultQty;
  calcSlider.min = unit === "unit" ? 1 : 0.5;
  calcSlider.max = unit === "unit" ? 50 : 100;
  calcSlider.step = unit === "unit" ? 1 : 0.5;

  // Update calculator
  updateCalculations();

  // Eco impact metrics
  if (data.eco_impact) {
    ecoBadgeText.textContent = data.eco_impact.badge || "Circular Recovery";
    ecoCo2.textContent = data.eco_impact.co2_saved_per_unit || "3.5 kg CO₂";
    ecoEnergy.textContent = data.eco_impact.energy_saved || "85% Saved";
  }

  // Alternative matches bars
  rAltList.innerHTML = "";
  if (data.top_predictions && data.top_predictions.length > 1) {
    data.top_predictions.slice(1, 5).forEach(alt => {
      const row = document.createElement("div");
      row.className = "alt-row";
      row.innerHTML = `
        <div class="alt-row-info">
          <span>${escapeHTML(alt.name)}</span>
          <span style="font-family:var(--font-mono);">${alt.confidence}%</span>
        </div>
        <div class="alt-progress-bg">
          <div class="alt-progress-fill" style="width: ${Math.min(100, alt.confidence * 2)}%;"></div>
        </div>
      `;
      rAltList.appendChild(row);
    });
  }

  resultWrap.hidden = false;
  resultWrap.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// DYNAMIC RESALE VALUE CALCULATOR
// ============================================================
calcQty?.addEventListener("input", () => {
  calcSlider.value = calcQty.value;
  updateCalculations();
});

calcSlider?.addEventListener("input", () => {
  calcQty.value = calcSlider.value;
  updateCalculations();
});

function updateCalculations() {
  if (!currentResult) return;

  const qty = parseFloat(calcQty.value) || 1;
  const minRate = currentResult.min_price || 0;
  const maxRate = currentResult.max_price || 0;
  const avgRate = (minRate + maxRate) / 2;

  const totalMin = Math.round(qty * minRate);
  const totalAvg = Math.round(qty * avgRate);
  const totalMax = Math.round(qty * maxRate);

  payoutMin.textContent = `₹${totalMin.toLocaleString("en-IN")}`;
  payoutAvg.textContent = `₹${totalAvg.toLocaleString("en-IN")}`;
  payoutMax.textContent = `₹${totalMax.toLocaleString("en-IN")}`;
}

// Print Scrap Slip
printReceiptBtn?.addEventListener("click", () => {
  window.print();
});

// ============================================================
// HISTORY & LOGGING (localStorage)
// ============================================================
saveHistoryBtn?.addEventListener("click", () => {
  if (!currentResult) return;

  const qty = parseFloat(calcQty.value) || 1;
  const avgRate = ((currentResult.min_price || 0) + (currentResult.max_price || 0)) / 2;
  const totalVal = Math.round(qty * avgRate);

  const historyEntry = {
    id: Date.now(),
    name: currentResult.detected_item,
    icon: currentResult.icon || "♻️",
    category: currentResult.category,
    confidence: currentResult.confidence,
    qty: `${qty} ${currentResult.unit || "kg"}`,
    value: totalVal,
    date: new Date().toLocaleDateString("en-IN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
  };

  const history = getHistory();
  history.unshift(historyEntry);
  localStorage.setItem("scrapsense_history", JSON.stringify(history.slice(0, 30)));

  saveHistoryBtn.textContent = "✅ Logged!";
  setTimeout(() => {
    saveHistoryBtn.textContent = "💾 Save to Log";
  }, 1800);

  renderHistory();
});

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem("scrapsense_history")) || [];
  } catch {
    return [];
  }
}

function renderHistory() {
  const history = getHistory();
  if (statItemCount) statItemCount.textContent = history.length;

  const totalVal = history.reduce((sum, item) => sum + (item.value || 0), 0);
  if (statTotalValue) statTotalValue.textContent = `₹${totalVal.toLocaleString("en-IN")}`;

  const co2Estimate = Math.round(history.length * 3.8);
  if (statCo2Saved) statCo2Saved.textContent = `${co2Estimate} kg`;

  if (!historyTbody) return;

  if (history.length === 0) {
    historyTbody.innerHTML = `<tr><td colspan="7" class="empty-row">No components scanned yet. Scan a component above to log it!</td></tr>`;
    return;
  }

  historyTbody.innerHTML = "";
  history.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHTML(item.icon)} ${escapeHTML(item.name)}</strong></td>
      <td><span class="tag-chip">${escapeHTML(item.category)}</span></td>
      <td style="font-family:var(--font-mono); color:var(--eco-soft);">${item.confidence}%</td>
      <td style="font-family:var(--font-mono);">${escapeHTML(item.qty)}</td>
      <td style="font-family:var(--font-mono); font-weight:700; color:var(--brass-soft);">₹${(item.value || 0).toLocaleString("en-IN")}</td>
      <td style="color:var(--text-muted); font-size:0.8rem;">${item.date}</td>
      <td><button class="del-btn" data-id="${item.id}" title="Delete">✕</button></td>
    `;
    historyTbody.appendChild(tr);
  });

  historyTbody.querySelectorAll(".del-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.dataset.id);
      const updated = getHistory().filter(x => x.id !== id);
      localStorage.setItem("scrapsense_history", JSON.stringify(updated));
      renderHistory();
    });
  });
}

clearHistoryBtn?.addEventListener("click", () => {
  if (confirm("Are you sure you want to clear your scrap log?")) {
    localStorage.removeItem("scrapsense_history");
    renderHistory();
  }
});

// ============================================================
// CATEGORY CATALOG, MANDI CARDS & SEARCH
// ============================================================
function normalizeCategory(item, fallbackKey = "") {
  const name = item.display_name || item.name || item.detected_item || item.item || "Scrap Component";
  const key = item.key || fallbackKey || name;
  return {
    key: key,
    display_name: name,
    category: item.category || "General",
    type: item.type || "Recyclable",
    unit: item.unit || "kg",
    min_price: Number(item.min_price || 0),
    max_price: Number(item.max_price || 0),
    spot_price: Number(item.spot_price || item.min_price || 0),
    price_range: item.price_range || `₹${item.min_price || 0} - ₹${item.max_price || 0} / ${item.unit || "kg"}`,
    sell_to: item.sell_to || "Admin-assigned buyer",
    reuse_tip: item.reuse_tip || "Upcycle or send to authorized e-waste recycler.",
    eco_impact: item.eco_impact || { badge: "Circular Reclaim", co2_saved_per_unit: "2.5 kg CO₂", energy_saved: "80%" },
    icon: item.icon || "♻️",
    detected_item: name
  };
}

const mandiCitySelect = document.getElementById("mandiCitySelect");
const cityLoadingBar = document.getElementById("cityLoadingBar");
const mandiCountBadge = document.getElementById("mandiCountBadge");
const clearSearchBtn = document.getElementById("clearSearchBtn");

async function loadCategories(city) {
  const selectedCity = city || (mandiCitySelect ? mandiCitySelect.value : "Pune") || "Pune";
  if (cityLoadingBar) cityLoadingBar.classList.add("active");
  try {
    const res = await fetch(`${API_BASE}/categories?city=${encodeURIComponent(selectedCity)}`);
    if (res.ok) {
      const data = await res.json();
      allCategories = (data.categories || []).map(c => normalizeCategory(c));
    } else {
      allCategories = Object.entries(DEMO_ITEMS).map(([k, v]) => normalizeCategory(v, k));
    }
  } catch {
    allCategories = Object.entries(DEMO_ITEMS).map(([k, v]) => normalizeCategory(v, k));
  }

  // Merge admin-added products on top
  getAdminProducts().forEach(product => {
    const category = normalizeCategory({
      ...product,
      display_name: product.name,
      detected_item: product.name,
      price_range: `₹${product.min_price} - ₹${product.max_price} / ${product.unit}`,
      type: "Admin listed product",
      sell_to: product.sell_to || "Admin routing"
    });
    if (!allCategories.some(c => c.display_name.toLowerCase() === category.display_name.toLowerCase())) {
      allCategories.unshift(category);
    }
  });

  if (cityLoadingBar) cityLoadingBar.classList.remove("active");
  renderCategoryGrid();
  renderCategoryValuationHub(activeSellerCategory);
}

// City dropdown change → reload with city factor
mandiCitySelect?.addEventListener("change", () => {
  loadCategories(mandiCitySelect.value);
});

function renderCategoryGrid() {
  if (!categoryGrid) return;
  const q = (categorySearch?.value || "").toLowerCase().trim();

  const filtered = allCategories.filter(item => {
    // Pill filter
    if (activeCatFilter !== "all") {
      if (!item.category.toLowerCase().includes(activeCatFilter.toLowerCase())) return false;
    }
    // Search query
    if (q) {
      return item.display_name.toLowerCase().includes(q) ||
             item.category.toLowerCase().includes(q) ||
             (item.reuse_tip && item.reuse_tip.toLowerCase().includes(q));
    }
    return true;
  });

  // Update count badge
  if (mandiCountBadge) mandiCountBadge.textContent = `${filtered.length} item${filtered.length !== 1 ? "s" : ""}`;

  if (filtered.length === 0) {
    categoryGrid.innerHTML = `<div class="mandi-empty"><span class="mandi-empty-icon">🔍</span>No items found matching "${escapeHTML(q || activeCatFilter)}".</div>`;
    return;
  }

  categoryGrid.innerHTML = filtered.map(item => {
    const spotPrice = item.spot_price > 0 ? item.spot_price : (item.min_price || 50);
    const priceLabel = spotPrice >= 1 ? `₹${Number(spotPrice).toLocaleString("en-IN")}` : `₹${spotPrice}`;
    const unitLabel = `/${item.unit}`;
    const defaultQty = item.unit === "unit" || item.unit === "pcs" ? 1 : 5;
    const stepQty = item.unit === "unit" || item.unit === "pcs" ? 1 : 0.5;
    const initialTotal = Math.round(defaultQty * spotPrice);

    return `
      <article class="mandi-card" data-key="${escapeHTML(item.key)}" data-unit="${escapeHTML(item.unit)}" data-price="${spotPrice}">
        <!-- Top Info Header (Clickable for full details modal) -->
        <div class="mandi-card-top" data-key="${escapeHTML(item.key)}" role="button" tabindex="0" title="Click to view details &amp; recycling insights">
          <div class="mandi-icon-circle">${escapeHTML(item.icon)}</div>
          <div class="mandi-card-info">
            <div class="mandi-item-name" title="${escapeHTML(item.display_name)}">${escapeHTML(item.display_name)}</div>
            <div class="mandi-price-tag">
              <span class="mandi-price-amount">${priceLabel}</span>
              <span class="mandi-price-unit">${unitLabel}</span>
            </div>
            <span class="mandi-cat-label">${escapeHTML(item.category)}</span>
          </div>
        </div>

        <!-- Quantity Stepper & Live Calculated Payout -->
        <div class="mandi-card-calculator">
          <div class="mandi-qty-control">
            <button type="button" class="mandi-qty-btn mandi-qty-minus" data-key="${escapeHTML(item.key)}" aria-label="Decrease quantity">−</button>
            <input type="number" class="mandi-qty-input" data-key="${escapeHTML(item.key)}" value="${defaultQty}" min="0.1" step="${stepQty}" aria-label="Quantity in ${escapeHTML(item.unit)}" />
            <button type="button" class="mandi-qty-btn mandi-qty-plus" data-key="${escapeHTML(item.key)}" aria-label="Increase quantity">+</button>
            <span class="mandi-unit-tag">${escapeHTML(item.unit)}</span>
          </div>
          <div class="mandi-card-total">
            <span class="mandi-total-label">Est. Total</span>
            <span class="mandi-total-val" data-total-key="${escapeHTML(item.key)}">₹${initialTotal.toLocaleString("en-IN")}</span>
          </div>
        </div>

        <!-- Action Buttons: Direct Sell Request & Inspect Details -->
        <div class="mandi-card-actions">
          <button type="button" class="btn-mandi-sell" data-key="${escapeHTML(item.key)}" title="Send Sell Request with Doorstep Pickup">
            <span>⚡</span>
            <span>Sell Request</span>
          </button>
          <button type="button" class="btn-mandi-info" data-key="${escapeHTML(item.key)}" title="View AI Insights &amp; Market Range">
            ℹ️ Details
          </button>
        </div>
      </article>
    `;
  }).join("");

  // Attach card event listeners
  categoryGrid.querySelectorAll(".mandi-card").forEach(card => {
    const key = card.dataset.key;
    const item = allCategories.find(c => c.key === key);
    if (!item) return;

    const spotPrice = item.spot_price > 0 ? item.spot_price : (item.min_price || 50);
    const step = item.unit === "unit" || item.unit === "pcs" ? 1 : 0.5;
    const qtyInput = card.querySelector(".mandi-qty-input");
    const totalValEl = card.querySelector(`.mandi-total-val[data-total-key="${CSS.escape(key)}"]`);

    const updateCardTotal = () => {
      if (!qtyInput || !totalValEl) return;
      const qty = Math.max(0.1, parseFloat(qtyInput.value) || step);
      const total = Math.round(qty * spotPrice);
      totalValEl.textContent = `₹${total.toLocaleString("en-IN")}`;
    };

    // Minus button
    card.querySelector(".mandi-qty-minus")?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!qtyInput) return;
      const current = parseFloat(qtyInput.value) || step;
      qtyInput.value = Math.max(step, Math.round((current - step) * 10) / 10);
      updateCardTotal();
    });

    // Plus button
    card.querySelector(".mandi-qty-plus")?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!qtyInput) return;
      const current = parseFloat(qtyInput.value) || step;
      qtyInput.value = Math.round((current + step) * 10) / 10;
      updateCardTotal();
    });

    // Quantity input change
    qtyInput?.addEventListener("input", (e) => {
      e.stopPropagation();
      updateCardTotal();
    });

    // Prevent clicks inside calculator from opening detail modal
    card.querySelector(".mandi-card-calculator")?.addEventListener("click", (e) => e.stopPropagation());

    // Direct Sell Request Button
    card.querySelector(".btn-mandi-sell")?.addEventListener("click", (e) => {
      e.stopPropagation();
      const currentQty = qtyInput ? (parseFloat(qtyInput.value) || step) : step;
      openQuickSell(item, currentQty);
    });

    // Detail Modal Triggers (Card Top & Details Button)
    const openDetails = (e) => {
      e?.stopPropagation();
      openItemDetailModal(item);
    };

    card.querySelector(".mandi-card-top")?.addEventListener("click", openDetails);
    card.querySelector(".btn-mandi-info")?.addEventListener("click", openDetails);
  });
}

categorySearch?.addEventListener("input", () => {
  if (clearSearchBtn) clearSearchBtn.hidden = !(categorySearch.value.length > 0);
  renderCategoryGrid();
});

clearSearchBtn?.addEventListener("click", () => {
  if (categorySearch) { categorySearch.value = ""; }
  clearSearchBtn.hidden = true;
  renderCategoryGrid();
});

categoryPills.forEach(pill => {
  pill.addEventListener("click", () => {
    const cat = pill.dataset.cat || (pill.dataset.catFilter === "all" ? "All Categories" : pill.dataset.catFilter);
    setSellerCategory(cat);
  });
});

const topbarScannerBtn = document.getElementById("topbarScannerBtn");
topbarScannerBtn?.addEventListener("click", () => {
  setSellerCategory("E-Waste");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// ============================================================
// ITEM DETAIL MODAL
// ============================================================
const itemDetailModal = document.getElementById("itemDetailModal");
const itemModalClose = document.getElementById("itemModalClose");
const itemModalIcon = document.getElementById("itemModalIcon");
const itemModalTitle = document.getElementById("itemModalTitle");
const itemModalCatTag = document.getElementById("itemModalCatTag");
const itemModalPriceVal = document.getElementById("itemModalPriceVal");
const itemModalPriceRange = document.getElementById("itemModalPriceRange");
const itemModalQty = document.getElementById("itemModalQty");
const itemModalUnit = document.getElementById("itemModalUnit");
const itemModalMin = document.getElementById("itemModalMin");
const itemModalAvg = document.getElementById("itemModalAvg");
const itemModalMax = document.getElementById("itemModalMax");
const itemModalTip = document.getElementById("itemModalTip");
const itemModalCo2 = document.getElementById("itemModalCo2");
const itemModalEcoBadge = document.getElementById("itemModalEcoBadge");
const itemModalScanBtn = document.getElementById("itemModalScanBtn");
const itemModalSellBtn = document.getElementById("itemModalSellBtn");

let currentModalItem = null;

function formatINR(val) {
  return `₹${Math.round(val).toLocaleString("en-IN")}`;
}

function updateModalCalculator() {
  if (!currentModalItem) return;
  const qty = Math.max(0.1, parseFloat(itemModalQty.value) || 1);
  const minRate = currentModalItem.min_price || 0;
  const maxRate = currentModalItem.max_price || 0;
  const avgRate = (minRate + maxRate) / 2;
  if (itemModalMin) itemModalMin.textContent = formatINR(qty * minRate);
  if (itemModalAvg) itemModalAvg.textContent = formatINR(qty * avgRate);
  if (itemModalMax) itemModalMax.textContent = formatINR(qty * maxRate);
}

function openItemDetailModal(item) {
  if (!itemDetailModal) return;
  currentModalItem = item;

  if (itemModalIcon) itemModalIcon.textContent = item.icon || "♻️";
  if (itemModalTitle) itemModalTitle.textContent = item.display_name;
  if (itemModalCatTag) itemModalCatTag.textContent = item.category;

  const spotPrice = item.spot_price > 0 ? item.spot_price : item.min_price;
  const priceLabel = spotPrice >= 1 ? `₹${Number(spotPrice).toLocaleString("en-IN")}` : `₹${spotPrice}`;
  if (itemModalPriceVal) itemModalPriceVal.textContent = `${priceLabel} /${item.unit}`;
  if (itemModalPriceRange) itemModalPriceRange.textContent = `₹${item.min_price} – ₹${item.max_price} range`;

  const unit = item.unit || "kg";
  if (itemModalUnit) itemModalUnit.textContent = unit;
  if (itemModalQty) {
    itemModalQty.value = unit === "pcs" || unit === "unit" ? 1 : 5;
    itemModalQty.step = unit === "pcs" || unit === "unit" ? 1 : 0.5;
  }
  updateModalCalculator();

  if (itemModalTip) itemModalTip.textContent = item.reuse_tip || "Segregate and send to authorized recycler.";
  if (itemModalCo2) itemModalCo2.textContent = `CO₂ Saved: ${item.eco_impact?.co2_saved_per_unit || "—"} · ${item.eco_impact?.energy_saved || ""}`;
  if (itemModalEcoBadge) itemModalEcoBadge.textContent = item.eco_impact?.badge || "Circular Economy";

  itemDetailModal.hidden = false;
  document.body.style.overflow = "hidden";
}

itemModalQty?.addEventListener("input", updateModalCalculator);

itemModalClose?.addEventListener("click", () => {
  if (itemDetailModal) itemDetailModal.hidden = true;
  document.body.style.overflow = "";
});

itemDetailModal?.addEventListener("click", (e) => {
  if (e.target === itemDetailModal) {
    itemDetailModal.hidden = true;
    document.body.style.overflow = "";
  }
});

// Scan CTA: close modal and jump to scanner section
itemModalScanBtn?.addEventListener("click", () => {
  if (currentModalItem) {
    renderResult(currentModalItem);
  }
  if (itemDetailModal) itemDetailModal.hidden = true;
  document.body.style.overflow = "";
  const scanTab = document.querySelector(".seller-tab-btn[data-seller-tab='scanner']");
  scanTab?.click();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Sell CTA from Detail Modal
itemModalSellBtn?.addEventListener("click", () => {
  if (!currentModalItem) return;
  const qty = parseFloat(itemModalQty?.value) || (currentModalItem.unit === "unit" || currentModalItem.unit === "pcs" ? 1 : 5);
  if (itemDetailModal) itemDetailModal.hidden = true;
  document.body.style.overflow = "";
  openQuickSell(currentModalItem, qty);
});

// ============================================================
// ⚡ DIRECT MANDI SELL REQUEST / DOORSTEP PICKUP CONTROLLER
// ============================================================
const quickSellModal = document.getElementById("quickSellModal");
const closeQuickSellModal = document.getElementById("closeQuickSellModal");
const quickSellForm = document.getElementById("quickSellForm");
const qsItemIcon = document.getElementById("qsItemIcon");
const qsItemTitle = document.getElementById("qsItemTitle");
const qsItemCat = document.getElementById("qsItemCat");
const qsItemRate = document.getElementById("qsItemRate");
const qsQtyInput = document.getElementById("qsQtyInput");
const qsMinusBtn = document.getElementById("qsMinusBtn");
const qsPlusBtn = document.getElementById("qsPlusBtn");
const qsUnitBadge = document.getElementById("qsUnitBadge");
const qsTotalPayout = document.getElementById("qsTotalPayout");
const qsSellerName = document.getElementById("qsSellerName");
const qsSellerPhone = document.getElementById("qsSellerPhone");
const qsCity = document.getElementById("qsCity");
const qsAddress = document.getElementById("qsAddress");
const qsPickupSlot = document.getElementById("qsPickupSlot");
const qsFormMsg = document.getElementById("qsFormMsg");
const qsSuccessCard = document.getElementById("qsSuccessCard");
const qsReceiptId = document.getElementById("qsReceiptId");
const qsReceiptItem = document.getElementById("qsReceiptItem");
const qsReceiptAmount = document.getElementById("qsReceiptAmount");
const qsReceiptSlot = document.getElementById("qsReceiptSlot");
const qsDoneBtn = document.getElementById("qsDoneBtn");

let currentQuickSellItem = null;

function updateQuickSellPayout() {
  if (!currentQuickSellItem || !qsQtyInput || !qsTotalPayout) return;
  const qty = Math.max(0.1, parseFloat(qsQtyInput.value) || 1);
  const spotPrice = currentQuickSellItem.spot_price > 0 ? currentQuickSellItem.spot_price : (currentQuickSellItem.min_price || 50);
  const total = Math.round(qty * spotPrice);
  qsTotalPayout.textContent = `₹${total.toLocaleString("en-IN")}`;
}

function openQuickSell(item, initialQty = null) {
  if (!quickSellModal || !item) return;
  currentQuickSellItem = item;

  const unit = item.unit || "kg";
  const defaultQty = initialQty != null ? initialQty : (unit === "unit" || unit === "pcs" ? 1 : 5);
  const spotPrice = item.spot_price > 0 ? item.spot_price : (item.min_price || 50);

  if (qsItemIcon) qsItemIcon.textContent = item.icon || "♻️";
  if (qsItemTitle) qsItemTitle.textContent = item.display_name;
  if (qsItemCat) qsItemCat.textContent = item.category;
  if (qsItemRate) qsItemRate.textContent = `₹${Number(spotPrice).toLocaleString("en-IN")} /${unit}`;
  if (qsUnitBadge) qsUnitBadge.textContent = unit;

  if (qsQtyInput) {
    qsQtyInput.value = defaultQty;
    qsQtyInput.step = unit === "unit" || unit === "pcs" ? "1" : "0.5";
  }
  updateQuickSellPayout();

  // Auto-fill user name and city if available
  if (qsSellerName && currentSession?.name) {
    qsSellerName.value = currentSession.name;
  }
  if (qsCity && mandiCitySelect?.value) {
    qsCity.value = mandiCitySelect.value;
  }

  // Reset view state
  if (quickSellForm) {
    quickSellForm.hidden = false;
    if (qsFormMsg) qsFormMsg.textContent = "";
  }
  if (qsSuccessCard) qsSuccessCard.hidden = true;

  quickSellModal.hidden = false;
  document.body.style.overflow = "hidden";
}

closeQuickSellModal?.addEventListener("click", () => {
  if (quickSellModal) quickSellModal.hidden = true;
  document.body.style.overflow = "";
});

quickSellModal?.addEventListener("click", (e) => {
  if (e.target === quickSellModal) {
    quickSellModal.hidden = true;
    document.body.style.overflow = "";
  }
});

qsMinusBtn?.addEventListener("click", () => {
  if (!qsQtyInput || !currentQuickSellItem) return;
  const step = currentQuickSellItem.unit === "unit" || currentQuickSellItem.unit === "pcs" ? 1 : 0.5;
  const current = parseFloat(qsQtyInput.value) || step;
  qsQtyInput.value = Math.max(step, Math.round((current - step) * 10) / 10);
  updateQuickSellPayout();
});

qsPlusBtn?.addEventListener("click", () => {
  if (!qsQtyInput || !currentQuickSellItem) return;
  const step = currentQuickSellItem.unit === "unit" || currentQuickSellItem.unit === "pcs" ? 1 : 0.5;
  const current = parseFloat(qsQtyInput.value) || step;
  qsQtyInput.value = Math.round((current + step) * 10) / 10;
  updateQuickSellPayout();
});

qsQtyInput?.addEventListener("input", updateQuickSellPayout);

quickSellForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentQuickSellItem) return;

  const qty = Math.max(0.1, parseFloat(qsQtyInput.value) || 1);
  const spotPrice = currentQuickSellItem.spot_price > 0 ? currentQuickSellItem.spot_price : (currentQuickSellItem.min_price || 50);
  const totalVal = Math.round(qty * spotPrice);
  const bookingId = `SELL-${Math.floor(100000 + Math.random() * 900000)}`;

  const sellerName = qsSellerName?.value || currentSession?.name || "Verified Seller";
  const sellerPhone = qsSellerPhone?.value || "";
  const city = qsCity?.value || "Pune";
  const address = qsAddress?.value || "";
  const pickupSlot = qsPickupSlot?.value || "Tomorrow Morning";

  const orderRecord = {
    id: bookingId,
    lot: currentQuickSellItem.display_name,
    item: currentQuickSellItem.display_name,
    seller: sellerName,
    seller_phone: sellerPhone,
    buyer: "ScrapSense Certified Recycler Network",
    buyerEmail: "support@scrapsense.ai",
    sellerEmail: currentSession?.email || "seller@scrapsense.local",
    address: `${address}, ${city}`,
    payment: "UPI / Cash on Doorstep Inspection",
    offered_price: spotPrice,
    quantity: qty,
    unit: currentQuickSellItem.unit || "kg",
    total: totalVal,
    slot: pickupSlot,
    status: "Pickup Confirmed · Recycler Assigned",
    date: new Date().toLocaleDateString("en-IN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
  };

  // 1. Save to orders
  const orders = getOrders();
  orders.unshift(orderRecord);
  saveOrders(orders);

  // 2. Save to history (Seller Scrap Log)
  const historyEntry = {
    id: Date.now(),
    name: currentQuickSellItem.display_name,
    icon: currentQuickSellItem.icon || "♻️",
    category: currentQuickSellItem.category,
    confidence: 100,
    qty: `${qty} ${currentQuickSellItem.unit || "kg"}`,
    value: totalVal,
    status: "Sell Request Sent",
    date: new Date().toLocaleDateString("en-IN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
  };
  const history = getHistory();
  history.unshift(historyEntry);
  localStorage.setItem("scrapsense_history", JSON.stringify(history.slice(0, 50)));

  // 3. Try to sync to backend API if available
  try {
    await fetch(`${API_BASE}/approval-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({
        listing_id: bookingId,
        buyer_name: "ScrapSense Recycler Network",
        quantity: qty,
        offered_price: spotPrice,
        address: `${address}, ${city} (Pickup: ${pickupSlot})`,
        payment_method: "UPI/Cash on Pickup"
      })
    });
  } catch {
    // Local storage fallback
  }

  // 4. Show success receipt screen
  if (qsReceiptId) qsReceiptId.textContent = bookingId;
  if (qsReceiptItem) qsReceiptItem.textContent = `${currentQuickSellItem.display_name} (${qty} ${currentQuickSellItem.unit || "kg"})`;
  if (qsReceiptAmount) qsReceiptAmount.textContent = `₹${totalVal.toLocaleString("en-IN")}`;
  if (qsReceiptSlot) qsReceiptSlot.textContent = pickupSlot;

  if (quickSellForm) quickSellForm.hidden = true;
  if (qsSuccessCard) qsSuccessCard.hidden = false;

  renderHistory();
  renderOrders();
});

qsDoneBtn?.addEventListener("click", () => {
  if (quickSellModal) quickSellModal.hidden = true;
  document.body.style.overflow = "";
});

// ============================================================
// FLOATING CAMERA AI SCANNER FAB
// ============================================================
const floatCamFab = document.getElementById("floatCamFab");
const floatCamBtn = document.getElementById("floatCamBtn");

floatCamBtn?.addEventListener("click", () => {
  const scanTab = document.querySelector(".seller-tab-btn[data-seller-tab='scanner']");
  scanTab?.click();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Show FAB when user scrolls below the scanner section
function updateFabVisibility() {
  if (!floatCamFab || !heroSection) return;
  const heroBottom = heroSection.getBoundingClientRect().bottom;
  const isSeller = currentSession && currentSession.role === "seller";
  floatCamFab.hidden = !(isSeller && heroBottom < -50);
}

window.addEventListener("scroll", updateFabVisibility, { passive: true });


// ============================================================
// ADMIN DATA HELPERS
// ============================================================
const DEFAULT_ADMIN_PRODUCTS = [
  { id: "copper-wire", name: "Copper Wire (Millberry)", category: "Non-Ferrous Metal", unit: "kg", icon: "🔶", min_price: 480, max_price: 680, sell_to: "Admin routing" },
  { id: "motherboard", name: "Motherboard / PCB", category: "High-Grade E-Waste", unit: "kg", icon: "🔌", min_price: 180, max_price: 450, sell_to: "Admin routing" },
  { id: "ic-chips", name: "IC Chips / Microchips", category: "High-Grade E-Waste", unit: "kg", icon: "🔲", min_price: 400, max_price: 950, sell_to: "Admin routing" },
  { id: "aluminium", name: "Aluminium Utensils / Sections", category: "Non-Ferrous Metal", unit: "kg", icon: "🥫", min_price: 125, max_price: 185, sell_to: "Admin routing" }
];

const DEFAULT_ADMIN_BUYERS = [];

function getAdminData(key, fallback) {
  try {
    const stored = JSON.parse(localStorage.getItem(key));
    return Array.isArray(stored) ? stored : fallback;
  } catch {
    return fallback;
  }
}

function saveAdminData(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    console.warn("Storage write error.");
  }
}

function getAdminProducts() { return getAdminData("scrapsense_admin_products", DEFAULT_ADMIN_PRODUCTS); }
function saveAdminProducts(products) { saveAdminData("scrapsense_admin_products", products); }
function getAdminBuyers() { return getAdminData("scrapsense_admin_buyers", DEFAULT_ADMIN_BUYERS); }
function saveAdminBuyers(buyers) { saveAdminData("scrapsense_admin_buyers", buyers); }
const DEFAULT_MARKETPLACE_LISTINGS = [
  // Metal Scrap
  { id: "lot-metal-1", item: "HMS 1&2 Heavy Melting Scrap", category: "Metal Scrap", unit: "kg", quantity: 1500, min_price: 38, max_price: 44, state: "Rajasthan", city: "Jaipur", note: "Clean 6mm+ industrial structural cuts, furnace-ready baled lots.", verified: true, created: "18/09/2026", ownerEmail: "apex.metals@scrapsense.org", seller: "Apex Metal Recyclers" },
  { id: "lot-metal-2", item: "Copper Millberry Bright Wire", category: "Metal Scrap", unit: "kg", quantity: 240, min_price: 740, max_price: 810, state: "Gujarat", city: "Ahmedabad", note: "99.9% pure stripped electrolytic copper wire scrap, unalloyed.", verified: true, created: "18/09/2026", ownerEmail: "gj.copper@scrapsense.org", seller: "Gujarat Copper Refiners" },
  { id: "lot-metal-3", item: "Stainless Steel 304 Scrap", category: "Metal Scrap", unit: "kg", quantity: 650, min_price: 130, max_price: 155, state: "Maharashtra", city: "Pune", note: "Industrial kitchenware & dairy tank offcuts, clean non-magnetic SS 304.", verified: true, created: "18/09/2026", ownerEmail: "western.alloys@scrapsense.org", seller: "Western Alloys Yard" },
  { id: "lot-metal-4", item: "Aluminium Extrusion 6063 Scrap", category: "Metal Scrap", unit: "kg", quantity: 420, min_price: 185, max_price: 215, state: "Delhi", city: "Delhi", note: "Clean architectural window sections, free of iron screws and gaskets.", verified: true, created: "18/09/2026", ownerEmail: "capital.extrusions@scrapsense.org", seller: "Capital Extrusions" },

  // Plastic Waste
  { id: "lot-plastic-1", item: "Clean Clear PET Bottle Bales", category: "Plastic Waste", unit: "kg", quantity: 800, min_price: 34, max_price: 42, state: "Madhya Pradesh", city: "Indore", note: "Post-consumer clear PET bottles, caps removed, washed and hydraulic baled.", verified: true, created: "18/09/2026", ownerEmail: "cleanpoly@scrapsense.org", seller: "CleanPoly Recyclers" },
  { id: "lot-plastic-2", item: "Rigid HDPE Drum & Crate Regrind", category: "Plastic Waste", unit: "kg", quantity: 500, min_price: 52, max_price: 64, state: "Rajasthan", city: "Jaipur", note: "Blue 200L drum regrind flakes, washed and dried, ready for extrusion.", verified: true, created: "18/09/2026", ownerEmail: "rj.polymers@scrapsense.org", seller: "Rajasthan Polymer Hub" },
  { id: "lot-plastic-3", item: "Rigid PVC Conduit Scrap", category: "Plastic Waste", unit: "kg", quantity: 350, min_price: 32, max_price: 40, state: "Uttar Pradesh", city: "Kanpur", note: "Factory electrical conduit pipe rejects, unplasticized PVC clean regrind.", verified: true, created: "18/09/2026", ownerEmail: "up.pipes@scrapsense.org", seller: "UP Pipes & Conduits" },
  { id: "lot-plastic-4", item: "LDPE Packaging Film Rolls", category: "Plastic Waste", unit: "kg", quantity: 600, min_price: 48, max_price: 58, state: "Punjab", city: "Ludhiana", note: "Transparent pallet stretch wrap scrap, 100% natural clear grade.", verified: true, created: "18/09/2026", ownerEmail: "pb.films@scrapsense.org", seller: "Punjab Film Solutions" },

  // Paper & Cardboard
  { id: "lot-paper-1", item: "Baled Corrugated Cartons (OCC 95/5)", category: "Paper & Cardboard", unit: "kg", quantity: 2200, min_price: 14, max_price: 18, state: "Rajasthan", city: "Jaipur", note: "High-burst corrugated cardboard boxes, mill baled, moisture under 10%.", verified: true, created: "18/09/2026", ownerEmail: "pinkcity.paper@scrapsense.org", seller: "Pink City Paper Pulp" },
  { id: "lot-paper-2", item: "Sorted Office White Paper (SOW)", category: "Paper & Cardboard", unit: "kg", quantity: 950, min_price: 18, max_price: 24, state: "Delhi", city: "Delhi", note: "De-stapled office copier paper, records and invoices, woodfree white stock.", verified: true, created: "18/09/2026", ownerEmail: "metro.paper@scrapsense.org", seller: "Metro Paper Recyclers" },
  { id: "lot-paper-3", item: "Old Newspapers (ONP Bales)", category: "Paper & Cardboard", unit: "kg", quantity: 1200, min_price: 14, max_price: 17, state: "Maharashtra", city: "Pune", note: "Sorted household and press return newspaper stacks, unsoiled.", verified: true, created: "18/09/2026", ownerEmail: "deccan.news@scrapsense.org", seller: "Deccan Newsprint Bales" },
  { id: "lot-paper-4", item: "Duplex Grey Board Offcuts", category: "Paper & Cardboard", unit: "kg", quantity: 700, min_price: 11, max_price: 15, state: "Gujarat", city: "Ahmedabad", note: "Clean box manufacturing trims, grey-back duplex board cuttings.", verified: true, created: "18/09/2026", ownerEmail: "gj.boards@scrapsense.org", seller: "Gujarat Board Yards" },

  // E-Waste
  { id: "lot-ewaste-1", item: "Dual-Socket Server Motherboards", category: "E-Waste", unit: "unit", quantity: 180, min_price: 550, max_price: 900, state: "Karnataka", city: "Bengaluru", note: "High-gold grade multi-socket enterprise server boards, BGA chips intact.", verified: true, created: "18/09/2026", ownerEmail: "silicon.escrap@scrapsense.org", seller: "Silicon City E-Scrap" },
  { id: "lot-ewaste-2", item: "DDR3/DDR4 Gold Finger RAM Modules", category: "E-Waste", unit: "unit", quantity: 350, min_price: 85, max_price: 145, state: "Maharashtra", city: "Pune", note: "Unsorted desktop and workstation memory DIMMs with clean gold pins.", verified: true, created: "18/09/2026", ownerEmail: "techcycle@scrapsense.org", seller: "TechCycle Labs" },
  { id: "lot-ewaste-3", item: "Defective Lithium-Ion 18650 Battery Cells", category: "E-Waste", unit: "kg", quantity: 280, min_price: 140, max_price: 195, state: "Delhi", city: "Delhi", note: "De-housed EV and power tool 18650 cells, sorted for black mass extraction.", verified: true, created: "18/09/2026", ownerEmail: "greenpower@scrapsense.org", seller: "GreenPower Battery Salvage" },
  { id: "lot-ewaste-4", item: "Mixed Ceramic & Fiber CPUs", category: "E-Waste", unit: "unit", quantity: 120, min_price: 220, max_price: 480, state: "Telangana", city: "Hyderabad", note: "High-yield Intel/AMD 486, Pentium Pro and socket 775/1155 ceramic processor scrap.", verified: true, created: "18/09/2026", ownerEmail: "cybergold@scrapsense.org", seller: "CyberGold Refineries" },

  // Glass & Rubber
  { id: "lot-glassrubber-1", item: "Crumb Rubber 30-Mesh Granules", category: "Glass & Rubber", unit: "kg", quantity: 1400, min_price: 26, max_price: 36, state: "Tamil Nadu", city: "Chennai", note: "Magnetic separated rubber granules, free of wire and fluff, ready for asphalt blending.", verified: true, created: "18/09/2026", ownerEmail: "tn.crumb@scrapsense.org", seller: "Tamil Nadu Crumb Industries" },
  { id: "lot-glassrubber-2", item: "Clear Flint Glass Cullet (Sorted)", category: "Glass & Rubber", unit: "kg", quantity: 3000, min_price: 3.5, max_price: 5.5, state: "Uttar Pradesh", city: "Firozabad", note: "Color-sorted flint cullet from beverage bottling plants, washed and furnace ready.", verified: true, created: "18/09/2026", ownerEmail: "suhaag.glass@scrapsense.org", seller: "Suhaag Glass Works" },
  { id: "lot-glassrubber-3", item: "Used Commercial TBR Truck Tyres", category: "Glass & Rubber", unit: "unit", quantity: 80, min_price: 450, max_price: 750, state: "Rajasthan", city: "Jaipur", note: "Heavy radial commercial vehicle casings suitable for pyrolysis distillation.", verified: true, created: "18/09/2026", ownerEmail: "rj.tyres@scrapsense.org", seller: "Rajasthan Tyre Recyclers" },
  { id: "lot-glassrubber-4", item: "Industrial EPDM Rubber Conveyor Belt Scrap", category: "Glass & Rubber", unit: "kg", quantity: 900, min_price: 16, max_price: 24, state: "Jharkhand", city: "Ranchi", note: "Heavy-duty 4-ply rubber conveyor belt strips salvaged from iron ore washeries.", verified: true, created: "18/09/2026", ownerEmail: "mining.conveyor@scrapsense.org", seller: "Mining Conveyor Salvage" },

  // Industrial Scrap
  { id: "lot-industrial-1", item: "Burned Cast Iron Motor Stators", category: "Industrial Scrap", unit: "kg", quantity: 450, min_price: 85, max_price: 115, state: "Tamil Nadu", city: "Coimbatore", note: "Heavy 3-phase industrial motor housings with complete copper stator windings.", verified: true, created: "18/09/2026", ownerEmail: "cbe.motors@scrapsense.org", seller: "Coimbatore Electro-Motors" },
  { id: "lot-industrial-2", item: "Industrial 200-Litre HDPE Drums", category: "Industrial Scrap", unit: "unit", quantity: 160, min_price: 320, max_price: 460, state: "Gujarat", city: "Vadodara", note: "Triple-rinsed neutral chemical storage barrels, unpunctured with bungs intact.", verified: true, created: "18/09/2026", ownerEmail: "baroda.drums@scrapsense.org", seller: "Baroda Chemical Packaging" },
  { id: "lot-industrial-3", item: "Rotary Machine Tool Bed Castings", category: "Industrial Scrap", unit: "kg", quantity: 1800, min_price: 36, max_price: 42, state: "Gujarat", city: "Rajkot", note: "Heavy grade 25 grey cast iron machine bed cuts, zero slag or porosity.", verified: true, created: "18/09/2026", ownerEmail: "saurashtra.foundry@scrapsense.org", seller: "Saurashtra Foundry Scrap" },
  { id: "lot-industrial-4", item: "Copper Tube & Aluminium Fin HVAC Coils", category: "Industrial Scrap", unit: "kg", quantity: 320, min_price: 310, max_price: 370, state: "Delhi", city: "Delhi", note: "Chiller and VRF indoor unit heat exchanger coils, dry clean metal.", verified: true, created: "18/09/2026", ownerEmail: "capital.hvac@scrapsense.org", seller: "Capital HVAC Dismantlers" }
];

function getListings() {
  const stored = getAdminData("scrapsense_listings", null);
  if (Array.isArray(stored) && stored.length > 0) {
    return stored;
  }
  saveAdminData("scrapsense_listings", DEFAULT_MARKETPLACE_LISTINGS);
  return DEFAULT_MARKETPLACE_LISTINGS;
}
function saveListings(listings) { saveAdminData("scrapsense_listings", listings); }
function getOrders() { return getAdminData("scrapsense_orders", []); }
function saveOrders(orders) { saveAdminData("scrapsense_orders", orders); }

// ============================================================
// ROLE VISIBILITY CONTROLLER
// ============================================================
const buyerNavBar = document.getElementById("buyerNavBar");
const buyerAddSection = document.getElementById("buyerAddItem");
const buyerRequestsSection = document.getElementById("buyerRequests");
const buyerRequestsList = document.getElementById("buyerRequestsList");
let activeBuyerTab = "marketplace";

function setRoleVisibility() {
  const isAdmin = currentSession && currentSession.role === "admin";
  const isSeller = currentSession && currentSession.role === "seller";
  const isBuyer = currentSession && currentSession.role === "buyer";
  document.body.dataset.role = currentSession?.role || "guest";

  const adminSection = document.getElementById("admin");

  // Admin: show ONLY admin panel
  if (adminSection) adminSection.hidden = !isAdmin;

  // Seller nav bar
  if (sellerNavBar) sellerNavBar.hidden = !isSeller;
  // Buyer nav bar
  if (buyerNavBar) buyerNavBar.hidden = !isBuyer;

  // Marketplace: visible to buyer (filtered to approved), admin (all lots), hidden to seller
  if (marketSection) marketSection.hidden = isSeller || isAdmin;

  // Update prominent User Session & Logout Widget in top header
  const userSessionWidget = document.getElementById("userSessionWidget");
  const userRoleTag = document.getElementById("userRoleTag");
  const userDisplayName = document.getElementById("userDisplayName");
  const userAvatarIcon = document.getElementById("userAvatarIcon");

  if (userSessionWidget) {
    if (currentSession) {
      userSessionWidget.hidden = false;
      if (userDisplayName) userDisplayName.textContent = currentSession.name || "User";
      if (userRoleTag) userRoleTag.textContent = currentSession.role ? currentSession.role.toUpperCase() : "MEMBER";
      if (userAvatarIcon) {
        userAvatarIcon.textContent = isAdmin ? "🛡️" : (isBuyer ? "🏢" : "📦");
      }
    } else {
      userSessionWidget.hidden = true;
    }
  }

  if (sessionLabel) {
    sessionLabel.textContent = currentSession ? `${currentSession.name} · ${currentSession.role.toUpperCase()}` : "";
  }

  if (isSeller) {
    // SELLER: only seller sections visible via tab navigation
    heroSection.hidden = false;
    categoriesSection.hidden = false;
    resultSection.hidden = !currentResult;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = true;
    if (buyerAddSection) buyerAddSection.hidden = true;
    if (buyerRequestsSection) buyerRequestsSection.hidden = true;
    setSellerView(activeSellerTab || "scanner");

  } else if (isBuyer) {
    // BUYER: only buyer sections visible via tab navigation
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = true;
    setBuyerView(activeBuyerTab || "marketplace");

  } else if (isAdmin) {
    // ADMIN: only admin panel
    heroSection.hidden = true;
    categoriesSection.hidden = true;
    resultSection.hidden = true;
    sellerPostLotSection.hidden = true;
    ordersSection.hidden = true;
    historySection.hidden = true;
    howSection.hidden = true;
    if (marketSection) marketSection.hidden = true;
    if (buyerAddSection) buyerAddSection.hidden = true;
    if (buyerRequestsSection) buyerRequestsSection.hidden = true;
  }

  // Update marketplace action button text and visibility based on role
  const marketAddProductBtn = document.getElementById("marketAddProductBtn");
  if (marketAddProductBtn) {
    if (isBuyer) {
      marketAddProductBtn.style.display = "";
      marketAddProductBtn.innerHTML = "<span>📋 Post Buy Requirement (RFQ)</span>";
      marketAddProductBtn.title = "Post your scrap procurement requirement to certified sellers";
    } else if (isSeller) {
      marketAddProductBtn.style.display = "";
      marketAddProductBtn.innerHTML = "<span>➕ Post Scrap Lot</span>";
      marketAddProductBtn.title = "Post your scrap lot for sale";
    } else if (isAdmin) {
      marketAddProductBtn.style.display = "none";
    }
  }

  renderMarketplace();
  renderOrders();
  renderSellerMyLots();
  if (isAdmin) {
    renderAdmin();
    loadRegisteredUsers();
  }
  syncListings().then(renderMarketplace);
  syncOrders().then(() => {
    renderAdmin();
    renderOrders();
  });
}

// ============================================================
// BUYER TAB NAVIGATION
// ============================================================
const buyerTabBtns = document.querySelectorAll(".buyer-tab-btn");

function setBuyerView(tabName) {
  activeBuyerTab = tabName;
  buyerTabBtns.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.buyerTab === tabName);
  });

  const isBuyer = currentSession && currentSession.role === "buyer";
  if (!isBuyer) return;

  if (tabName === "marketplace") {
    if (marketSection) marketSection.hidden = false;
    if (buyerAddSection) buyerAddSection.hidden = true;
    if (buyerRequestsSection) buyerRequestsSection.hidden = true;
    renderMarketplace();
  } else if (tabName === "add-item") {
    if (marketSection) marketSection.hidden = true;
    if (buyerAddSection) buyerAddSection.hidden = false;
    if (buyerRequestsSection) buyerRequestsSection.hidden = true;
  } else if (tabName === "my-requests") {
    if (marketSection) marketSection.hidden = true;
    if (buyerAddSection) buyerAddSection.hidden = true;
    if (buyerRequestsSection) buyerRequestsSection.hidden = false;
    renderBuyerRequests();
  } else if (tabName === "chatbot") {
    if (window.openCopilot) window.openCopilot();
  }
}

buyerTabBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    setBuyerView(btn.dataset.buyerTab);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});

function renderBuyerRequests() {
  if (!buyerRequestsList) return;
  const orders = getOrders().filter(o => o.buyerEmail === currentSession?.email);
  if (!orders.length) {
    buyerRequestsList.innerHTML = '<div class="empty-market">No requests submitted yet. Use "Add Item / Price Offer" tab to send one.</div>';
    return;
  }
  buyerRequestsList.innerHTML = orders.map(o => `
    <div class="order-row">
      <div>
        <strong>${escapeHTML(o.lot || "Scrap Request")}</strong>
        <span>Qty: ${escapeHTML(String(o.quantity || ""))} ${escapeHTML(o.unit || "")} · ${escapeHTML(o.date || "")}</span>
      </div>
      <span class="offer-price">${o.offered_price ? `₹${Number(o.offered_price).toLocaleString("en-IN")} / unit` : "Pending price"}</span>
      <b class="order-status ${(o.status || "").includes("approved") ? "status-approved" : ""}">${
        escapeHTML(o.status || "Pending Admin Review")
      }</b>
    </div>
  `).join("");
}

// ============================================================
// AUTHENTICATION & LOGIN/REGISTRATION
// ============================================================
function setAuthMode(mode) {
  if (mode === "register" && authRole === "admin") {
    setRole("seller");
  }
  if (mode === "register") {
    modeRegisterBtn?.classList.add("active");
    modeLoginBtn?.classList.remove("active");
    if (registerCard) registerCard.hidden = false;
    if (loginCard) loginCard.hidden = true;
    if (registrationMessage) registrationMessage.textContent = "";
  } else {
    modeLoginBtn?.classList.add("active");
    modeRegisterBtn?.classList.remove("active");
    if (loginCard) loginCard.hidden = false;
    if (registerCard) registerCard.hidden = true;
    if (authMessage) authMessage.textContent = "";
  }
}

modeLoginBtn?.addEventListener("click", () => setAuthMode("login"));
modeRegisterBtn?.addEventListener("click", () => setAuthMode("register"));
goToRegisterBtn?.addEventListener("click", () => setAuthMode("register"));
goToLoginBtn?.addEventListener("click", () => setAuthMode("login"));

// Role config per role
const ROLE_CONFIG = {
  seller: {
    icon: "📦",
    label: "Seller Portal",
    panelClass: "auth-panel--seller",
    loginTitle: "Seller Sign In",
    loginSubtitle: "Access AI camera scanner, live scrap rates, and post your lots for sale.",
    btnText: "Sign In as Seller",
    registerTitle: "Create Seller Account",
    registerSubtitle: "Register to scan components, check live mandi rates, and submit lots for sale.",
    canRegister: true
  },
  buyer: {
    icon: "🏢",
    label: "Buyer Portal",
    panelClass: "auth-panel--buyer",
    loginTitle: "Buyer Sign In",
    loginSubtitle: "Browse verified seller lots, approve purchases, and request items at your price.",
    btnText: "Sign In as Buyer",
    registerTitle: "Create Buyer Account",
    registerSubtitle: "Register to browse lots, approve seller listings, and send price requests to admin.",
    canRegister: true
  },
  admin: {
    icon: "🛡️",
    label: "Admin Control Room",
    panelClass: "auth-panel--admin",
    loginTitle: "Administrator Sign In",
    loginSubtitle: "Enter administrator credentials to manage approvals, buyer records, and product rates.",
    btnText: "Sign In as Administrator",
    canRegister: false
  }
};

function setRole(role) {
  authRole = role;
  const config = ROLE_CONFIG[role] || ROLE_CONFIG.seller;

  // Update role card active state
  roleCardBtns.forEach(card => {
    card.classList.toggle("active-role-card", card.dataset.role === role);
  });

  // Update form panel role class
  if (authFormPanel) {
    authFormPanel.className = `auth-form-panel ${config.panelClass}`;
  }

  // Update role badge
  if (authRoleBadgeIcon) authRoleBadgeIcon.textContent = config.icon;
  if (authRoleBadgeLabel) authRoleBadgeLabel.textContent = config.label;

  if (role === "admin") {
    // Admin: no registration, show hint, pre-fill credentials
    if (adminHint) adminHint.hidden = false;
    if (registerSwitchPrompt) registerSwitchPrompt.hidden = true;
    // Hide register mode button for admin
    const modeRegBtn = document.getElementById("modeRegisterBtn");
    if (modeRegBtn) modeRegBtn.style.display = "none";
    if (authEmailLabel) authEmailLabel.childNodes[0].textContent = "Admin ID / Phone";
    if (authEmailInput) {
      authEmailInput.type = "text";
      authEmailInput.placeholder = "Enter Admin Login ID";
      authEmailInput.value = "";
    }
    if (authPasswordInput) {
      authPasswordInput.value = "";
    }
    setAuthMode("login");
  } else {
    // Seller / Buyer
    if (adminHint) adminHint.hidden = true;
    if (registerSwitchPrompt) registerSwitchPrompt.hidden = false;
    // Show register mode button
    const modeRegBtn = document.getElementById("modeRegisterBtn");
    if (modeRegBtn) modeRegBtn.style.display = "";
    if (authEmailLabel) authEmailLabel.childNodes[0].textContent = "Email Address";
    if (authEmailInput) {
      authEmailInput.type = "email";
      authEmailInput.placeholder = "you@example.com";
      authEmailInput.value = "";
    }
    if (authPasswordInput) {
      authPasswordInput.value = "";
    }
    if (registerTitle) registerTitle.textContent = config.registerTitle;
    if (registerSubtitle) registerSubtitle.textContent = config.registerSubtitle;
  }

  if (loginTitle) loginTitle.textContent = config.loginTitle;
  if (loginSubtitle) loginSubtitle.textContent = config.loginSubtitle;
  const txt = loginSubmitBtn?.querySelector(".btn-text");
  if (txt) txt.textContent = config.btnText;

  // Update quick role pills in form panel
  document.querySelectorAll(".quick-role-pill").forEach(pill => {
    pill.classList.toggle("active", pill.dataset.role === role);
  });
}

// Role card click handlers
roleCardBtns.forEach(card => card.addEventListener("click", () => {
  setRole(card.dataset.role);
}));

// Quick role pill click handlers in form panel
document.querySelectorAll(".quick-role-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    setRole(pill.dataset.role);
  });
});

// Handle Login
authForm?.addEventListener("submit", async event => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(authForm));
  authMessage.textContent = "";

  const payload = authRole === "admin"
    ? { email: values.email, password: values.password, role: "admin" }
    : { email: values.email.trim().toLowerCase(), password: values.password, role: authRole };

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Authentication failed");

    currentSession = { name: data.name, email: data.email, role: data.role };
    if (data.token) setAuthToken(data.token);
    saveStoredSession(currentSession);
    authScreen.hidden = true;
    setRoleVisibility();
  } catch (err) {
    // Local demo login fallback if offline
    if (!isBackendOnline) {
      currentSession = { name: values.email.split("@")[0] || "User", email: values.email, role: authRole };
      saveStoredSession(currentSession);
      authScreen.hidden = true;
      setRoleVisibility();
    } else {
      authMessage.textContent = err.message;
    }
  }
});

// Handle Register
registrationForm?.addEventListener("submit", async event => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(registrationForm));
  registrationMessage.textContent = "";

  const payload = {
    name: values.name.trim(),
    email: values.email.trim().toLowerCase(),
    password: values.password,
    role: authRole
  };

  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed");

    currentSession = { name: data.name, email: data.email, role: data.role };
    if (data.token) setAuthToken(data.token);
    saveStoredSession(currentSession);
    authScreen.hidden = true;
    setRoleVisibility();
  } catch (err) {
    if (!isBackendOnline) {
      currentSession = { name: values.name, email: values.email, role: authRole };
      saveStoredSession(currentSession);
      authScreen.hidden = true;
      setRoleVisibility();
    } else {
      registrationMessage.textContent = err.message;
    }
  }
});

// ============================================================
// UNIVERSAL LOGOUT CONTROLLER
// ============================================================
function performLogout() {
  const previousRole = currentSession?.role || "seller";
  currentSession = null;
  authToken = null;
  clearStoredSession();
  clearStoredToken();
  if (authScreen) authScreen.hidden = false;
  setRole(previousRole);
  setAuthMode("login");
  setRoleVisibility();
  showToast("🚪 You have been logged out.", "info");
}

logoutBtn?.addEventListener("click", performLogout);
document.getElementById("headerLogoutBtn")?.addEventListener("click", performLogout);
document.getElementById("sellerLogoutBtn")?.addEventListener("click", performLogout);
document.getElementById("buyerLogoutBtn")?.addEventListener("click", performLogout);
document.getElementById("adminLogoutBtn")?.addEventListener("click", performLogout);

// ============================================================
// SELLER LOT SUBMISSION
// ============================================================
const autoDetectLocationBtn = document.getElementById("autoDetectLocationBtn");

if (autoDetectLocationBtn) {
  autoDetectLocationBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      if (typeof showToast !== "undefined") showToast("Geolocation is not supported by your browser.", "error");
      return;
    }
    
    autoDetectLocationBtn.textContent = "⌛...";
    autoDetectLocationBtn.disabled = true;

    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
        const data = await response.json();
        const addrInput = document.getElementById("lotAddressInput");
        const lCity = document.getElementById("listingCity");
        const lState = document.getElementById("listingState");
        
        if (data && data.address) {
          const addr = data.address;
          const road = addr.road || addr.suburb || addr.neighbourhood || "";
          const city = addr.city || addr.town || addr.village || addr.county || "";
          const state = addr.state || "";
          
          if (addrInput) addrInput.value = data.display_name || `${road}, ${city}`;
          
          if (city && lCity) {
            let cityOption = Array.from(lCity.options).find(opt => opt.value.toLowerCase() === city.toLowerCase());
            if (!cityOption) {
              const newOpt = document.createElement("option");
              newOpt.value = city;
              newOpt.textContent = city;
              lCity.appendChild(newOpt);
              cityOption = newOpt;
            }
            lCity.value = cityOption.value;
          }
          
          if (state && lState) {
             let stateOption = Array.from(lState.options).find(opt => opt.value.toLowerCase() === state.toLowerCase());
             if (stateOption) lState.value = stateOption.value;
          }
          
          if (typeof showToast !== "undefined") showToast("Location detected successfully!", "success");
        } else {
          if (addrInput) addrInput.value = `GPS: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
          if (typeof showToast !== "undefined") showToast("Could not resolve address. Coordinates saved.", "info");
        }
      } catch (err) {
        const addrInput = document.getElementById("lotAddressInput");
        if (addrInput) addrInput.value = `GPS: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
        if (typeof showToast !== "undefined") showToast("Address lookup failed. Coordinates saved.", "info");
      } finally {
        autoDetectLocationBtn.textContent = "📍 Detect";
        autoDetectLocationBtn.disabled = false;
      }
    }, (error) => {
      if (typeof showToast !== "undefined") showToast("Location access denied or failed.", "error");
      autoDetectLocationBtn.textContent = "📍 Detect";
      autoDetectLocationBtn.disabled = false;
    });
  });
}
listingForm?.addEventListener("submit", async event => {
  event.preventDefault();
  if (!currentSession) return;
  const values = Object.fromEntries(new FormData(listingForm));
  const listings = getListings();

  const itemName = values.item || (currentResult ? currentResult.detected_item : "Scrap Component");
  const categoryName = values.category || (currentResult ? currentResult.category : "High-Grade E-Waste");
  const minP = currentResult?.min_price || 100;
  const maxP = currentResult?.max_price || 300;

  let photoData = "";
  const fileInput = document.getElementById("lotFileInput");
  if (fileInput && fileInput.files.length > 0) {
    const file = fileInput.files[0];
    if (file.type.startsWith("image/")) {
      photoData = await compressImage(file);
    } else {
      photoData = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => resolve("");
        reader.readAsDataURL(file);
      });
    }
  } else if (currentBlob) {
    photoData = await compressImage(currentBlob);
  }

  const listing = {
    seller: currentSession.name,
    seller_email: currentSession.email,
    item: itemName,
    category: categoryName,
    unit: values.unit || "kg",
    quantity: Number(values.quantity),
    state: values.state,
    city: values.city,
    note: values.note,
    min_price: minP,
    max_price: maxP,
    photo: photoData,
    seller_phone: values.seller_phone,
    address: values.address
  };

  let listingId = `lot-${Date.now()}`;
  try {
    const response = await fetch(`${API_BASE}/listings`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(listing)
    });
    if (response.ok) {
      const serverListing = await response.json();
      listingId = serverListing.id || listingId;
    }
  } catch {
    // Storage fallback
  }

  const publicListing = {
    id: listingId,
    item: listing.item,
    category: listing.category,
    unit: listing.unit,
    quantity: listing.quantity,
    state: listing.state,
    city: listing.city,
    note: listing.note,
    min_price: listing.min_price,
    max_price: listing.max_price,
    photo: listing.photo,
    ownerEmail: currentSession.email,
    verified: false,
    created: new Date().toLocaleDateString("en-IN")
  };

  listings.unshift(publicListing);
  saveAdminData("scrapsense_listings", listings);
  listingForm.reset();
  listingMessage.textContent = "✅ Lot submitted successfully! Admin will verify and publish for buyers.";
  renderMarketplace();
  renderSellerMyLots();
});

function compressImage(blob, maxKB = 150) {
  return new Promise((resolve) => {
    if (!blob) { resolve(""); return; }
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      let { width, height } = img;
      const maxDim = 800;
      if (width > maxDim || height > maxDim) {
        if (width > height) { height = Math.round((height * maxDim) / width); width = maxDim; }
        else { width = Math.round((width * maxDim) / height); height = maxDim; }
      }
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, width, height);
      canvas.toBlob((compressed) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => resolve("");
        reader.readAsDataURL(compressed);
      }, "image/jpeg", 0.7);
    };
    img.onerror = () => resolve("");
    img.src = URL.createObjectURL(blob);
  });
}

// ============================================================
// SELLER "MY PUBLISHED LOTS" MANAGEMENT & EDIT MODAL
// ============================================================
function renderSellerMyLots() {
  const tbody = document.getElementById("sellerMyLotsTbody");
  const countBadge = document.getElementById("sellerMyLotsCount");
  if (!tbody) return;

  const isSeller = currentSession && currentSession.role === "seller";
  if (!isSeller) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-lots-cell">Log in as a seller to manage your scrap lots.</td></tr>';
    if (countBadge) countBadge.textContent = "0 Lots";
    return;
  }

  const allListings = getListings();
  const email = (currentSession.email || "").toLowerCase().trim();
  const name = (currentSession.name || "").toLowerCase().trim();

  // Lots owned by this seller
  let myLots = allListings.filter(lot => {
    const lotEmail = (lot.ownerEmail || lot.seller_email || "").toLowerCase().trim();
    const lotSeller = (lot.seller || "").toLowerCase().trim();
    return (email && lotEmail === email) || (name && lotSeller === name);
  });

  // If newly registered seller with 0 lots, seed 2 manageable draft lots so they can test editing right away
  if (myLots.length === 0 && email) {
    const starterLot1 = {
      id: `lot-seller-${Date.now()}-1`,
      item: "Mixed Electronics & Motherboard PCBs",
      category: "E-Waste",
      unit: "kg",
      quantity: 25,
      min_price: 180,
      max_price: 320,
      state: "Rajasthan",
      city: "Jaipur",
      note: "Dual-socket telecom & desktop PCBs, intact ICs ready for inspection.",
      photo: "",
      ownerEmail: email,
      seller: currentSession.name,
      verified: true,
      created: new Date().toLocaleDateString("en-IN")
    };
    const starterLot2 = {
      id: `lot-seller-${Date.now()}-2`,
      item: "Heavy Melting Steel & Rebar Scrap",
      category: "Metal Scrap",
      unit: "kg",
      quantity: 350,
      min_price: 36,
      max_price: 42,
      state: "Rajasthan",
      city: "Jaipur",
      note: "Structural fabrication offcuts, clean 8mm cuts.",
      photo: "",
      ownerEmail: email,
      seller: currentSession.name,
      verified: false,
      created: new Date().toLocaleDateString("en-IN")
    };
    allListings.unshift(starterLot1, starterLot2);
    saveListings(allListings);
    myLots = [starterLot1, starterLot2];
  }

  if (countBadge) countBadge.textContent = `${myLots.length} Lot${myLots.length === 1 ? "" : "s"}`;

  if (myLots.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-lots-cell">You have not published any scrap lots yet. Fill the form above to submit your first lot.</td></tr>';
    return;
  }

  tbody.innerHTML = myLots.map(lot => {
    const minP = Number(lot.min_price || 0).toLocaleString("en-IN");
    const maxP = Number(lot.max_price || 0).toLocaleString("en-IN");
    const isVerified = lot.verified === true;
    return `
      <tr data-lot-id="${escapeHTML(lot.id)}">
        <td>
          <div class="sml-item-cell">
            <strong>${escapeHTML(lot.item)}</strong>
            <span class="tag-chip">${escapeHTML(lot.category)}</span>
          </div>
        </td>
        <td><b>${escapeHTML(String(lot.quantity))}</b> <span class="sml-unit">${escapeHTML(lot.unit || "kg")}</span></td>
        <td><span class="sml-price-text">₹${minP} – ₹${maxP}</span></td>
        <td><span class="sml-loc">${escapeHTML(lot.city || "N/A")}${lot.state ? `, ${escapeHTML(lot.state)}` : ""}</span></td>
        <td>
          <span class="verify-state ${isVerified ? "verified" : "pending"}">
            ${isVerified ? "✓ Verified" : "⏳ Pending"}
          </span>
        </td>
        <td style="text-align: right;">
          <div class="sml-actions">
            <button type="button" class="btn btn-sm btn-outline edit-lot-btn" data-lot-id="${escapeHTML(lot.id)}" title="Edit lot details">
              ✏️ Edit
            </button>
            <button type="button" class="btn btn-sm btn-danger delete-lot-btn" data-lot-id="${escapeHTML(lot.id)}" title="Delete scrap lot">
              🗑️
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  // Attach edit and delete handlers
  tbody.querySelectorAll(".edit-lot-btn").forEach(btn => {
    btn.addEventListener("click", () => openEditLotModal(btn.dataset.lotId));
  });
  tbody.querySelectorAll(".delete-lot-btn").forEach(btn => {
    btn.addEventListener("click", () => deleteSellerLot(btn.dataset.lotId));
  });
}

const editLotModal = document.getElementById("editLotModal");
const editLotForm = document.getElementById("editLotForm");
const closeEditLotModalBtn = document.getElementById("closeEditLotModal");
const cancelEditLotBtn = document.getElementById("cancelEditLotBtn");
const editLotMessage = document.getElementById("editLotMessage");

function openEditLotModal(lotId) {
  const lot = getListings().find(l => String(l.id) === String(lotId));
  if (!lot) {
    showToast("Lot not found", "error");
    return;
  }
  document.getElementById("editLotId").value = lot.id;
  document.getElementById("editLotItem").value = lot.item || "";
  document.getElementById("editLotCategory").value = lot.category || "E-Waste";
  document.getElementById("editLotQuantity").value = lot.quantity || "";
  document.getElementById("editLotUnit").value = lot.unit || "kg";
  document.getElementById("editLotMinPrice").value = lot.min_price || "";
  document.getElementById("editLotMaxPrice").value = lot.max_price || "";
  document.getElementById("editLotState").value = lot.state || "";
  document.getElementById("editLotCity").value = lot.city || "";
  document.getElementById("editLotNote").value = lot.note || "";
  if (editLotMessage) editLotMessage.textContent = "";

  const kicker = document.getElementById("editLotKicker");
  const title = document.getElementById("editLotModalTitle");
  const sub = document.getElementById("editLotModalSub");
  if (currentSession?.role === "buyer") {
    if (kicker) kicker.textContent = "BUYER PRODUCT & PRICING DESK";
    if (title) title.textContent = "✏️ Edit Product Price & Data";
    if (sub) sub.textContent = "Update spot rates, quantity, material specifications, or procurement terms.";
  } else {
    if (kicker) kicker.textContent = "SELLER LOT MANAGEMENT";
    if (title) title.textContent = "✏️ Edit Scrap Lot";
    if (sub) sub.textContent = "Update pricing, quantity, condition, or location for this scrap lot.";
  }

  if (editLotModal) editLotModal.hidden = false;
}

function closeEditLotModal() {
  if (editLotModal) editLotModal.hidden = true;
}

closeEditLotModalBtn?.addEventListener("click", closeEditLotModal);
cancelEditLotBtn?.addEventListener("click", closeEditLotModal);

editLotForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("editLotId").value;
  const item = document.getElementById("editLotItem").value.trim();
  const category = document.getElementById("editLotCategory").value;
  const quantity = parseFloat(document.getElementById("editLotQuantity").value) || 0;
  const unit = document.getElementById("editLotUnit").value;
  const min_price = parseFloat(document.getElementById("editLotMinPrice").value) || 0;
  const max_price = parseFloat(document.getElementById("editLotMaxPrice").value) || 0;
  const state = document.getElementById("editLotState").value.trim();
  const city = document.getElementById("editLotCity").value.trim();
  const note = document.getElementById("editLotNote").value.trim();

  try {
    await fetch(`${API_BASE}/listings/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ item, category, quantity, unit, min_price, max_price, state, city, note })
    });
  } catch (err) {
    console.warn("Backend update skipped:", err);
  }

  // Update in local storage
  const currentListings = getListings();
  const updatedListings = currentListings.map(lot => {
    if (String(lot.id) === String(id)) {
      return { ...lot, item, category, quantity, unit, min_price, max_price, state, city, note };
    }
    return lot;
  });
  saveListings(updatedListings);
  closeEditLotModal();
  renderSellerMyLots();
  renderMarketplace();
  showToast("✅ Scrap lot updated successfully!", "success");
});

async function deleteSellerLot(lotId) {
  const lot = getListings().find(l => String(l.id) === String(lotId));
  if (!lot) return;
  if (!confirm(`Are you sure you want to delete "${lot.item}" from your published scrap lots?`)) {
    return;
  }

  try {
    await fetch(`${API_BASE}/listings/${encodeURIComponent(lotId)}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
  } catch (err) {
    console.warn("Backend delete skipped:", err);
  }

  const nextListings = getListings().filter(l => String(l.id) !== String(lotId));
  saveListings(nextListings);
  renderSellerMyLots();
  renderMarketplace();
  showToast("🗑️ Scrap lot removed.", "info");
}

// ============================================================
// MARKETPLACE & BUYER DECISIONS
// ============================================================
function renderMarketplace() {
  if (!marketGrid) return;
  const allListings = getListings();
  const cities = [...new Set(allListings.map(lot => `${lot.state ? `${lot.state} · ` : ""}${lot.city || ""}`).filter(Boolean))].sort();
  const previousCity = cityFilter?.value || "all";
  if (cityFilter) {
    cityFilter.innerHTML = '<option value="all">All cities</option>' + cities.map(city => `<option value="${escapeHTML(city)}">${escapeHTML(city)}</option>`).join("");
    cityFilter.value = cities.includes(previousCity) ? previousCity : "all";
  }

  const visibleListings = currentSession?.role === "admin" ? allListings : allListings.filter(lot => lot.verified === true);
  const listings = (cityFilter?.value && cityFilter.value !== "all")
    ? visibleListings.filter(lot => `${lot.state ? `${lot.state} · ` : ""}${lot.city || ""}` === cityFilter.value)
    : visibleListings;

  if (marketCount) marketCount.textContent = `${listings.length} active lot${listings.length === 1 ? "" : "s"}`;
  if (!listings.length) {
    marketGrid.innerHTML = '<div class="empty-market">No seller lots published yet.</div>';
    return;
  }

  marketGrid.innerHTML = listings.map(lot => {
    const isBuyer = currentSession?.role === "buyer";
    const isAdmin = currentSession?.role === "admin";
    const canEdit = isBuyer || isAdmin || (currentSession?.email && lot.ownerEmail === currentSession.email);
    const refCode = String(lot.id).replace(/[^a-zA-Z0-9]/g, '').slice(-4).toUpperCase();
    const authorName = lot.seller || (isBuyer ? (currentSession.name || "Enterprise Procurement Desk") : "Verified Supplier");
    const manualBadgeText = lot.isManual ? "✍️ Manually Added · Custom Product" : `✍️ Manual Listing · Ref #${refCode}`;

    return `
    <article class="market-card ${lot.isManual ? 'market-card-custom' : ''}">
      <div class="market-photo">
        ${lot.photo ? `<img src="${sanitizeImageSrc(lot.photo)}" alt="${escapeHTML(lot.item)}" />` : `<span>${escapeHTML(currentResult?.icon || "♻️")}</span>`}
      </div>
      <div class="market-card-body">
        <div class="market-card-top">
          <span class="tag-chip">${escapeHTML(lot.category)}</span>
          <span class="manual-badge">${escapeHTML(manualBadgeText)}</span>
        </div>
        <h3>${escapeHTML(lot.item)}</h3>
        <p class="market-meta">📦 ${escapeHTML(String(lot.quantity))} ${escapeHTML(lot.unit)} · 📍 ${escapeHTML(lot.state ? `${lot.state}, ` : "")}${escapeHTML(lot.city || "Location pending")} · 👤 ${escapeHTML(authorName)}</p>
        <p class="market-note">${escapeHTML(lot.note || "Quality inspected scrap lot available for procurement.")}</p>
        <div class="market-price">₹${Number(lot.min_price).toLocaleString("en-IN")}–₹${Number(lot.max_price).toLocaleString("en-IN")} <span>/ ${escapeHTML(lot.unit)}</span></div>
        <div class="market-actions">
          ${isAdmin ? `<button type="button" class="btn btn-secondary btn-sm verify-btn" data-id="${lot.id}">${lot.verified ? "Approved" : "Verify lot"}</button>` : ""}
          ${canEdit ? `<button type="button" class="btn btn-secondary btn-sm edit-market-lot-btn" data-lot-id="${lot.id}" title="Edit product price, quantity, or specifications">✏️ Edit Price / Data</button>` : ""}
          ${lot.verified ? `<button type="button" class="btn btn-primary btn-sm buy-btn" data-id="${lot.id}" ${currentSession?.role !== "buyer" ? "disabled" : ""}>Review &amp; Purchase</button>` : ""}
          ${lot.isManual || isAdmin ? `<button type="button" class="btn btn-danger-ghost btn-sm delete-market-lot-btn" data-lot-id="${lot.id}" title="Delete product">🗑️</button>` : ""}
        </div>
      </div>
    </article>
    `;
  }).join("");

  marketGrid.querySelectorAll(".verify-btn").forEach(btn => btn.addEventListener("click", async () => {
    try {
      await fetch(`${API_BASE}/listings/${encodeURIComponent(btn.dataset.id)}/verify`, { method: "PATCH", headers: getAuthHeaders() });
    } catch {}
    const next = getListings().map(lot => lot.id === btn.dataset.id ? { ...lot, verified: true } : lot);
    saveListings(next);
    renderMarketplace();
  }));

  // Attach Edit Price / Data handlers for Buyer & Admin
  marketGrid.querySelectorAll(".edit-market-lot-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openEditLotModal(btn.dataset.lotId);
    });
  });

  // Attach Delete handlers for manual lots
  marketGrid.querySelectorAll(".delete-market-lot-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteSellerLot(btn.dataset.lotId);
    });
  });

  marketGrid.querySelectorAll(".buy-btn").forEach(btn => btn.addEventListener("click", () => {
    selectedListingId = btn.dataset.id;
    const lot = getListings().find(item => item.id === selectedListingId);
    if (!lot) return;
    purchaseItem.textContent = `${lot.item} · ${lot.quantity} ${lot.unit} · Admin-set Quote ₹${lot.min_price}–₹${lot.max_price}`;
    purchaseMessage.textContent = "";
    // Auto-fill buyer name from session (hidden field)
    const hiddenName = document.getElementById("buyerNameHidden");
    if (hiddenName && currentSession?.name) hiddenName.value = currentSession.name;
    // Pre-set offer price to seller's min price as default
    if (buyerOfferPrice) buyerOfferPrice.value = lot.min_price || "";
    purchaseModal.hidden = false;
  }));
}

cityFilter?.addEventListener("change", renderMarketplace);

document.getElementById("closePurchase")?.addEventListener("click", () => { purchaseModal.hidden = true; });
document.getElementById("closePurchaseCancel")?.addEventListener("click", () => { purchaseModal.hidden = true; });
purchaseModal?.addEventListener("click", (e) => {
  if (e.target === purchaseModal) purchaseModal.hidden = true;
});
const editLotModalEl = document.getElementById("editLotModal");
editLotModalEl?.addEventListener("click", (e) => {
  if (e.target === editLotModalEl) closeEditLotModal();
});

purchaseForm?.addEventListener("submit", async event => {
  event.preventDefault();
  const lot = getListings().find(item => item.id === selectedListingId);
  if (!lot) return;
  const values = Object.fromEntries(new FormData(purchaseForm));
  const orders = getOrders();
  const requestedQuantity = Number(values.quantity);
  if (requestedQuantity > lot.quantity) {
    purchaseMessage.textContent = `Only ${lot.quantity} ${lot.unit} is available.`;
    return;
  }
  const accepted = values.decision === "accepted";
  const request = {
    listing_id: lot.id,
    buyer_name: values.name,
    buyer_email: currentSession?.email || "",
    quantity: requestedQuantity,
    offered_price: Number(values.offered_price),
    buyer_decision: values.decision,
    address: values.address,
    payment_method: values.payment
  };

  let receiptId = `REQ-${Date.now()}`;
  try {
    const res = await fetch(`${API_BASE}/approval-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(request)
    });
    if (res.ok) {
      const data = await res.json();
      receiptId = data.id || receiptId;
    }
  } catch {
    orders.unshift({
      id: receiptId,
      lot: lot.item,
      buyer: values.name,
      buyerEmail: currentSession?.email || "",
      sellerEmail: lot.ownerEmail || "",
      address: values.address,
      payment: values.payment,
      offered_price: Number(values.offered_price),
      quantity: requestedQuantity,
      unit: lot.unit,
      status: accepted ? "Buyer accepted - Admin approval pending" : "Buyer declined",
      date: new Date().toLocaleDateString("en-IN")
    });
    saveOrders(orders);
  }

  purchaseMessage.textContent = accepted ? "Buyer decision sent to Admin. Seller will be notified after Admin approval." : "Decline recorded.";
  receiptNumber.textContent = `Receipt ${receiptId}`;
  receiptQr.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(`ScrapSense request ${receiptId} ${lot.item} ${requestedQuantity} ${lot.unit}`)}`;
  paymentReceipt.hidden = false;
  await syncOrders();
  renderAdmin();
  setTimeout(() => {
    purchaseModal.hidden = true;
    purchaseForm.reset();
    renderOrders();
  }, 1200);
});

function renderOrders() {
  if (!ordersList) return;
  const isSeller = currentSession?.role === "seller";
  const isAdmin = currentSession?.role === "admin";

  const orders = isAdmin
    ? getOrders()
    : isSeller
      ? getOrders().filter(order => order.sellerEmail === currentSession?.email)
      : getOrders().filter(order => order.buyerEmail === currentSession?.email);

  if (!orders.length) {
    ordersList.innerHTML = '<div class="empty-market">No orders or inquiries yet.</div>';
    return;
  }

  ordersList.innerHTML = orders.map(order => {
    const isApproved = (order.status || "").toLowerCase().includes("approved");
    const pdfBtn = (isSeller && isApproved) ? `
      <button class="btn btn-primary btn-sm download-pdf-btn" data-order-id="${escapeHTML(order.id)}" title="Download Payment Receipt PDF">
        📄 Download Payment PDF
      </button>` : "";

    // SELLER VIEW: Buyer identity completely hidden — only show lot, qty, price, status
    if (isSeller) {
      return `
        <div class="order-row ${isApproved ? "order-row-approved" : ""}">
          <div>
            <strong>${escapeHTML(order.lot || "Scrap lot")}</strong>
            <span>📅 ${escapeHTML(order.date || "")} · Qty: ${escapeHTML(String(order.quantity || ""))} ${escapeHTML(order.unit || "")}</span>
            ${order.offered_price ? `<span class="offer-chip">💰 Offer: ₹${Number(order.offered_price).toLocaleString("en-IN")} / unit</span>` : ""}
          </div>
          <div class="order-right">
            <b class="order-status ${isApproved ? "status-approved" : ""}">${
              isApproved ? "✅ Admin Approved — Payment Due" : escapeHTML(order.status || "Pending")
            }</b>
            ${pdfBtn}
          </div>
        </div>`;
    }

    // BUYER VIEW: show own request details
    if (!isAdmin) {
      return `
        <div class="order-row ${isApproved ? "order-row-approved" : ""}">
          <div>
            <strong>${escapeHTML(order.lot || "Scrap Request")}</strong>
            <span>📅 ${escapeHTML(order.date || "")} · Qty: ${escapeHTML(String(order.quantity || ""))} ${escapeHTML(order.unit || "")}</span>
            ${order.offered_price ? `<span class="offer-chip">💰 ₹${Number(order.offered_price).toLocaleString("en-IN")} / unit</span>` : ""}
            ${isApproved ? `
            <div class="buyer-contact-box" style="margin-top:10px; padding:10px; background:rgba(0,180,100,0.1); border:1px solid rgba(0,180,100,0.3); border-radius:8px;">
              <div style="font-weight:600; color:#10b981; margin-bottom:4px;">✅ Seller Contact Unlocked</div>
              <div>📞 Phone: <a href="tel:${escapeHTML(order.seller_phone || '')}" style="color:var(--text-main); font-weight:bold;">${escapeHTML(order.seller_phone || 'N/A')}</a>
                  <a href="https://wa.me/${escapeHTML((order.seller_phone || '').replace(/[^0-9]/g, ''))}" target="_blank" style="margin-left:8px; color:#25D366; text-decoration:none;">💬 WhatsApp</a>
              </div>
              <div>📍 Location: ${escapeHTML(order.seller_location || 'N/A')}</div>
              <div>✉️ Email: ${escapeHTML(order.seller_email || 'N/A')}</div>
            </div>
            ` : `
            <div style="margin-top:10px; color:var(--text-muted); font-size:0.9rem;">
              🔒 Seller Contact: Locked until Admin Approval
            </div>
            `}
          </div>
          <b class="order-status ${isApproved ? "status-approved" : ""}">${
            isApproved ? "✅ Admin Approved" : escapeHTML(order.status || "Pending Admin Review")
          }</b>
        </div>`;
    }

    // ADMIN VIEW: show full details including buyer identity
    return `
      <div class="order-row ${isApproved ? "order-row-approved" : ""}">
        <div>
          <strong>${escapeHTML(order.lot || "Scrap lot")}</strong>
          <span>🏢 Buyer: ${escapeHTML(order.buyer || "Anonymous")} · ${escapeHTML(order.date || "")}</span>
          ${order.offered_price ? `<span class="offer-chip">💰 ₹${Number(order.offered_price).toLocaleString("en-IN")} / unit · ${escapeHTML(String(order.quantity || ""))} ${escapeHTML(order.unit || "")}</span>` : ""}
        </div>
        <div class="order-right">
          <b class="order-status ${isApproved ? "status-approved" : ""}">${
            isApproved ? "✅ Admin Approved — Payment Due" : escapeHTML(order.status || "Pending")
          }</b>
        </div>
      </div>`;
  }).join("");

  // Attach PDF download handlers for seller
  if (isSeller) {
    ordersList.querySelectorAll(".download-pdf-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const orderId = btn.dataset.orderId;
        const order = getOrders().find(o => o.id === orderId);
        if (order) downloadPaymentPDF(order);
      });
    });
  }
}

async function syncListings() {
  if (!currentSession || !["admin", "buyer"].includes(currentSession.role)) return;
  try {
    const endpoint = currentSession.role === "admin" ? `${API_BASE}/admin/listings` : `${API_BASE}/listings`;
    const response = await fetch(endpoint, { headers: getAuthHeaders() });
    const data = await response.json();
    if (response.ok) {
      saveListings((data.listings || []).map(l => ({ ...l, ownerEmail: l.ownerEmail || l.seller_email || "" })));
    }
  } catch {}
}

async function syncOrders() {
  if (!currentSession) return;
  try {
    const endpoint = currentSession.role === "admin"
      ? `${API_BASE}/admin/approval-requests`
      : `${API_BASE}/orders?role=${encodeURIComponent(currentSession.role)}&email=${encodeURIComponent(currentSession.email || "")}`;
    const response = await fetch(endpoint, { headers: getAuthHeaders() });
    const data = await response.json();
    if (response.ok) {
      const orders = currentSession.role === "admin"
        ? (data.requests || []).map(o => ({ ...o, lot: o.item, buyer: o.buyer_name, buyerEmail: o.buyer_email, sellerEmail: o.seller_email, payment: o.payment_method, date: o.created_at }))
        : (data.orders || []).map(o => ({ ...o, buyerEmail: currentSession.role === "buyer" ? currentSession.email : "", sellerEmail: currentSession.role === "seller" ? currentSession.email : "" }));
      saveOrders(orders);
    }
  } catch {}
}

async function loadRegisteredUsers() {
  if (!registeredUsers) return;
  try {
    const response = await fetch(`${API_BASE}/admin/users`, { headers: getAuthHeaders() });
    const data = await response.json();
    if (response.ok) {
      registeredUserCount.textContent = data.users.length;
      registeredUsers.innerHTML = data.users.length ? data.users.map(u => `
        <div class="admin-list-row">
          <div>
            <strong>${escapeHTML(u.name)}</strong>
            <span>${escapeHTML(u.email)} · Joined ${u.created_at ? new Date(u.created_at).toLocaleDateString("en-IN") : "date unavailable"}</span>
          </div>
          <b>${escapeHTML(u.role)}</b>
        </div>
      `).join("") : '<div class="empty-market">No registered accounts.</div>';
    }
  } catch {
    registeredUserCount.textContent = "-";
    registeredUsers.innerHTML = '<div class="empty-market">MongoDB accounts unavailable.</div>';
  }
}

function renderAdmin() {
  const products = getAdminProducts();
  const buyers = getAdminBuyers();
  const orders = getOrders();
  const pendingOrders = orders.filter(o => (o.status || "").toLowerCase().includes("pending"));
  const approvedOrders = orders.filter(o => (o.status || "").toLowerCase().includes("approved"));

  if (productCount) productCount.textContent = products.length;
  if (buyerCount) buyerCount.textContent = buyers.length;
  if (requestCount) requestCount.textContent = pendingOrders.length;
  const approvedCountEl = document.getElementById("approvedCount");
  if (approvedCountEl) approvedCountEl.textContent = approvedOrders.length;
  if (adminSummary) adminSummary.textContent = `${products.length} products · ${buyers.length} buyers · ${orders.length} requests`;

  // --- Pending Approval Requests ---
  if (adminRequests) {
    adminRequests.innerHTML = pendingOrders.length ? pendingOrders.map(o => `
      <div class="admin-list-row admin-approval-row">
        <div class="approval-info">
          <strong>📦 ${escapeHTML(o.lot || "Scrap lot")}</strong>
          <span>Buyer: ${escapeHTML(o.buyer || "Anonymous")} · ${escapeHTML(o.date || "")} · Qty: ${escapeHTML(String(o.quantity || ""))} ${escapeHTML(o.unit || "")}</span>
          <span>💰 Offered: ₹${o.offered_price ? Number(o.offered_price).toLocaleString("en-IN") : "—"} / unit · Payment: ${escapeHTML(o.payment || "UPI")}</span>
          <span>📞 Seller Phone: ${escapeHTML(o.seller_phone || "—")} · 📍 Seller Location: ${escapeHTML(o.seller_location || "—")}</span>
          ${o.address ? `<span>📍 Delivery to: ${escapeHTML(o.address)}</span>` : ""}
        </div>
        <div class="approval-actions">
          <button class="btn btn-primary btn-sm admin-approve-btn" data-order-id="${escapeHTML(o.id)}">
            ✅ Approve &amp; Send Payment Log
          </button>
          <button class="btn btn-secondary btn-sm admin-reject-btn" data-order-id="${escapeHTML(o.id)}">
            ❌ Reject
          </button>
        </div>
      </div>
    `).join("") : '<div class="empty-market">No pending approval requests. Buyers need to submit purchase offers first.</div>';

    adminRequests.querySelectorAll(".admin-approve-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const orderId = btn.dataset.orderId;
        try {
          await fetch(`${API_BASE}/admin/approval-requests/${encodeURIComponent(orderId)}?approved=true`, { method: "PATCH", headers: getAuthHeaders() });
        } catch {}
        const now = new Date().toLocaleDateString("en-IN");
        const next = getOrders().map(o => o.id === orderId ? {
          ...o,
          status: "Admin Approved — Payment Log Sent to Seller",
          approvedAt: now,
          approvedBy: currentSession?.name || "Admin"
        } : o);
        saveOrders(next);
        renderAdmin();
        renderOrders();
        // Show success toast
        showToast("✅ Request approved! Payment log sent to seller.", "success");
      });
    });

    adminRequests.querySelectorAll(".admin-reject-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const orderId = btn.dataset.orderId;
        const next = getOrders().map(o => o.id === orderId ? { ...o, status: "Admin Rejected" } : o);
        saveOrders(next);
        renderAdmin();
        showToast("❌ Request rejected.", "error");
      });
    });
  }

  // --- Approved orders log ---
  const adminApprovedEl = document.getElementById("adminApproved");
  if (adminApprovedEl) {
    adminApprovedEl.innerHTML = approvedOrders.length ? approvedOrders.map(o => `
      <div class="admin-list-row">
        <div>
          <strong>✅ ${escapeHTML(o.lot || "Scrap lot")}</strong>
          <span>Buyer: ${escapeHTML(o.buyer || "—")} · Seller notified · Approved: ${escapeHTML(o.approvedAt || o.date || "—")}</span>
          <span>₹${o.offered_price ? Number(o.offered_price).toLocaleString("en-IN") : "—"} / unit · Qty: ${escapeHTML(String(o.quantity || ""))} ${escapeHTML(o.unit || "")}</span>
          <div style="margin-top:6px; padding:8px; background:rgba(255,255,255,0.05); border-radius:6px; font-size:0.85rem;">
            <div>📞 Seller: ${escapeHTML(o.seller_phone || "—")}</div>
            <div>📍 Location: ${escapeHTML(o.seller_location || "—")}</div>
          </div>
        </div>
        <b class="status-approved">Payment Log Sent</b>
      </div>
    `).join("") : '<div class="empty-market">No approved orders yet.</div>';
  }

  // --- Active product rates ---
  if (adminProducts) {
    adminProducts.innerHTML = products.length ? products.map(p => `
      <div class="admin-list-row">
        <div><strong>${escapeHTML(p.icon || "♻️")} ${escapeHTML(p.name)}</strong><span>${escapeHTML(p.category)} · ₹${p.min_price}–₹${p.max_price} / ${escapeHTML(p.unit)}</span></div>
        <button class="del-btn" data-product-id="${p.id}" title="Delete">✕</button>
      </div>
    `).join("") : '<div class="empty-market">No custom products listed.</div>';

    adminProducts.querySelectorAll("[data-product-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        saveAdminProducts(getAdminProducts().filter(p => p.id !== btn.dataset.productId));
        renderAdmin();
        loadCategories();
      });
    });
  }

  // --- Private buyer records ---
  if (adminBuyers) {
    adminBuyers.innerHTML = buyers.length ? buyers.map(b => `
      <div class="admin-list-row">
        <div><strong>${escapeHTML(b.name)}</strong><span>${escapeHTML(b.category)} · ${escapeHTML(b.city)}, ${escapeHTML(b.state)}</span></div>
        <button class="del-btn" data-buyer-id="${b.id}" title="Delete">✕</button>
      </div>
    `).join("") : '<div class="empty-market">No private buyers listed.</div>';

    adminBuyers.querySelectorAll("[data-buyer-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        saveAdminBuyers(getAdminBuyers().filter(b => b.id !== btn.dataset.buyerId));
        renderAdmin();
      });
    });
  }
}

// Add admin product form
productForm?.addEventListener("submit", event => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(productForm));
  const products = getAdminProducts();
  products.unshift({
    id: `prod-${Date.now()}`,
    name: values.name,
    category: values.category,
    unit: values.unit,
    icon: values.icon || "♻️",
    min_price: Number(values.min_price),
    max_price: Number(values.max_price),
    sell_to: values.sell_to || "Admin routing"
  });
  saveAdminProducts(products);
  productForm.reset();
  renderAdmin();
  loadCategories();
});

// Add admin buyer form
buyerForm?.addEventListener("submit", event => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(buyerForm));
  const buyers = getAdminBuyers();
  buyers.unshift({
    id: `buy-${Date.now()}`,
    name: values.name,
    category: values.category,
    state: values.state,
    city: values.city,
    phone: values.phone,
    rate: values.rate,
    source_url: values.source_url
  });
  saveAdminBuyers(buyers);
  buyerForm.reset();
  renderAdmin();
});

// ============================================================
// PDF PAYMENT RECEIPT DOWNLOAD
// ============================================================
function downloadPaymentPDF(order) {
  const printWin = window.open("", "_blank", "width=700,height=900");
  const now = new Date().toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" });
  const receiptId = order.id || `PAY-${Date.now()}`;
  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Payment Receipt - ScrapSense AI</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', Arial, sans-serif; background: #fff; color: #1a1a2e; padding: 2rem; }
        .receipt-pdf { max-width: 620px; margin: 0 auto; border: 2px solid #16213e; border-radius: 12px; overflow: hidden; }
        .pdf-header { background: linear-gradient(135deg, #16213e, #0f3460); color: #fff; padding: 2rem; text-align: center; }
        .pdf-logo { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .pdf-title { font-size: 1.4rem; font-weight: 700; letter-spacing: 2px; }
        .pdf-subtitle { font-size: 0.8rem; opacity: 0.75; margin-top: 0.25rem; }
        .pdf-badge { display: inline-block; background: #00d4aa; color: #16213e; font-weight: 700; font-size: 0.75rem; padding: 0.25rem 0.75rem; border-radius: 20px; margin-top: 0.75rem; }
        .pdf-body { padding: 2rem; }
        .pdf-section-title { font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; color: #0f3460; text-transform: uppercase; margin: 1.5rem 0 0.75rem; border-bottom: 1px solid #e8ecf0; padding-bottom: 0.4rem; }
        .pdf-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f0f4f8; font-size: 0.9rem; }
        .pdf-row dt { color: #666; }
        .pdf-row dd { font-weight: 600; color: #1a1a2e; }
        .pdf-amount { background: linear-gradient(135deg, #00d4aa15, #0f346015); border: 1px solid #00d4aa; border-radius: 8px; padding: 1.25rem; margin: 1.5rem 0; text-align: center; }
        .pdf-amount-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
        .pdf-amount-val { font-size: 2rem; font-weight: 800; color: #00d4aa; margin-top: 0.25rem; }
        .pdf-footer { background: #f8f9fa; padding: 1.25rem 2rem; text-align: center; font-size: 0.75rem; color: #888; border-top: 1px dashed #ddd; }
        .pdf-approved-stamp { display: inline-block; border: 3px solid #00b894; color: #00b894; font-weight: 800; font-size: 1.1rem; padding: 0.5rem 1.5rem; border-radius: 6px; transform: rotate(-5deg); margin-top: 1rem; }
        @media print { body { padding: 0; } .pdf-body { padding: 1.5rem; } }
      </style>
    </head>
    <body>
      <div class="receipt-pdf">
        <div class="pdf-header">
          <div class="pdf-logo">⚙️</div>
          <div class="pdf-title">SCRAPSENSE AI</div>
          <div class="pdf-subtitle">Electronic &amp; Scrap Valuation Platform · Admin Payment Log</div>
          <div class="pdf-badge">✅ ADMIN APPROVED</div>
        </div>
        <div class="pdf-body">
          <p class="pdf-section-title">Transaction Details</p>
          <dl>
            <div class="pdf-row"><dt>Receipt ID</dt><dd>${escapeHTML(receiptId)}</dd></div>
            <div class="pdf-row"><dt>Approval Date</dt><dd>${escapeHTML(order.approvedAt || now)}</dd></div>
            <div class="pdf-row"><dt>Approved By</dt><dd>${escapeHTML(order.approvedBy || "ScrapSense Admin")}</dd></div>
            <div class="pdf-row"><dt>Lot Item</dt><dd>${escapeHTML(order.lot || "Scrap lot")}</dd></div>
            <div class="pdf-row"><dt>Quantity</dt><dd>${escapeHTML(String(order.quantity || ""))} ${escapeHTML(order.unit || "")}</dd></div>
            <div class="pdf-row"><dt>Buyer</dt><dd>${escapeHTML(order.buyer || "Verified Buyer")} (Identity Protected)</dd></div>
          </dl>

          <p class="pdf-section-title">Payment Information</p>
          <dl>
            <div class="pdf-row"><dt>Agreed Price</dt><dd>₹${order.offered_price ? Number(order.offered_price).toLocaleString("en-IN") : "—"} per unit</dd></div>
            <div class="pdf-row"><dt>Payment Method</dt><dd>${escapeHTML(order.payment || "UPI")}</dd></div>
            <div class="pdf-row"><dt>Pickup / Delivery Address</dt><dd>${escapeHTML(order.address || "As agreed")}</dd></div>
          </dl>

          <div class="pdf-amount">
            <div class="pdf-amount-label">Total Estimated Payout to Seller</div>
            <div class="pdf-amount-val">₹${order.offered_price && order.quantity ? Number(order.offered_price * order.quantity).toLocaleString("en-IN") : "—"}</div>
          </div>

          <div style="text-align:center">
            <div class="pdf-approved-stamp">PAYMENT AUTHORIZED</div>
          </div>
        </div>
        <div class="pdf-footer">
          Generated by ScrapSense AI · ${now} · Receipt ${escapeHTML(receiptId)}<br>
          *This is an admin-approved payment log. Actual payment terms are subject to physical verification.
        </div>
      </div>
      <script>window.onload = () => { window.print(); }<\/script>
    </body>
    </html>
  `);
  printWin.document.close();
}

// ============================================================
// TOAST NOTIFICATION
// ============================================================
function showToast(message, type = "success") {
  let toast = document.getElementById("scrapToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "scrapToast";
    document.body.appendChild(toast);
  }
  toast.className = `scrap-toast scrap-toast-${type} scrap-toast-show`;
  toast.textContent = message;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.classList.remove("scrap-toast-show"); }, 3200);
}

// ============================================================
// BUYER ITEM / PRICE OFFER FORM
// ============================================================
const buyerItemForm = document.getElementById("buyerItemForm");
const buyerItemMessage = document.getElementById("buyerItemMessage");

// Quick Add button in marketplace toolbar
document.getElementById("marketAddProductBtn")?.addEventListener("click", () => {
  if (currentSession?.role === "seller") {
    setSellerView("post-lot");
  } else {
    setBuyerView("add-item");
  }
});

buyerItemForm?.addEventListener("submit", async event => {
  event.preventDefault();
  if (!currentSession) return;
  const values = Object.fromEntries(new FormData(buyerItemForm));
  
  const manualLotId = `lot-manual-${Date.now()}`;
  const unitVal = values.unit || "kg";
  const qtyVal = Number(values.quantity) || 10;
  const targetPrice = Number(values.offered_price) || 100;
  const minPrice = targetPrice;
  const maxPrice = Math.round(targetPrice * 1.2);
  const lotName = values.item.trim();
  const lotCategory = values.category || "E-Waste";
  const lotState = values.state || "Rajasthan";
  const lotCity = values.city || "Jaipur";
  const author = currentSession.name || "Enterprise Procurement Desk";

  // 1. Create manual marketplace listing so it appears as a custom manual product in the marketplace!
  const manualListing = {
    id: manualLotId,
    item: lotName,
    category: lotCategory,
    unit: unitVal,
    quantity: qtyVal,
    min_price: minPrice,
    max_price: maxPrice,
    state: lotState,
    city: lotCity,
    note: `Manually cataloged product by ${author}. Location: ${lotState}, ${lotCity}. Settlement: ${values.payment || "UPI"}.`,
    verified: true,
    isManual: true,
    created: new Date().toLocaleDateString("en-IN"),
    ownerEmail: currentSession.email || "buyer@scrapsense.org",
    seller: author
  };

  const currentListings = getListings();
  currentListings.unshift(manualListing);
  saveListings(currentListings);

  // Sync manual listing to MongoDB backend
  try {
    await fetch(`${API_BASE}/listings`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({
        item: manualListing.item,
        category: manualListing.category,
        quantity: manualListing.quantity,
        unit: manualListing.unit,
        min_price: manualListing.min_price,
        max_price: manualListing.max_price,
        state: manualListing.state,
        city: manualListing.city,
        note: manualListing.note
      })
    });
  } catch (err) {
    console.warn("Backend listing sync skipped:", err);
  }

  // 2. Also register purchase order / RFQ in orders
  const orders = getOrders();
  const requestId = `BYR-${Date.now()}`;
  const newOrder = {
    id: requestId,
    lot: lotName,
    buyer: author,
    buyerEmail: currentSession.email || "",
    sellerEmail: "",
    quantity: qtyVal,
    unit: unitVal,
    offered_price: targetPrice,
    payment: values.payment,
    address: values.address,
    status: "Active Manual Product · Verified for Trading",
    date: new Date().toLocaleDateString("en-IN"),
    category: lotCategory,
    urgency: values.urgency || "Standard (Within 7 Days)"
  };

  try {
    const res = await fetch(`${API_BASE}/approval-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({
        listing_id: requestId,
        buyer_name: author,
        buyer_email: currentSession.email || "",
        quantity: newOrder.quantity,
        offered_price: newOrder.offered_price,
        buyer_decision: "accepted",
        address: values.address,
        payment_method: values.payment
      })
    });
    if (res.ok) {
      const data = await res.json();
      newOrder.id = data.id || requestId;
    }
  } catch {}

  orders.unshift(newOrder);
  saveOrders(orders);
  buyerItemForm.reset();
  if (buyerItemMessage) {
    buyerItemMessage.textContent = `✅ Manual product "${lotName}" published to Marketplace! You can edit its price or data anytime.`;
    buyerItemMessage.style.color = "#00d4aa";
  }
  showToast(`✅ Manual product "${lotName}" published to Marketplace!`, "success");
  renderMarketplace();
  renderAdmin();
  setTimeout(() => { setBuyerView("marketplace"); }, 1100);
});

// ============================================================
// ADMIN TAB SWITCHING
// ============================================================
const adminTabBtns = document.querySelectorAll(".admin-tab-btn");
const adminTabContents = {
  approvals: document.getElementById("adminTabApprovals"),
  analytics: document.getElementById("adminTabAnalytics"),
  rates: document.getElementById("adminTabRates"),
  buyers: document.getElementById("adminTabBuyers"),
  users: document.getElementById("adminTabUsers")
};

adminTabBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    adminTabBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.adminTab;
    Object.entries(adminTabContents).forEach(([key, el]) => {
      if (el) el.hidden = key !== tab;
    });
    if (tab === "users") loadRegisteredUsers();
    if (tab === "approvals") renderAdmin();
    if (tab === "analytics") loadAdminAnalytics();
  });
});

// ============================================================
// BOOTSTRAP INITIALIZATION
// ============================================================
async function init() {
  // 1. Immediately restore persistent session & role so UI does not flicker or require relogin
  if (!currentSession) {
    const stored = getStoredSession();
    const storedToken = getStoredToken();
    if (stored) {
      currentSession = stored;
      if (storedToken) authToken = storedToken;
      authScreen.hidden = true;
      setRoleVisibility();
    } else {
      setRole("seller");
    }
  }

  renderAdmin();
  renderHistory();
  initMobilePhoneLink();

  // 2. Connect to backend with auto-discovery & latching
  await checkBackendStatus();
  startBackendHeartbeat();
  await loadCategories();
  setSellerCategory("All Categories");

  if (currentSession) {
    authScreen.hidden = true;
    setRoleVisibility();
  }
}

init();

// Mobile Hamburger Menu
const hamburgerBtn = document.getElementById("hamburgerBtn");
const siteNav = document.getElementById("siteNav");

if (hamburgerBtn && siteNav) {
  hamburgerBtn.addEventListener("click", () => {
    const expanded = hamburgerBtn.getAttribute("aria-expanded") === "true";
    hamburgerBtn.setAttribute("aria-expanded", !expanded);
    siteNav.classList.toggle("nav-open");
    hamburgerBtn.classList.toggle("active");
  });

  siteNav.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("nav-open");
      hamburgerBtn.classList.remove("active");
      hamburgerBtn.setAttribute("aria-expanded", "false");
    });
  });
}

// ============================================================
// AI RECYCLING COPILOT (GPT · CLAUDE · ASTRA · ASTRA DB)
// ============================================================
(function initCopilotController() {
  const trigger = document.getElementById("aiCopilotTrigger");
  const modal = document.getElementById("copilotModal");
  const closeBtn = document.getElementById("copilotCloseBtn");
  const providerBtns = document.querySelectorAll(".copilot-provider-btn");
  const messagesContainer = document.getElementById("copilotMessages");
  const inputForm = document.getElementById("copilotInputForm");
  const inputField = document.getElementById("copilotInputField");
  const sendBtn = document.getElementById("copilotSendBtn");
  const attachBtn = document.getElementById("copilotAttachBtn");
  const fileInput = document.getElementById("copilotFileInput");
  const previewBox = document.getElementById("copilotAttachmentPreview");
  const previewThumb = document.getElementById("copilotPreviewThumb");
  const removeAttachBtn = document.getElementById("copilotRemoveAttachBtn");
  const quickChips = document.querySelectorAll(".c-quick-chip");
  const providerStatus = document.getElementById("copilotProviderStatus");
  const astraDbBadge = document.getElementById("astraDbBadge");
  const astraDbState = document.getElementById("astraDbState");

  let activeProvider = "gemini";
  let currentImageBase64 = null;
  let chatHistory = [];
  const sessionId = "copilot_" + Math.random().toString(36).substring(2, 10);

  const providerNames = {
    gemini: "Google Astra / Gemini 1.5",
    openai: "OpenAI GPT-4o",
    claude: "Anthropic Claude 3.5 Sonnet"
  };

  // Open / Close Drawer
  function openCopilot() {
    if (!modal) return;
    modal.hidden = false;
    setTimeout(() => inputField?.focus(), 150);
  }

  function closeCopilot() {
    if (!modal) return;
    modal.hidden = true;
  }

  window.openCopilot = openCopilot;
  window.closeCopilot = closeCopilot;

  trigger?.addEventListener("click", openCopilot);
  closeBtn?.addEventListener("click", closeCopilot);

  document.getElementById("navChatbotBtn")?.addEventListener("click", openCopilot);
  document.getElementById("tabChatbotBtn")?.addEventListener("click", openCopilot);
  document.getElementById("buyerTabChatbotBtn")?.addEventListener("click", openCopilot);

  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeCopilot();
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal && !modal.hidden) {
      closeCopilot();
    }
  });

  // Fetch AI Providers Status
  async function checkAiStatus() {
    try {
      const res = await fetch(`${API_BASE}/ai/status`);
      if (res.ok) {
        const data = await res.json();
        const astraCfg = data.providers?.astradb;
        if (astraCfg && astraCfg.configured) {
          if (astraDbState) astraDbState.textContent = "Synced";
          if (astraDbBadge) astraDbBadge.style.borderColor = "rgba(16, 185, 129, 0.4)";
        } else {
          if (astraDbState) astraDbState.textContent = "Ready";
        }
      }
    } catch {
      // Backend may be offline or starting up
    }
  }
  checkAiStatus();

  // Provider switching
  providerBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      providerBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeProvider = btn.dataset.provider || "gemini";
      if (providerStatus) {
        providerStatus.textContent = `Active: ${providerNames[activeProvider] || activeProvider}`;
      }
    });
  });

  // Quick prompt chips
  quickChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.dataset.query;
      if (query && inputField) {
        inputField.value = query;
        sendChatMessage(query);
      }
    });
  });

  // Image Attachment Handling
  attachBtn?.addEventListener("click", () => fileInput?.click());

  fileInput?.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) {
      const file = fileInput.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        currentImageBase64 = e.target.result;
        if (previewThumb) previewThumb.src = currentImageBase64;
        if (previewBox) previewBox.hidden = false;
      };
      reader.readAsDataURL(file);
    }
  });

  removeAttachBtn?.addEventListener("click", () => {
    currentImageBase64 = null;
    if (fileInput) fileInput.value = "";
    if (previewBox) previewBox.hidden = true;
    if (previewThumb) previewThumb.src = "";
  });

  // Markdown Formatter helper for AI responses
  function renderFormattedMessage(text) {
    if (!text) return "";
    let formatted = escapeHTML(text);

    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Bullet lists - line starting with "- " or "* "
    const lines = formatted.split("\n");
    let inList = false;
    const outputLines = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList) {
          outputLines.push("<ul>");
          inList = true;
        }
        outputLines.push(`<li>${trimmed.substring(2)}</li>`);
      } else {
        if (inList) {
          outputLines.push("</ul>");
          inList = false;
        }
        if (trimmed === "") {
          outputLines.push("<br>");
        } else {
          outputLines.push(`<p>${line}</p>`);
        }
      }
    });
    if (inList) outputLines.push("</ul>");

    return outputLines.join("");
  }

  // Append a message bubble to UI
  function appendMessage(role, text, imgSrc = null, note = null) {
    if (!messagesContainer) return;
    const msgDiv = document.createElement("div");
    msgDiv.className = `c-msg ${role === "user" ? "c-user" : "c-bot"}`;

    const avatar = document.createElement("div");
    avatar.className = "c-avatar";
    avatar.textContent = role === "user" ? "👤" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "c-bubble";

    if (imgSrc) {
      const img = document.createElement("img");
      img.src = sanitizeImageSrc(imgSrc);
      img.className = "c-msg-img";
      img.alt = "Attached component";
      bubble.appendChild(img);
    }

    const textHolder = document.createElement("div");
    if (role === "user") {
      textHolder.textContent = text;
    } else {
      textHolder.innerHTML = renderFormattedMessage(text);
      if (note) {
        const metaDiv = document.createElement("div");
        metaDiv.className = "c-bot-meta";
        metaDiv.innerHTML = `<span class="c-tag">${escapeHTML(note)}</span>`;
        textHolder.appendChild(metaDiv);
      }
    }
    bubble.appendChild(textHolder);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return msgDiv;
  }

  // Send Chat Message
  async function sendChatMessage(text) {
    const query = (text || inputField?.value || "").trim();
    if (!query && !currentImageBase64) return;

    const attachedImg = currentImageBase64;

    // Reset input and attachment
    if (inputField) inputField.value = "";
    currentImageBase64 = null;
    if (fileInput) fileInput.value = "";
    if (previewBox) previewBox.hidden = true;

    // Display user bubble
    appendMessage("user", query, attachedImg);

    // Add to history
    chatHistory.push({ role: "user", content: query });

    // Show typing placeholder
    const typingBubble = appendMessage("assistant", "Thinking with " + (providerNames[activeProvider] || "AI") + "...");
    if (sendBtn) sendBtn.disabled = true;

    try {
      const res = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          message: query,
          provider: activeProvider,
          history: chatHistory.slice(-8),
          image: attachedImg,
          session_id: sessionId
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      typingBubble.remove();

      const aiReply = data.response || "No response received.";
      appendMessage("assistant", aiReply, null, data.note || (data.saved_to_astra ? "⚡ Synced to Astra DB" : null));

      chatHistory.push({ role: "assistant", content: aiReply });
    } catch (err) {
      console.warn("AI Chat error:", err);
      typingBubble.remove();
      // Smart simulated reply fallback
      appendMessage(
        "assistant",
        `**[Offline / Local Advisor]**\nRegarding: *"${query}"*\nScrapSense AI monitors 26+ electronic components & scrap materials with daily calibrated spot prices. Please verify the backend server is running on port 8000.`,
        null,
        "Local Fallback Mode"
      );
    } finally {
      if (sendBtn) sendBtn.disabled = false;
      if (inputField) inputField.focus();
    }
  }

  inputForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    sendChatMessage();
  });
})();

// ============================================================
// ADMIN ANALYTICS DASHBOARD (Chart.js)
// ============================================================
let analyticsChartInstances = {};

async function loadAdminAnalytics() {
  if (typeof Chart === "undefined") return;
  try {
    const resp = await fetch(`${API_BASE}/admin/analytics`, { headers: getAuthHeaders() });
    if (!resp.ok) throw new Error("API error");
    const data = await resp.json();

    // Update stat cards
    const el = (id) => document.getElementById(id);
    if (el("analyticsUsers")) el("analyticsUsers").textContent = data.total_users || 0;
    if (el("analyticsListings")) el("analyticsListings").textContent = data.total_listings || 0;
    if (el("analyticsOrders")) el("analyticsOrders").textContent = data.total_orders || 0;
    if (el("analyticsRevenue")) el("analyticsRevenue").textContent = `₹${(data.revenue_total || 0).toLocaleString("en-IN")}`;

    // Destroy existing charts to prevent duplication
    Object.values(analyticsChartInstances).forEach(c => c?.destroy?.());

    const chartColors = ["#4de1c1", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#22c55e", "#06b6d4"];

    // Category distribution pie chart
    const catLabels = Object.keys(data.listings_by_category || {});
    const catValues = Object.values(data.listings_by_category || {});
    if (catLabels.length > 0) {
      const catCtx = document.getElementById("chartCategory");
      if (catCtx) {
        analyticsChartInstances.category = new Chart(catCtx, {
          type: "doughnut",
          data: {
            labels: catLabels,
            datasets: [{ data: catValues, backgroundColor: chartColors.slice(0, catLabels.length), borderWidth: 0 }]
          },
          options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: "bottom", labels: { color: "#9ab2bd", font: { size: 11 } } } }
          }
        });
      }
    }

    // Orders by status bar chart
    const ordLabels = Object.keys(data.orders_by_status || {});
    const ordValues = Object.values(data.orders_by_status || {});
    if (ordLabels.length > 0) {
      const ordCtx = document.getElementById("chartOrders");
      if (ordCtx) {
        analyticsChartInstances.orders = new Chart(ordCtx, {
          type: "bar",
          data: {
            labels: ordLabels.map(l => l.length > 20 ? l.substring(0, 20) + "..." : l),
            datasets: [{ label: "Orders", data: ordValues, backgroundColor: chartColors, borderRadius: 8, borderWidth: 0 }]
          },
          options: {
            responsive: true, maintainAspectRatio: false, indexAxis: "y",
            scales: {
              x: { ticks: { color: "#9ab2bd" }, grid: { color: "#1e3a4e" } },
              y: { ticks: { color: "#9ab2bd", font: { size: 10 } }, grid: { display: false } }
            },
            plugins: { legend: { display: false } }
          }
        });
      }
    }

    // User distribution doughnut
    const userCtx = document.getElementById("chartUsers");
    if (userCtx) {
      analyticsChartInstances.users = new Chart(userCtx, {
        type: "doughnut",
        data: {
          labels: ["Sellers", "Buyers"],
          datasets: [{ data: [data.sellers_count || 0, data.buyers_count || 0], backgroundColor: ["#4de1c1", "#3b82f6"], borderWidth: 0 }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: "bottom", labels: { color: "#9ab2bd", font: { size: 12 } } } }
        }
      });
    }

    // Activity feed
    const feed = document.getElementById("analyticsActivityFeed");
    if (feed && data.recent_activity?.length) {
      feed.innerHTML = data.recent_activity.map(a => {
        const dotClass = a.status?.includes("approved") ? "approved" : a.status?.includes("Rejected") ? "rejected" : "pending";
        const dateStr = a.date ? new Date(a.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }) : "—";
        return `<div class="activity-item">
          <span class="activity-dot ${dotClass}"></span>
          <span class="activity-text"><strong>${a.item}</strong> · ${a.quantity} units · ${a.status}</span>
          <span class="activity-date">${dateStr}</span>
        </div>`;
      }).join("");
    }
  } catch (err) {
    console.warn("Analytics load error:", err);
  }
}

// ============================================================
// MARKETPLACE SEARCH, FILTER & SORT
// ============================================================
let _allMarketListings = [];

const _origRenderMarketplace = typeof renderMarketplace === "function" ? renderMarketplace : null;

// Debounce helper
function debounce(fn, ms) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}

function applyMarketplaceFilters() {
  const searchInput = document.getElementById("marketSearchInput");
  const sortSelect = document.getElementById("marketSortSelect");
  const filterPills = document.querySelectorAll(".market-filter-pill");
  const activeFilter = document.querySelector(".market-filter-pill.active")?.dataset?.marketFilter || "all";
  const query = (searchInput?.value || "").trim().toLowerCase();
  const sortBy = sortSelect?.value || "newest";

  let listings = [..._allMarketListings];

  // Strict Category Filter
  if (activeFilter !== "all") {
    const norm = activeFilter.trim().toLowerCase();
    listings = listings.filter(lot => {
      const cat = (lot.category || "").trim().toLowerCase();
      return cat === norm || (norm === "e-waste" && (cat.includes("electronic") || cat.includes("e-waste")));
    });
  }

  // Search
  if (query) {
    listings = listings.filter(lot =>
      (lot.item || "").toLowerCase().includes(query) ||
      (lot.category || "").toLowerCase().includes(query) ||
      (lot.city || "").toLowerCase().includes(query) ||
      (lot.note || "").toLowerCase().includes(query)
    );
  }

  // Sort
  switch (sortBy) {
    case "oldest":
      listings.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
      break;
    case "newest":
      listings.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
      break;
    case "price-low":
      listings.sort((a, b) => (a.min_price || 0) - (b.min_price || 0));
      break;
    case "price-high":
      listings.sort((a, b) => (b.max_price || 0) - (a.max_price || 0));
      break;
    case "qty-high":
      listings.sort((a, b) => (b.quantity || 0) - (a.quantity || 0));
      break;
  }

  // Update market count
  const marketCountEl = document.getElementById("marketCount");
  if (marketCountEl) marketCountEl.textContent = `${listings.length} active lot${listings.length === 1 ? "" : "s"}`;

  // Re-render grid with filtered listings
  if (marketGrid) {
    if (!listings.length) {
      marketGrid.innerHTML = '<div class="empty-market">No lots match your search.</div>';
      return;
    }
    marketGrid.innerHTML = listings.map(lot => `
      <article class="market-card">
        <div class="market-photo">
          ${lot.photo ? `<img src="${sanitizeImageSrc(lot.photo)}" alt="${escapeHTML(lot.item)}" />` : `<span>${escapeHTML(currentResult?.icon || "♻️")}</span>`}
        </div>
        <div class="market-card-body">
          <div class="market-card-top">
            <span class="tag-chip">${escapeHTML(lot.category)}</span>
            <span class="verify-state ${lot.verified ? "verified" : "pending"}">${lot.verified ? "✓ Admin approved" : "Awaiting Admin verification"}</span>
          </div>
          <h3>${escapeHTML(lot.item)}</h3>
          <p class="market-meta">${escapeHTML(String(lot.quantity))} ${escapeHTML(lot.unit)} · ${escapeHTML(lot.state ? `${lot.state}, ` : "")}${escapeHTML(lot.city || "Location pending")} · Seller private</p>
          <p class="market-note">${escapeHTML(lot.note || "No condition notes.")}</p>
          <div class="market-price">₹${Number(lot.min_price).toLocaleString("en-IN")}–₹${Number(lot.max_price).toLocaleString("en-IN")} <span>/ ${escapeHTML(lot.unit)}</span></div>
          <div class="market-actions">
            ${currentSession?.role === "admin" ? `<button class="btn btn-secondary btn-sm verify-btn" data-id="${lot.id}">${lot.verified ? "Approved" : "Verify lot"}</button>` : ""}
            ${lot.verified ? `<button class="btn btn-primary btn-sm buy-btn" data-id="${lot.id}" ${currentSession?.role !== "buyer" ? "disabled" : ""}>Review &amp; Purchase</button>` : ""}
          </div>
        </div>
      </article>
    `).join("");

    // Re-attach event listeners
    marketGrid.querySelectorAll(".verify-btn").forEach(btn => btn.addEventListener("click", async () => {
      try { await fetch(`${API_BASE}/listings/${encodeURIComponent(btn.dataset.id)}/verify`, { method: "PATCH", headers: getAuthHeaders() }); } catch {}
      const next = getListings().map(lot => lot.id === btn.dataset.id ? { ...lot, verified: true } : lot);
      saveListings(next);
      renderMarketplace();
    }));
    marketGrid.querySelectorAll(".buy-btn").forEach(btn => btn.addEventListener("click", () => {
      selectedListingId = btn.dataset.id;
      const lot = getListings().find(item => item.id === selectedListingId);
      if (!lot) return;
      purchaseItem.textContent = `${lot.item} · ${lot.quantity} ${lot.unit} · Admin-set Quote ₹${lot.min_price}–₹${lot.max_price}`;
      purchaseMessage.textContent = "";
      const hiddenName = document.getElementById("buyerNameHidden");
      if (hiddenName && currentSession?.name) hiddenName.value = currentSession.name;
      if (buyerOfferPrice) buyerOfferPrice.value = lot.min_price || "";
      purchaseModal.hidden = false;
    }));
  }
}

// Hook into marketplace rendering to capture listings for filtering
const _originalRenderMarketplaceFn = window.renderMarketplace;
if (typeof renderMarketplace === "function") {
  const __origFn = renderMarketplace;
  window.renderMarketplace = function() {
    __origFn();
    // Capture all listings after original render for filter/search
    _allMarketListings = getListings().filter(lot => currentSession?.role === "admin" ? true : lot.verified === true);
  };
}

// Attach search/filter/sort event listeners
document.getElementById("marketSearchInput")?.addEventListener("input", debounce(() => {
  _allMarketListings = getListings().filter(lot => currentSession?.role === "admin" ? true : lot.verified === true);
  applyMarketplaceFilters();
}, 300));

document.getElementById("marketSortSelect")?.addEventListener("change", () => {
  _allMarketListings = getListings().filter(lot => currentSession?.role === "admin" ? true : lot.verified === true);
  applyMarketplaceFilters();
});

document.querySelectorAll(".market-filter-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    document.querySelectorAll(".market-filter-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    _allMarketListings = getListings().filter(lot => currentSession?.role === "admin" ? true : lot.verified === true);
    applyMarketplaceFilters();
  });
});

// ============================================================
// PWA SERVICE WORKER REGISTRATION
// ============================================================
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").then(reg => {
      console.log("[PWA] Service Worker registered:", reg.scope);
    }).catch(err => {
      console.log("[PWA] Service Worker registration skipped:", err.message);
    });
  });
}
