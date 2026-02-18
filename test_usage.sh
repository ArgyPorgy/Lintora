#!/bin/bash
# Quick test script for Private Security Agent

echo "🔒 Private Security Agent — Quick Test"
echo "======================================"
echo

# Create a test contract with a real vulnerability
mkdir -p test-contract
cat > test-contract/Vault.sol << 'SOL'
pragma solidity ^0.8.0;

contract Vault {
    address public owner;
    mapping(address => uint256) public balances;
    
    constructor() {
        owner = msg.sender;
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // REENTRANCY VULNERABILITY
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent);
        balances[msg.sender] -= amount;  // State updated AFTER external call
    }
    
    // RUG-PULL RISK
    function emergencyWithdraw() public {
        require(msg.sender == owner);
        payable(owner).transfer(address(this).balance);
    }
}
SOL

echo "📦 Creating test contract ZIP..."
cd test-contract && zip -r ../test-vault.zip . > /dev/null 2>&1 && cd ..
echo "✓ Created test-vault.zip"
echo

echo "🔍 Submitting for audit..."
RESPONSE=$(curl -s -X POST http://localhost:8000/audit \
  -F "file=@test-vault.zip" \
  -F "project_name=TestVault")

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create job"
    echo "$RESPONSE"
    exit 1
fi

echo "✓ Job created: $JOB_ID"
echo

echo "⏳ Waiting for analysis (this may take 2-5 minutes)..."
echo "   (Mythril symbolic execution is CPU-intensive)"
echo

for i in {1..60}; do
    STATUS=$(curl -s http://localhost:8000/audit/$JOB_ID | \
      python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
    
    if [ "$STATUS" = "completed" ]; then
        echo "✓ Analysis complete!"
        echo
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Analysis failed"
        exit 1
    fi
    
    if [ $((i % 10)) -eq 0 ]; then
        echo "   Still processing... ($i seconds)"
    fi
    sleep 2
done

echo "📊 Results:"
curl -s http://localhost:8000/audit/$JOB_ID | python3 -c "
import sys, json
r = json.load(sys.stdin)
if r['status'] == 'completed':
    report = r['report']
    print(f\"  Project: {report['project_name']}\")
    print(f\"  Risk Level: {report['risk_level']}\")
    print(f\"  Total Findings: {report['summary']['total_findings']}\")
    print(f\"    Critical: {report['summary']['critical']}\")
    print(f\"    High: {report['summary']['high']}\")
    print(f\"    Medium: {report['summary']['medium']}\")
    print(f\"  Analyzers: {', '.join(report['summary']['analyzers_used'])}\")
    print()
    print(f\"  📄 View full report: http://localhost:8000/report/{r['job_id']}\")
    print()
    print(\"  Top findings:\")
    for f in report['findings'][:5]:
        src = f['source'].upper()[:8]
        print(f\"    [{f['severity'].upper():8s}] [{src:8s}] {f['file_path']}:{f.get('line_number', '?')} — {f['description'][:60]}\")
else:
    print(f\"  Status: {r['status']}\")
    if r.get('error'):
        print(f\"  Error: {r['error']}\")
"

echo
echo "🌐 Opening report in browser..."
if command -v open > /dev/null; then
    open "http://localhost:8000/report/$JOB_ID"
fi

echo
echo "======================================"
echo "✅ Test complete!"
echo
echo "Next: Upload your own contracts with:"
echo "  curl -X POST http://localhost:8000/audit \\"
echo "    -F \"file=@your-contracts.zip\" \\"
echo "    -F \"project_name=YourProject\""
