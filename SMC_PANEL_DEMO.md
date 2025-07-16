# SMC Panel Component Documentation

## 🎯 Overview
SMC Panel adalah komponen React untuk menampilkan analisis Smart Money Concept (SMC) pada dashboard trading crypto. Komponen ini menampilkan informasi struktur market seperti BOS, CHoCH, Order Block, dan Fair Value Gap dengan UI yang modern dan informatif.

## 📦 Installation & Integration

### 1. Standalone Component File (Recommended)
Simpan komponen di `src/components/SMCPanel.jsx` dan import ke dashboard:

```jsx
import SMCPanel from './components/SMCPanel';
```

### 2. Inline Integration (Current Implementation)
Komponen sudah terintegrasi langsung di `templates/react_dashboard.html`

## 🔧 Props & Data Structure

### Props
- `data` (object): Object berisi data SMC analysis

### Data Structure
```javascript
{
  timeframe: '1H',          // Timeframe analisis
  bos: true,                // Break of Structure (boolean)
  choch: true,              // Change of Character (boolean)
  ob: 147.20,               // Order Block price level (number/null)
  fvgZone: '148.50 - 149.10', // Fair Value Gap zone (string/null)
  liquiditySweep: false,    // Liquidity sweep detection (boolean)
  status: 'valid'           // Status validitas ('valid', 'invalid', 'pending')
}
```

## 💻 Usage Example

### Basic Usage
```jsx
const [smcData, setSmcData] = useState({
  timeframe: '1H',
  bos: true,
  choch: true,
  ob: 147.20,
  fvgZone: '148.50 - 149.10',
  liquiditySweep: false,
  status: 'valid'
});

return <SMCPanel data={smcData} />;
```

### Dynamic Update Example
```jsx
// Update saat menerima data dari API
useEffect(() => {
  fetchSMCAnalysis(selectedPair, selectedTimeframe)
    .then(data => {
      setSmcData({
        timeframe: selectedTimeframe,
        bos: data.breakOfStructure,
        choch: data.changeOfCharacter,
        ob: data.orderBlockLevel,
        fvgZone: data.fairValueGap,
        liquiditySweep: data.liquiditySweepDetected,
        status: data.isValid ? 'valid' : 'invalid'
      });
    });
}, [selectedPair, selectedTimeframe]);
```

## 🎨 Component Features

### 1. Status Indicators
- **Valid**: Green indicator - struktur market valid
- **Invalid**: Red indicator - struktur market invalid
- **Pending**: Yellow indicator - analisis sedang berlangsung

### 2. SMC Indicators
- **BOS (Break of Structure)**: Mendeteksi apakah struktur market telah broken
- **CHoCH (Change of Character)**: Mendeteksi perubahan karakter trend
- **Order Block**: Level harga institusional yang signifikan
- **FVG Zone**: Fair Value Gap yang bisa menjadi target price

### 3. Visual Feedback
- Active indicators ditampilkan dengan highlight biru
- Inactive indicators ditampilkan dengan warna gray
- Color-coded zones untuk different market conditions

## 🔄 Integration dengan Backend API

### Example API Endpoint
```javascript
// GET /api/smc-analysis/{pair}/{timeframe}
{
  "success": true,
  "data": {
    "timeframe": "1H",
    "breakOfStructure": true,
    "changeOfCharacter": false,
    "orderBlockLevel": 147.20,
    "fairValueGap": "148.50 - 149.10",
    "liquiditySweepDetected": false,
    "validityStatus": "valid",
    "timestamp": "2025-01-16T04:30:00Z"
  }
}
```

### Frontend Integration
```jsx
const fetchSMCData = async () => {
  try {
    const response = await fetch(`/api/smc-analysis/${selectedPair}/${selectedTimeframe}`);
    const result = await response.json();
    
    if (result.success) {
      setSmcData({
        timeframe: result.data.timeframe,
        bos: result.data.breakOfStructure,
        choch: result.data.changeOfCharacter,
        ob: result.data.orderBlockLevel,
        fvgZone: result.data.fairValueGap,
        liquiditySweep: result.data.liquiditySweepDetected,
        status: result.data.validityStatus
      });
    }
  } catch (error) {
    console.error('Error fetching SMC data:', error);
  }
};
```

## 🎯 Current Implementation
Komponen SMC Panel sudah terintegrasi di dashboard React dengan:
- Position: Bottom left panel (menggantikan Order Flow panel)
- State management: Menggunakan React hooks
- Dummy data untuk demo
- Responsive design dengan Tailwind CSS

## 🚀 Next Steps
1. Connect ke backend API untuk real-time SMC analysis
2. Add WebSocket support untuk live updates
3. Implement interactive features (click pada zones untuk detail)
4. Add historical SMC pattern tracking
5. Export/import SMC analysis configuration

## 📸 Visual Preview
Component menampilkan:
- Header dengan timeframe dan status
- 4 indicator boxes (BOS, CHoCH, Liquidity Sweep, Order Block)
- Color-coded zones untuk FVG
- Responsive grid layout
- Dark theme yang konsisten dengan dashboard