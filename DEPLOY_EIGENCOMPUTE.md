# 🚀 Deploy Lintora to EigenCompute

Deploy your confidential smart contract auditor to Intel TDX TEE using EigenCompute.

## Prerequisites

1. **Node.js** installed
2. **Docker** installed and running
3. **Groq API Key** for AI analysis
4. **ETH** for deployment (Sepolia testnet or mainnet)

---

## Step 1: Install EigenCloud CLI

```bash
npm install -g @layr-labs/ecloud-cli
```

Verify installation:
```bash
ecloud version
```

---

## Step 2: Authenticate

### Option A: Generate New Key (Recommended for first time)
```bash
ecloud auth generate --store
```

### Option B: Use Existing Key
```bash
ecloud auth login
```

Check your wallet address:
```bash
ecloud auth whoami
```

---

## Step 3: Get Testnet Funds (for Sepolia)

If deploying to Sepolia testnet:

1. Set environment to Sepolia:
   ```bash
   ecloud compute env set sepolia
   ```

2. Get testnet ETH from:
   - [Google Cloud Faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
   - [Alchemy Faucet](https://sepoliafaucet.com/)

---

## Step 4: Login to Docker

```bash
docker login
```

---

## Step 5: Subscribe to EigenCompute

```bash
ecloud billing subscribe
```

Complete payment in the portal ($100 free credit available).

---

## Step 6: Configure Environment Variables

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Required - Your Groq API key for AI analysis
GROQ_API_KEY=your_groq_api_key_here

# Optional - Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1
MAX_UPLOAD_SIZE_BYTES=52428800

# Public variables (visible to users)
APP_NAME_PUBLIC=Lintora
VERSION_PUBLIC=1.0.0
```

---

## Step 7: Deploy to TEE

From the Lintora project directory:

```bash
ecloud compute app deploy
```

When prompted:
- Select **"Build and deploy from Dockerfile"**

The CLI will:
1. Build Docker image targeting `linux/amd64`
2. Push image to your Docker registry
3. Deploy to Intel TDX TEE instance
4. Return your app ID and instance IP

---

## Step 8: View Your Application

```bash
ecloud compute app info
```

This shows:
- App ID
- Instance IP
- Status
- Exposed ports

---

## Step 9: Test Your Deployment

```bash
# Health check
curl http://<your-instance-ip>:8000/health

# Test audit endpoint
curl -X POST http://<your-instance-ip>:8000/audit \
  -F "file=@example.zip" \
  -F "project_name=test"
```

---

## Step 10: Deploy Frontend (Optional)

### Option A: Deploy to Vercel/Netlify

1. Update frontend environment:
   ```bash
   cd frontend
   echo "VITE_API_URL=http://<your-instance-ip>:8000" > .env.production
   npm run build
   ```

2. Deploy `dist/` folder to Vercel/Netlify

### Option B: Serve from Same Instance

The backend already serves the API. You can:
- Host frontend separately
- Or modify Dockerfile to serve static files

---

## Useful Commands

```bash
# View app logs
ecloud compute app logs

# Check app status
ecloud compute app info

# List all apps
ecloud compute app list

# Check billing status
ecloud billing status

# Check authentication
ecloud auth whoami
```

---

## Troubleshooting

### Docker Build Fails
Ensure Dockerfile has correct platform:
```dockerfile
FROM --platform=linux/amd64 python:3.12-slim-bookworm
```

### Deployment Transaction Fails
Check ETH balance:
```bash
ecloud auth whoami
```

### Image Push Fails
Re-login to Docker:
```bash
docker login
```

### App Not Starting
Check logs:
```bash
ecloud compute app logs
```

Common issues:
- Missing environment variables
- Port binding issues (must bind to 0.0.0.0)
- Application crashes

---

## Security Features in TEE

✅ **Code Isolation** - Analysis runs in Intel TDX enclave  
✅ **Memory Encryption** - All data encrypted in TEE  
✅ **Attestation** - Cryptographic proof of execution  
✅ **Secure Signing** - Ed25519 keys generated in TEE  
✅ **No Source Leakage** - Source code never leaves TEE  

---

## Support

- [EigenCompute Discord](https://discord.gg/eigenlayer)
- [EigenCompute Docs](https://docs.eigenlayer.xyz)

---

**Your Lintora app is now running in a confidential computing environment!** 🔐
